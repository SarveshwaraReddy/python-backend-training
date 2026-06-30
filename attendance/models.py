from django.db import models
from employees.models import Employee

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['employee', 'date'], name='unique_employee_date')
        ]

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.date} - {self.status}"
