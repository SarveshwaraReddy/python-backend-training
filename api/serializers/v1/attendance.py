from rest_framework import serializers
from attendance.models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_id_val = serializers.CharField(source='employee.employee_id', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_id_val', 'employee_name',
            'date', 'status', 'created_at', 'updated_at'
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
