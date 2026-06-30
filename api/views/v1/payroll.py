from typing import cast
from rest_framework import viewsets, status
from django.core.cache import cache
from accounts.models import User
from api.services.payroll import PayrollService
from api.serializers.v1.payroll import PayrollSerializer
from api.permissions import PayrollRBACPermission
from api.pagination import StandardResultsSetPagination
from api.responses.custom_response import SuccessResponse

class PayrollViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollSerializer
    permission_classes = [PayrollRBACPermission]
    pagination_class = StandardResultsSetPagination

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PayrollService()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return self.service.repository.model.objects.none()

        user = cast(User, user)
        if user.role in ['ADMIN', 'HR']:
            return self.service.get_all_payrolls().order_by('-month')

        # Employees and Managers can only see their own payroll
        return self.service.repository.model.objects.select_related('employee').filter(
            employee__employee_id=user.employee_id
        ).order_by('-month')

    def list(self, request, *args, **kwargs):
        user = cast(User, request.user)
        query_params = request.query_params.urlencode()
        cache_key = f"v1_payroll_list_{user.id}_{user.role}_{query_params}"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return SuccessResponse(data=cached_data, message="Payroll records fetched successfully (cached)")

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
            cache.set(cache_key, paginated_data, 60 * 5)
            return SuccessResponse(data=paginated_data, message="Payroll records fetched successfully")

        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, 60 * 5)
        return SuccessResponse(data=serializer.data, message="Payroll records fetched successfully")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return SuccessResponse(data=serializer.data, message="Payroll details fetched successfully")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create_payroll(serializer.validated_data)
        cache.clear()
        
        # Trigger salary PDF generation asynchronously (which will also send the email)
        from company_portal.tasks.payroll_tasks import generate_salary_pdf
        getattr(generate_salary_pdf, 'delay')(obj.id)
        
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="Payroll Created Successfully (PDF & Email Generation Queued)", status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update_payroll(instance.id, serializer.validated_data)
        cache.clear()
        
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="Payroll Updated Successfully")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_payroll(instance.id)
        cache.clear()
        return SuccessResponse(message="Payroll Deleted Successfully")
