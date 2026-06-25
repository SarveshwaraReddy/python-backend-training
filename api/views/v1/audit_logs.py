from rest_framework import viewsets, permissions, serializers
from audit_logs.models import AuditLog
from api.responses.custom_response import SuccessResponse

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_email', 'action', 'module', 'timestamp', 'ip_address', 'details']

class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        return AuditLog.objects.all().order_by('-timestamp')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return SuccessResponse(data=self.get_paginated_response(serializer.data).data, message="Audit logs retrieved successfully")

        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, message="Audit logs retrieved successfully")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return SuccessResponse(data=serializer.data, message="Audit log detail retrieved successfully")
