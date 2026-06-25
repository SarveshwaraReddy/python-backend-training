from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.core.cache import cache

from api.services.employee import EmployeeService
from api.serializers.v1.employee import EmployeeSerializer
from api.permissions import EmployeeRBACPermission
from api.filters import EmployeeFilter
from api.pagination import StandardResultsSetPagination
from api.responses.custom_response import SuccessResponse

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [EmployeeRBACPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']
    ordering_fields = ['salary', 'joining_date']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmployeeService()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return self.service.repository.model.objects.none()
        
        # Admins and HR see all employees
        if user.role in ['ADMIN', 'HR']:
            return self.service.get_all_employees().order_by('employee_id')
        
        # Managers and Employees see only their own records
        return self.service.repository.model.objects.filter(employee_id=user.employee_id).order_by('employee_id')

    def list(self, request, *args, **kwargs):
        user = request.user
        query_params = request.query_params.urlencode()
        cache_key = f"v1_employees_list_{user.id}_{user.role}_{query_params}"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return SuccessResponse(data=cached_data, message="Employees fetched successfully (cached)")

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
            cache.set(cache_key, paginated_data, 60 * 5)
            return SuccessResponse(data=paginated_data, message="Employees fetched successfully")

        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, 60 * 5)
        return SuccessResponse(data=serializer.data, message="Employees fetched successfully")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return SuccessResponse(data=serializer.data, message="Employee details fetched successfully")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create_employee(serializer.validated_data)
        cache.clear()
        
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="Employee Created Successfully", status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update_employee(instance.id, serializer.validated_data)
        cache.clear()
        
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="Employee Updated Successfully")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_employee(instance.id)
        cache.clear()
        return SuccessResponse(message="Employee Deleted Successfully")
