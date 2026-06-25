from rest_framework import serializers
from employees.models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'email',
            'phone', 'designation', 'department', 'department_name', 'status'
        ]
