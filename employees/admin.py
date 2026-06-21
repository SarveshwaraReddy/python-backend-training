from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id',
        'first_name',
        'email',
        'salary',
        'department',
    )

    search_fields = (
        'employee_id',
        'first_name',
        'email',
    )

    list_filter = (
        'department',
    )
