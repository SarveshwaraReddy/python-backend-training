from django.db import models
from typing import TYPE_CHECKING


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class EmployeeQuerySet(models.QuerySet):
    def active(self) -> 'EmployeeQuerySet':
        return self.filter(status='active')

    def inactive(self) -> 'EmployeeQuerySet':
        return self.filter(status='inactive')

    def engineering(self) -> 'EmployeeQuerySet':
        return self.filter(department__name='Engineering')

    def high_salary(self) -> 'EmployeeQuerySet':
        return self.filter(salary__gt=50000)


class EmployeeManager(models.Manager):
    def get_queryset(self) -> 'EmployeeQuerySet':
        return EmployeeQuerySet(self.model, using=self._db)

    def active(self) -> 'EmployeeQuerySet':
        return self.get_queryset().active()

    def inactive(self) -> 'EmployeeQuerySet':
        return self.get_queryset().inactive()

    def engineering(self) -> 'EmployeeQuerySet':
        return self.get_queryset().engineering()

    def high_salary(self) -> 'EmployeeQuerySet':
        return self.get_queryset().high_salary()

    def active_employees(self) -> 'EmployeeQuerySet':
        return self.active()

    def inactive_employees(self) -> 'EmployeeQuerySet':
        return self.inactive()

    def highest_salary(self) -> 'Employee | None':
        return self.order_by('-salary').first()

    def new_joiners(self) -> 'EmployeeQuerySet':
        import datetime
        today = datetime.date.today()
        return self.get_queryset().filter(joining_date__year=today.year, joining_date__month=today.month)


class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joining_date = models.DateField()
    designation = models.CharField(max_length=100)
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    profile_image = models.ImageField(upload_to='employees/', null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name='employees', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EmployeeManager()

    if TYPE_CHECKING:
        from typing import ClassVar
        objects: ClassVar[EmployeeManager]
        profile: 'EmployeeProfile'



    def clean(self):
        from django.core.exceptions import ValidationError
        import datetime
        super().clean()
        if self.salary is not None and self.salary < 10000:
            raise ValidationError({'salary': 'Salary must be at least 10000.'})
        if self.joining_date and self.joining_date > datetime.date.today():
            raise ValidationError({'joining_date': 'Joining date cannot be in the future.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(salary__gte=10000),
                name='salary_check'
            )
        ]
        indexes = [
            models.Index(fields=['joining_date'], name='idx_employee_joining_date'),
            models.Index(fields=['salary'], name='idx_employee_salary'),
            models.Index(fields=['department', 'salary'], name='idx_department_salary'),
        ]

    def __str__(self):
        return self.first_name


class EmployeeProfile(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.employee.first_name}'s Profile"

