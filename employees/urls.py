from django.urls import path
from .views import (
    home, about, contact,
    employee_list, employee_add, employee_edit, employee_delete,
)

app_name = 'employees'

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('employees/', employee_list, name='employee_list'),
    path('employees/add/', employee_add, name='employee_add'),
    path('employees/edit/<int:pk>/', employee_edit, name='employee_edit'),
    path('employees/delete/<int:pk>/', employee_delete, name='employee_delete'),
]
