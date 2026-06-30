from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Employee Management API System",
        default_version='v1',
        description="Comprehensive documentation for Company Portal Employee Management system, including versioned APIs (v1 and v2), authentication, user profile management, departments, employees, and audit logs.",
        contact=openapi.Contact(email="admin@company.local"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

from api.views.v1.task_status import TaskStatusView

urlpatterns = [
    # Task Status API
    path('tasks/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
    
    # Version 1 APIs
    path('v1/', include('api.urls.v1')),
    
    # Version 2 APIs
    path('v2/', include('api.urls.v2')),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
