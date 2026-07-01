from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.v2.employee import EmployeeViewSet
from api.views.v2.department import DepartmentViewSet
from api.views.v2.reports import ORMReportsView
from api.views.v1.auth import LoginView, LogoutView, RefreshTokenView
from api.views.v1.audit_logs import AuditLogViewSet
from api.views.v1.user import UserViewSet
from api.views.v1.payroll import PayrollViewSet
from api.views.v1.attendance import AttendanceViewSet

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee-v2')
router.register('departments', DepartmentViewSet, basename='department-v2')
router.register('audit-logs', AuditLogViewSet, basename='audit-log-v2')
router.register('users', UserViewSet, basename='user-v2')
router.register('payroll', PayrollViewSet, basename='payroll-v2')
router.register('attendance', AttendanceViewSet, basename='attendance-v2')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login-v2'),
    path('auth/logout/', LogoutView.as_view(), name='logout-v2'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh-v2'),
    path('reports/<str:report_type>/', ORMReportsView.as_view(), name='reports-v2'),
    path('', include(router.urls)),
]

