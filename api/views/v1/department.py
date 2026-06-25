from rest_framework import viewsets, status
from django.core.cache import cache

from api.services.department import DepartmentService
from api.serializers.v1.department import DepartmentSerializer
from api.permissions import DepartmentRBACPermission
from api.pagination import StandardResultsSetPagination
from api.responses.custom_response import SuccessResponse

class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [DepartmentRBACPermission]
    pagination_class = StandardResultsSetPagination

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DepartmentService()

    def get_queryset(self):
        return self.service.get_all_departments().order_by('name')

    def list(self, request, *args, **kwargs):
        user = request.user
        query_params = request.query_params.urlencode()
        cache_key = f"v1_departments_list_{user.id}_{user.role}_{query_params}"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return SuccessResponse(data=cached_data, message="Departments fetched successfully (cached)")

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
            cache.set(cache_key, paginated_data, 60 * 5)
            return SuccessResponse(data=paginated_data, message="Departments fetched successfully")

        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, 60 * 5)
        return SuccessResponse(data=serializer.data, message="Departments fetched successfully")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return SuccessResponse(data=serializer.data, message="Department details fetched successfully")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create_department(serializer.validated_data)
        cache.clear()
        
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="Department Created Successfully", status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update_department(instance.id, serializer.validated_data)
        cache.clear()
        
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="Department Updated Successfully")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_department(instance.id)
        cache.clear()
        return SuccessResponse(message="Department Deleted Successfully")
