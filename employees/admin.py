from django.contrib import admin
from .models import Employee, Skill, EmployeeProfile


class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    can_delete = False
    verbose_name_plural = 'Profile'


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

    inlines = [EmployeeProfileInline]
    filter_horizontal = ('skills',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('employee', 'birth_date', 'emergency_contact')
    search_fields = ('employee__first_name', 'employee__employee_id')

