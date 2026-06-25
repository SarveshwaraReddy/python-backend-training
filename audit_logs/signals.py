from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from employees.models import Employee
from audit_logs.models import AuditLog
from company_portal.middleware import get_current_user, get_current_ip

@receiver(post_save, sender=Employee)
def log_employee_save(sender, instance, created, **kwargs):
    action = "CREATE" if created else "UPDATE"
    user = get_current_user()
    ip = get_current_ip()
    
    details = f"Employee ID: {instance.employee_id}, Name: {instance.first_name} {instance.last_name}, Designation: {instance.designation}"
    
    AuditLog.objects.create(
        user=user,
        action=action,
        module="Employees",
        ip_address=ip,
        details=details
    )

@receiver(post_delete, sender=Employee)
def log_employee_delete(sender, instance, **kwargs):
    user = get_current_user()
    ip = get_current_ip()
    
    details = f"Deleted Employee ID: {instance.employee_id}, Name: {instance.first_name} {instance.last_name}"
    
    AuditLog.objects.create(
        user=user,
        action="DELETE",
        module="Employees",
        ip_address=ip,
        details=details
    )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')
    
    AuditLog.objects.create(
        user=user,
        action="LOGIN",
        module="Auth",
        ip_address=ip,
        details=f"User {user.email} logged in successfully."
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    ip = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')
        
    AuditLog.objects.create(
        user=user,
        action="LOGOUT",
        module="Auth",
        ip_address=ip,
        details=f"User {user.email if user else 'Unknown'} logged out."
    )
