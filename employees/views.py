from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView, RedirectView
from django.db.models import Q

from departments.models import Department
from .models import Employee
from .forms import EmployeeForm
from accounts.decorators import RoleRequiredMixin


class HomeView(TemplateView):
    template_name = 'employees/home.html'

class AboutView(TemplateView):
    template_name = 'employees/about.html'

class ContactView(TemplateView):
    template_name = 'employees/contact.html'
    
class LoginView(RedirectView):
    pattern_name = 'accounts:login'
    permanent = True
    
class EmployeeListView(RoleRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10
    allowed_roles = ['ADMIN', 'HR', 'MANAGER']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        search = self.request.GET.get('search', '')
        department_id = self.request.GET.get('department', '')
        status = self.request.GET.get('status', '')
        designation = self.request.GET.get('designation', '')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )

        if department_id:
            queryset = queryset.filter(department_id=department_id)
            
        if status:
            queryset = queryset.filter(status=status)
            
        if designation:
            queryset = queryset.filter(designation__icontains=designation)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        # Preserve query parameters for pagination
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['query_params'] = query_params.urlencode()
        
        # Current filter states
        context['search'] = self.request.GET.get('search', '')
        context['selected_department'] = self.request.GET.get('department', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_designation'] = self.request.GET.get('designation', '')
        return context


class EmployeeDetailView(RoleRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'
    allowed_roles = ['ADMIN', 'HR', 'MANAGER', 'EMPLOYEE']

    def get(self, request, *args, **kwargs):
        employee = self.get_object()
        # Restrict standard employees to only view their own detailed record
        if request.user.role == 'EMPLOYEE' and request.user.employee_id != employee.employee_id:
            messages.error(request, "You are only allowed to view your own profile.")
            return redirect('accounts:dashboard')
        return super().get(request, *args, **kwargs)


class EmployeeCreateView(RoleRequiredMixin, SuccessMessageMixin, CreateView):
    model = Employee
    allowed_roles = ['ADMIN', 'HR']
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    success_message = "Employee Created Successfully"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add Employee'
        return context
        
    def form_invalid(self, form):
        messages.error(self.request, "Validation Failed. Please correct the errors below.")
        return super().form_invalid(form)


class EmployeeUpdateView(RoleRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Employee
    allowed_roles = ['ADMIN', 'HR']
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    success_message = "Employee Updated Successfully"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Update Employee'
        return context
        
    def form_invalid(self, form):
        messages.error(self.request, "Validation Failed. Please correct the errors below.")
        return super().form_invalid(form)


class EmployeeDeleteView(RoleRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Employee
    allowed_roles = ['ADMIN', 'HR']
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')
    success_message = "Employee Deleted Successfully"
