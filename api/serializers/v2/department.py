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
    employees = NestedEmployeeSerializer(source='employee_set', many=True, read_only=True)

    class Meta:  # type: ignore
        model = Department
        fields = ['id', 'name', 'description', 'employees']
