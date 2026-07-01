from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, F, Count, Sum, Avg, Max, Min
from django.core.cache import cache
from api.views.v1.employee import EmployeeViewSet as EmployeeViewSetV1
from api.serializers.v2.employee import EmployeeSerializerV2
from api.responses.custom_response import SuccessResponse
from employees.models import Employee
from rest_framework import status

class EmployeeViewSet(EmployeeViewSetV1):
    serializer_class = EmployeeSerializerV2

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Employee.objects.none()
        
        # Module 10: Optimize queries by select_related profile and prefetching skills
        queryset = Employee.objects.select_related('department', 'profile').prefetch_related('skills')

        if user.role not in ['ADMIN', 'HR']:
            queryset = queryset.filter(employee_id=user.employee_id)

        # Module 2: Advanced Search/Filter using Q objects (AND, OR, NOT)
        q_filter = Q()
        
        dept = self.request.query_params.get('department_name')
        if dept:
            q_filter &= Q(department__name__iexact=dept)
            
        min_salary = self.request.query_params.get('min_salary')
        if min_salary:
            q_filter &= Q(salary__gte=min_salary)
            
        max_salary = self.request.query_params.get('max_salary')
        if max_salary:
            q_filter &= Q(salary__lte=max_salary)

        status_param = self.request.query_params.get('status')
        if status_param:
            q_filter &= Q(status__iexact=status_param)

        skills = self.request.query_params.get('skills')
        if skills:
            skill_list = [s.strip() for s in skills.split(',') if s.strip()]
            for skill_name in skill_list:
                q_filter &= Q(skills__name__iexact=skill_name)

        exclude_dept = self.request.query_params.get('exclude_department')
        if exclude_dept:
            q_filter &= ~Q(department__name__iexact=exclude_dept)

        search = self.request.query_params.get('search')
        if search:
            search_filter = (
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) | 
                Q(employee_id__icontains=search) | 
                Q(email__icontains=search)
            )
            q_filter &= search_filter

        queryset = queryset.filter(q_filter)
        return queryset.distinct().order_by('employee_id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        cache.clear()
        
        # Queue welcome email task asynchronously
        from company_portal.tasks.email_tasks import send_welcome_email
        getattr(send_welcome_email, 'delay')(obj.employee_id)
        
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(
            data=out_serializer.data,
            message="Employee Created Successfully (Welcome Email Queued)",
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        cache.clear()
        
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="Employee Updated Successfully")

    @action(detail=False, methods=['post'], url_path='increment-salaries')
    def increment_salaries(self, request):
        """
        Module 3: Increase every employee salary by 10%.
        No Python loops allowed. Uses F Expressions.
        """
        if request.user.role not in ['ADMIN', 'HR']:
            return Response({"success": False, "message": "Permission Denied"}, status=403)
        
        count = Employee.objects.update(salary=F('salary') * 1.10)
        return SuccessResponse(message=f"Successfully incremented salary for {count} employees by 10%")

    @action(detail=False, methods=['get'], url_path='dashboard-stats')
    def dashboard_stats(self, request):
        """
        Module 4: HR Dashboard statistics.
        Uses Aggregations (Count, Sum, Avg, Max, Min).
        """
        if request.user.role not in ['ADMIN', 'HR']:
            return Response({"success": False, "message": "Permission Denied"}, status=403)
            
        stats = Employee.objects.aggregate(
            total_employees=Count('id'),
            total_salary=Sum('salary'),
            average_salary=Avg('salary'),
            max_salary=Max('salary'),
            min_salary=Min('salary')
        )
        return SuccessResponse(data=stats, message="HR Dashboard statistics fetched successfully")


