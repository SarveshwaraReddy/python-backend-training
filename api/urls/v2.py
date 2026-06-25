from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.v2.employee import EmployeeViewSet
from api.views.v2.department import DepartmentViewSet
from api.views.v1.auth import LoginView, LogoutView, RefreshTokenView
from api.views.v1.audit_logs import AuditLogViewSet
from api.views.v1.user import UserViewSet

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee-v2')
router.register('departments', DepartmentViewSet, basename='department-v2')
router.register('audit-logs', AuditLogViewSet, basename='audit-log-v2')
router.register('users', UserViewSet, basename='user-v2')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login-v2'),
    path('auth/logout/', LogoutView.as_view(), name='logout-v2'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh-v2'),
    path('', include(router.urls)),
]
