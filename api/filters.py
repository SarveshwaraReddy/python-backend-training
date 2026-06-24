import django_filters
from employees.models import Employee

class EmployeeFilter(django_filters.FilterSet):
    department_name = django_filters.CharFilter(field_name='department__name', lookup_expr='iexact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    designation = django_filters.CharFilter(field_name='designation', lookup_expr='icontains')

    class Meta:
        model = Employee
        fields = ['department', 'department_name', 'status', 'designation']
