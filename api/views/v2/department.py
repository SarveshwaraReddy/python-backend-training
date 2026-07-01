from django.db.models import Count, Avg, Max, Min, FloatField
from django.db.models.functions import Coalesce
from api.views.v1.department import DepartmentViewSet as DepartmentViewSetV1
from api.serializers.v2.department import DepartmentSerializerV2
from departments.models import Department

class DepartmentViewSet(DepartmentViewSetV1):
    serializer_class = DepartmentSerializerV2

    def get_queryset(self):
        # Module 5 & 10: Annotate statistics and optimize with prefetching
        return Department.objects.annotate(
            employee_count=Count('employee'),
            average_salary=Coalesce(Avg('employee__salary'), 0.0, output_field=FloatField()),
            highest_salary=Coalesce(Max('employee__salary'), 0.0, output_field=FloatField()),
            lowest_salary=Coalesce(Min('employee__salary'), 0.0, output_field=FloatField())
        ).prefetch_related('employee_set').order_by('name')


