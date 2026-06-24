from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email.split('@')[0])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ADMIN = 'ADMIN'
    HR = 'HR'
    MANAGER = 'MANAGER'
    EMPLOYEE = 'EMPLOYEE'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (HR, 'HR'),
        (MANAGER, 'Manager'),
        (EMPLOYEE, 'Employee'),
    ]

    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    employee_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=EMPLOYEE)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['employee_id']

    def save(self, *args, **kwargs):
        if not self.username and self.email:
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            # We bypass model-level query check during initial DB setup if User doesn't exist
            try:
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
            except Exception:
                pass
            self.username = username

        # Synchronize Django standard staff/superuser flags based on user role
        if self.role == self.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role in [self.HR, self.MANAGER]:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False
            
        super().save(*args, **kwargs)

        try:
            self.assign_role_permissions()
        except Exception:
            # Avoid breaking migrations before tables exist
            pass

    def assign_role_permissions(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from employees.models import Employee
        from departments.models import Department

        # Create/Get groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        hr_group, _ = Group.objects.get_or_create(name='HR')
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        employee_group, _ = Group.objects.get_or_create(name='Employee')

        # Clean existing groups for this user
        self.groups.clear()

        # Get content types
        employee_ct = ContentType.objects.get_for_model(Employee)
        department_ct = ContentType.objects.get_for_model(Department)

        # Retrieve permissions
        add_emp = Permission.objects.filter(content_type=employee_ct, codename='add_employee').first()
        change_emp = Permission.objects.filter(content_type=employee_ct, codename='change_employee').first()
        delete_emp = Permission.objects.filter(content_type=employee_ct, codename='delete_employee').first()
        view_emp = Permission.objects.filter(content_type=employee_ct, codename='view_employee').first()

        add_dept = Permission.objects.filter(content_type=department_ct, codename='add_department').first()
        change_dept = Permission.objects.filter(content_type=department_ct, codename='change_department').first()
        delete_dept = Permission.objects.filter(content_type=department_ct, codename='delete_department').first()
        view_dept = Permission.objects.filter(content_type=department_ct, codename='view_department').first()

        # Populate permissions in groups
        # HR Group: All permissions
        for perm in [add_emp, change_emp, delete_emp, view_emp, add_dept, change_dept, delete_dept, view_dept]:
            if perm:
                hr_group.permissions.add(perm)

        # Manager Group: Change employee, view employee, view department
        for perm in [change_emp, view_emp, view_dept]:
            if perm:
                manager_group.permissions.add(perm)

        # Employee Group: View employee
        for perm in [view_emp]:
            if perm:
                employee_group.permissions.add(perm)

        # Assign user to correct group
        if self.role == self.ADMIN:
            self.groups.add(admin_group)
        elif self.role == self.HR:
            self.groups.add(hr_group)
        elif self.role == self.MANAGER:
            self.groups.add(manager_group)
        elif self.role == self.EMPLOYEE:
            self.groups.add(employee_group)

    def __str__(self):
        return f"{self.email} ({self.role})"
