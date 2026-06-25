from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.v1.auth import LoginView, LogoutView, RefreshTokenView
from api.views.v1.employee import EmployeeViewSet
from api.views.v1.department import DepartmentViewSet
from api.views.v1.audit_logs import AuditLogViewSet
from api.views.v1.user import UserViewSet

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee-v1')
router.register('departments', DepartmentViewSet, basename='department-v1')
router.register('audit-logs', AuditLogViewSet, basename='audit-log-v1')
router.register('users', UserViewSet, basename='user-v1')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login-v1'),
    path('auth/logout/', LogoutView.as_view(), name='logout-v1'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh-v1'),
    path('', include(router.urls)),
]
