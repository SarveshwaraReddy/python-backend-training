from rest_framework import serializers
from employees.models import Employee, Skill, EmployeeProfile
from api.serializers.v1.department import DepartmentSerializer

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'description']
        extra_kwargs = {
            'name': {'validators': []}  # Bypass unique validator for get_or_create lookup
        }


class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = ['id', 'address', 'birth_date', 'emergency_contact']


class EmployeeSerializerV2(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False)
    profile = EmployeeProfileSerializer(required=False, allow_null=True)
    skills = SkillSerializer(many=True, required=False)
    
    class Meta:  # type: ignore
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'email', 'phone',
            'designation', 'department', 'department_id', 'status', 'salary',
            'joining_date', 'profile_image', 'profile', 'skills'
        ]

    def create(self, validated_data):
        dept_id = validated_data.pop('department_id', None)
        profile_data = validated_data.pop('profile', None)
        skills_data = validated_data.pop('skills', [])

        if dept_id:
            validated_data['department_id'] = dept_id

        employee = super().create(validated_data)

        if profile_data:
            EmployeeProfile.objects.create(employee=employee, **profile_data)

        if skills_data:
            skills_objs = []
            for skill_item in skills_data:
                name = skill_item.get('name')
                if name:
                    skill_obj, _ = Skill.objects.get_or_create(
                        name=name,
                        defaults={'description': skill_item.get('description')}
                    )
                    skills_objs.append(skill_obj)
            employee.skills.set(skills_objs)

        return employee

    def update(self, instance, validated_data):
        dept_id = validated_data.pop('department_id', None)
        profile_data = validated_data.pop('profile', None)
        skills_data = validated_data.pop('skills', None)

        if dept_id:
            instance.department_id = dept_id

        employee = super().update(instance, validated_data)

        if profile_data is not None:
            if profile_data:
                EmployeeProfile.objects.update_or_create(
                    employee=employee,
                    defaults=profile_data
                )
            else:
                EmployeeProfile.objects.filter(employee=employee).delete()

        if skills_data is not None:
            skills_objs = []
            for skill_item in skills_data:
                name = skill_item.get('name')
                if name:
                    skill_obj, _ = Skill.objects.get_or_create(
                        name=name,
                        defaults={'description': skill_item.get('description')}
                    )
                    skills_objs.append(skill_obj)
            employee.skills.set(skills_objs)

        return employee

