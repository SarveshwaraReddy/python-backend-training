from api.views.v1.department import DepartmentViewSet as DepartmentViewSetV1
from api.serializers.v2.department import DepartmentSerializerV2

class DepartmentViewSet(DepartmentViewSetV1):
    serializer_class = DepartmentSerializerV2
