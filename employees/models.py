from django.db import models


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
