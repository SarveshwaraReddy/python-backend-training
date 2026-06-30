from rest_framework import viewsets, status
from django.core.cache import cache
from api.services.attendance import AttendanceService
from api.serializers.v1.attendance import AttendanceSerializer
from api.permissions import AttendanceRBACPermission
from api.pagination import StandardResultsSetPagination
from api.responses.custom_response import SuccessResponse

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [AttendanceRBACPermission]
    pagination_class = StandardResultsSetPagination

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = AttendanceService()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return self.service.repository.model.objects.none()

        if user.role in ['ADMIN', 'HR', 'MANAGER']:
            return self.service.get_all_attendances().order_by('-date')

        # Employees can only view their own attendance
        return self.service.repository.model.objects.select_related('employee').filter(
            employee__employee_id=user.employee_id
        ).order_by('-date')

    def list(self, request, *args, **kwargs):
        user = request.user
        query_params = request.query_params.urlencode()
        cache_key = f"v1_attendance_list_{user.id}_{user.role}_{query_params}"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return SuccessResponse(data=cached_data, message="Attendance records fetched successfully (cached)")

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
            cache.set(cache_key, paginated_data, 60 * 5)
            return SuccessResponse(data=paginated_data, message="Attendance records fetched successfully")

        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, 60 * 5)
        return SuccessResponse(data=serializer.data, message="Attendance records fetched successfully")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return SuccessResponse(data=serializer.data, message="Attendance details fetched successfully")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create_attendance(serializer.validated_data)
        cache.clear()
        
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="Attendance Created Successfully", status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update_attendance(instance.id, serializer.validated_data)
        cache.clear()
        
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="Attendance Updated Successfully")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_attendance(instance.id)
        cache.clear()
        return SuccessResponse(message="Attendance Deleted Successfully")
