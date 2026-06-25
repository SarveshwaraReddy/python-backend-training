from api.views.v1.employee import EmployeeViewSet as EmployeeViewSetV1
from api.serializers.v2.employee import EmployeeSerializerV2

class EmployeeViewSet(EmployeeViewSetV1):
    serializer_class = EmployeeSerializerV2
