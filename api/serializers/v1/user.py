from rest_framework import serializers
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'employee_id', 'phone', 'role', 'profile_image', 'password']
        read_only_fields = ['username']
