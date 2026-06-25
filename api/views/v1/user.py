from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from api.services.user import UserService
from api.serializers.v1.user import UserSerializer
from api.permissions import UserRBACPermission
from api.pagination import StandardResultsSetPagination
from api.responses.custom_response import SuccessResponse

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [UserRBACPermission]
    pagination_class = StandardResultsSetPagination

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserService()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return self.service.repository.model.objects.none()
            
        if user.role in ['ADMIN', 'HR']:
            return self.service.get_all_users().order_by('id')
            
        return self.service.repository.model.objects.filter(id=user.id).order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return SuccessResponse(data=self.get_paginated_response(serializer.data).data, message="Users fetched successfully")

        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, message="Users fetched successfully")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return SuccessResponse(data=serializer.data, message="User details fetched successfully")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.service.create_user(serializer.validated_data)
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="User created successfully", status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        obj = self.service.update_user(instance.id, serializer.validated_data)
        out_serializer = self.get_serializer(obj)
        return SuccessResponse(data=out_serializer.data, message="User updated successfully")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_user(instance.id)
        return SuccessResponse(message="User deleted successfully")

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return SuccessResponse(data=serializer.data, message="Profile fetched successfully")
        elif request.method in ['PUT', 'PATCH']:
            partial = (request.method == 'PATCH')
            serializer = self.get_serializer(user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            obj = self.service.update_user(user.id, serializer.validated_data)
            out_serializer = self.get_serializer(obj)
            return SuccessResponse(data=out_serializer.data, message="Profile updated successfully")
