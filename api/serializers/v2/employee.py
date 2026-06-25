from rest_framework import serializers
from employees.models import Employee
from api.serializers.v1.department import DepartmentSerializer

class EmployeeSerializerV2(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    # Writeable field if needed, but we read it as a full object and can set it by ID using another field
    department_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'email', 'phone',
            'designation', 'department', 'department_id', 'status', 'salary',
            'joining_date', 'profile_image'
        ]

    def create(self, validated_data):
        dept_id = validated_data.pop('department_id', None)
        if dept_id:
            validated_data['department_id'] = dept_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        dept_id = validated_data.pop('department_id', None)
        if dept_id:
            instance.department_id = dept_id
        return super().update(instance, validated_data)
