from django.db import models
from employees.models import Employee

class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    month = models.CharField(max_length=7)  # Format: YYYY-MM
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-month']
        constraints = [
            models.UniqueConstraint(fields=['employee', 'month'], name='unique_employee_month')
        ]

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.month} - {self.net_salary}"
