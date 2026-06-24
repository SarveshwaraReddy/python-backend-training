from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from departments.models import Department
from employees.models import Employee
from accounts.models import User

from api.serializers import DepartmentSerializer, EmployeeSerializer, UserSerializer
from api.permissions import EmployeeRBACPermission, DepartmentRBACPermission, UserRBACPermission
from api.filters import EmployeeFilter
from api.pagination import StandardResultsSetPagination


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Department CRUD.
    - Admin and HR have full CRUD.
    - Other users have read-only access.
    """
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    permission_classes = [DepartmentRBACPermission]
    pagination_class = StandardResultsSetPagination


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Employee CRUD.
    - Admin has full CRUD.
    - HR has CRUD (except DELETE).
    - Employees can only view their own record.
    """
    serializer_class = EmployeeSerializer
    permission_classes = [EmployeeRBACPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']
    ordering_fields = ['salary', 'joining_date']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Employee.objects.none()
        
        # Admin and HR see all employee records
        if user.role in ['ADMIN', 'HR']:
            return Employee.objects.all().order_by('employee_id')
            
        # Managers and Employees can only see their own records
        return Employee.objects.filter(employee_id=user.employee_id).order_by('employee_id')


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Custom User CRUD and Profile Management.
    - Admin has full CRUD.
    - HR can retrieve all users.
    - Any authenticated user can access/update their own profile via /api/users/profile/.
    """
    serializer_class = UserSerializer
    permission_classes = [UserRBACPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
            
        # Admin and HR can see all user accounts
        if user.role in ['ADMIN', 'HR']:
            return User.objects.all().order_by('id')
            
        # Employees and Managers can only see their own user account
        return User.objects.filter(id=user.id).order_by('id')

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """
        Endpoint: GET/PUT/PATCH /api/users/profile/
        Allows any authenticated user to view or update their own user details.
        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            partial = (request.method == 'PATCH')
            serializer = self.get_serializer(user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)