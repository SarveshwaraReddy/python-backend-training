from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Count
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView,
    PasswordChangeView
)
from django.urls import reverse_lazy
from datetime import date

from .models import User
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from employees.models import Employee
from departments.models import Department

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create user but do not activate yet (pending email verification)
            user = form.save(commit=False)
            user.is_active = False
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # 1. Sync or Create corresponding Employee record
            default_dept = Department.objects.first()
            if not default_dept:
                default_dept = Department.objects.create(
                    name="General", 
                    description="General Department"
                )
                
            employee, created = Employee.objects.get_or_create(
                employee_id=user.employee_id,
                defaults={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone': user.phone or '',
                    'salary': 10000.00,
                    'joining_date': date.today(),
                    'designation': user.role,
                    'department': default_dept,
                    'status': 'inactive', # Sync with user is_active status
                    'profile_image': user.profile_image
                }
            )
            if not created:
                employee.first_name = user.first_name
                employee.last_name = user.last_name
                employee.email = user.email
                employee.phone = user.phone or employee.phone
                if user.profile_image:
                    employee.profile_image = user.profile_image
                employee.status = 'inactive'
                employee.save()
                
            # 2. Email verification link generation
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = f"http://{current_site.domain}/accounts/verify-email/{uid}/{token}/"
            
            subject = "Activate Your Acme Corporation Account"
            message = f"Hello {user.first_name},\n\nThank you for registering. Please click the link below to verify your email address and activate your account:\n{verification_link}\n\nRegards,\nAcme Corporation HR Team"
            
            send_mail(
                subject,
                message,
                'noreply@acme.com',
                [user.email],
                fail_silently=False,
            )
            
            return render(request, 'accounts/verify_email_sent.html', {'email': user.email})
    else:
        form = UserRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})


def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        # Sync Employee record status
        employee = Employee.objects.filter(employee_id=user.employee_id).first()
        if employee:
            employee.status = 'active'
            employee.save()
            
        login(request, user)
        messages.success(request, "Your account has been successfully verified and logged in!")
        return redirect('accounts:dashboard')
    else:
        return render(request, 'accounts/verify_email_invalid.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name or user.email}!")
                    next_url = request.GET.get('next', '')
                    if next_url:
                        return redirect(next_url)
                    return redirect('accounts:dashboard')
                else:
                    messages.warning(request, "Your account is not active. Please complete email verification.")
                    return redirect('accounts:login')
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = UserLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    role = request.user.role
    context = {'role': role}
    
    if role == 'ADMIN' or request.user.is_superuser:
        context['total_employees'] = Employee.objects.count()
        context['total_departments'] = Department.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['inactive_users'] = User.objects.filter(is_active=False).count()
        
        # User statistics
        role_counts = User.objects.values('role').annotate(count=Count('id'))
        context['role_counts'] = {item['role']: item['count'] for item in role_counts}
        
    elif role == 'HR':
        context['total_employees'] = Employee.objects.count()
        context['active_employees'] = Employee.objects.filter(status='active').count()
        context['recent_employees'] = Employee.objects.order_by('-created_at')[:5]
        
    elif role == 'MANAGER':
        context['total_employees'] = Employee.objects.count()
        context['total_departments'] = Department.objects.count()
        context['departments'] = Department.objects.all()
        context['recent_employees'] = Employee.objects.order_by('-created_at')[:5]
        
    else: # EMPLOYEE
        employee = Employee.objects.filter(employee_id=request.user.employee_id).first()
        context['employee'] = employee
        
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            
            # Sync details to Employee record
            employee = Employee.objects.filter(employee_id=request.user.employee_id).first()
            if employee:
                employee.first_name = request.user.first_name
                employee.last_name = request.user.last_name
                employee.phone = request.user.phone or employee.phone
                if request.user.profile_image:
                    employee.profile_image = request.user.profile_image
                employee.save()
                
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
        
    return render(request, 'accounts/profile.html', {'form': form})


# Password management CBVs
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed successfully!")
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
