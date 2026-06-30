from rest_framework import permissions

class EmployeeRBACPermission(permissions.BasePermission):
    """
    Role-Based Access Control for Employee APIs:
    - ADMIN: Full CRUD access.
    - HR: Create, Read, and Update access (no DELETE).
    - EMPLOYEE / MANAGER: Read access to their own record only.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        # Admin has full access
        if request.user.role == 'ADMIN':
            return True
            
        # HR has access to all actions except DELETE
        if request.user.role == 'HR':
            if request.method == 'DELETE':
                return False
            return True
            
        # Employees and Managers can only perform read actions (GET)
        if request.user.role in ['EMPLOYEE', 'MANAGER']:
            if request.method in permissions.SAFE_METHODS:
                return True
            return False
            
        return False

    def has_object_permission(self, request, view, obj):
        # Admin and HR can access any employee object
        if request.user.role in ['ADMIN', 'HR']:
            return True
            
        # Employees and Managers can only access their own profile
        if request.user.role in ['EMPLOYEE', 'MANAGER']:
            return obj.employee_id == request.user.employee_id
            
        return False


class DepartmentRBACPermission(permissions.BasePermission):
    """
    Role-Based Access Control for Department APIs:
    - ADMIN & HR: Full CRUD access.
    - Others: Read-only access.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        if request.user.role in ['ADMIN', 'HR']:
            return True
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return False


class UserRBACPermission(permissions.BasePermission):
    """
    Role-Based Access Control for User APIs:
    - ADMIN: Full CRUD access.
    - HR: Read access to all users.
    - Any authenticated user: Retrieve and Update their own user profile.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        if request.user.role == 'ADMIN':
            return True
            
        # HR can view lists or details
        if request.user.role == 'HR':
            if request.method in permissions.SAFE_METHODS:
                return True
                
        # Employees / Managers can perform actions on their own record (checked in has_object_permission)
        return True

    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == 'ADMIN':
            return True
            
        # HR can retrieve other users but not modify or delete
        if request.user.role == 'HR':
            if request.method in permissions.SAFE_METHODS:
                return True
                
        # Users can retrieve and update their own User instance
        return obj == request.user


class PayrollRBACPermission(permissions.BasePermission):
    """
    Role-Based Access Control for Payroll APIs:
    - ADMIN: Full CRUD access.
    - HR: Create, Read, and Update access (no DELETE).
    - EMPLOYEE / MANAGER: Read access to their own records only.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        if request.user.role == 'ADMIN':
            return True
            
        if request.user.role == 'HR':
            if request.method == 'DELETE':
                return False
            return True
            
        if request.user.role in ['EMPLOYEE', 'MANAGER']:
            if request.method in permissions.SAFE_METHODS:
                return True
            return False
            
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['ADMIN', 'HR']:
            return True
            
        if request.user.role in ['EMPLOYEE', 'MANAGER']:
            return obj.employee.employee_id == request.user.employee_id
            
        return False


class AttendanceRBACPermission(permissions.BasePermission):
    """
    Role-Based Access Control for Attendance APIs:
    - ADMIN & HR: Full CRUD access.
    - MANAGER: Full CRUD access (to manage team attendance).
    - EMPLOYEE: Read-only access to their own attendance.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        if request.user.role in ['ADMIN', 'HR', 'MANAGER']:
            return True
            
        if request.user.role == 'EMPLOYEE':
            if request.method in permissions.SAFE_METHODS:
                return True
            return False
            
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['ADMIN', 'HR', 'MANAGER']:
            return True
            
        if request.user.role == 'EMPLOYEE':
            return obj.employee.employee_id == request.user.employee_id
            
        return False
