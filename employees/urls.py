from django.urls import path
from .views import (
    HomeView, AboutView, ContactView,
    EmployeeListView, EmployeeDetailView, 
    EmployeeCreateView, EmployeeUpdateView, EmployeeDeleteView,LoginView
)

app_name = 'employees'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('login/',LoginView.as_view(), name='login'),
    path('employees/', EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', EmployeeCreateView.as_view(), name='employee_add'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/update/<int:pk>/', EmployeeUpdateView.as_view(), name='employee_edit'),
    path('employees/delete/<int:pk>/', EmployeeDeleteView.as_view(), name='employee_delete'),
]
