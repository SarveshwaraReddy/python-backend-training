from rest_framework import serializers
from departments.models import Department
from employees.models import Employee

class NestedEmployeeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:  # type: ignore
        model = Employee
        fields = ['id', 'name']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class DepartmentSerializerV2(serializers.ModelSerializer):
    employee_count = serializers.IntegerField(read_only=True, default=0)
    average_salary = serializers.FloatField(read_only=True, default=0.0)
    highest_salary = serializers.FloatField(read_only=True, default=0.0)
    lowest_salary = serializers.FloatField(read_only=True, default=0.0)
    employees = NestedEmployeeSerializer(source='employee_set', many=True, read_only=True)

    class Meta:  # type: ignore
        model = Department
        fields = [
            'id', 'name', 'description', 'employee_count', 'average_salary',
            'highest_salary', 'lowest_salary', 'employees'
        ]

