from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import AccessMixin
from functools import wraps

def role_required(allowed_roles):
    """
    Decorator for views that checks if the user has one of the allowed roles.
    Bypasses checking for superusers.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                # We can store next page parameter
                return redirect(f"/accounts/login/?next={request.path}")
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "You do not have permission to access this page.")
            return redirect('accounts:dashboard')
        return _wrapped_view
    return decorator

def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)

def hr_required(view_func):
    return role_required(['ADMIN', 'HR'])(view_func)

def manager_required(view_func):
    return role_required(['ADMIN', 'HR', 'MANAGER'])(view_func)

class RoleRequiredMixin(AccessMixin):
    """
    CBV mixin that checks if the user has one of the allowed roles.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role in self.allowed_roles or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, "You do not have permission to access this page.")
        return redirect('accounts:dashboard')
