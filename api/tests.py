# API tests for company_portal
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from departments.models import Department
from employees.models import Employee
from audit_logs.models import AuditLog

class HRMSPlatformTests(APITestCase):
    client: APIClient
    
    def setUp(self):
        self.dept = Department.objects.create(name="Engineering", description="Eng Dept")
        
        self.admin_user = User.objects.create_user(
            email="admin@company.local",
            username="admin@company.local",
            employee_id="ADM001",
            role="ADMIN",
            password="testpassword123"
        )
        
        self.employee_user = User.objects.create_user(
            email="emp@company.local",
            username="emp@company.local",
            employee_id="EMP001",
            role="EMPLOYEE",
            password="testpassword123"
        )
        
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            email="emp@company.local",
            phone="9123456789",
            salary=50000.00,
            joining_date="2026-01-01",
            designation="Developer",
            department=self.dept,
            status="active"
        )

    def test_jwt_login_success(self):
        url = reverse('login-v1')
        data = {
            "email": "admin@company.local",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        login_log = AuditLog.objects.filter(action="LOGIN", user=self.admin_user).exists()
        self.assertTrue(login_log)

    def test_custom_response_format_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('employee-v1-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Employees fetched successfully")
        self.assertIn('data', response.data)

    def test_custom_response_format_validation_error(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('employee-v1-list')
        data = {
            "employee_id": "EMP999",
            "first_name": "Invalid"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], "Validation Failed")
        self.assertIn('email', response.data['errors'])

    def test_api_versioning_differences(self):
        self.client.force_authenticate(user=self.admin_user)
        
        url_v1 = reverse('employee-v1-detail', args=[self.employee.id])
        response_v1 = self.client.get(url_v1)
        self.assertEqual(response_v1.status_code, status.HTTP_200_OK)
        self.assertNotIn('salary', response_v1.data['data'])
        self.assertNotIn('joining_date', response_v1.data['data'])
        
        url_v2 = reverse('employee-v2-detail', args=[self.employee.id])
        response_v2 = self.client.get(url_v2)
        self.assertEqual(response_v2.status_code, status.HTTP_200_OK)
        self.assertIn('salary', response_v2.data['data'])
        self.assertIn('joining_date', response_v2.data['data'])
        self.assertEqual(response_v2.data['data']['department']['name'], "Engineering")

    def test_signals_audit_logging_employee_lifecycle(self):
        self.client.force_authenticate(user=self.admin_user)
        
        AuditLog.objects.all().delete()
        
        url = reverse('employee-v1-list')
        data = {
            "employee_id": "EMP102",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@company.local",
            "phone": "9876543210",
            "salary": 60000.00,
            "joining_date": "2026-01-15",
            "designation": "Manager",
            "department": self.dept.id,
            "status": "active"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        create_log = AuditLog.objects.filter(action="CREATE", module="Employees").first()
        self.assertIsNotNone(create_log)
        self.assertIn("EMP102", create_log.details or "")
        
        emp_id = response.data['data']['id']
        url_detail = reverse('employee-v1-detail', args=[emp_id])
        response_del = self.client.delete(url_detail)
        self.assertEqual(response_del.status_code, status.HTTP_200_OK)
        
        delete_log = AuditLog.objects.filter(action="DELETE", module="Employees").first()
        self.assertIsNotNone(delete_log)
        self.assertIn("Jane Smith", delete_log.details or "")

    def test_audit_logs_rbac(self):
        self.client.force_authenticate(user=self.employee_user)
        url = reverse('audit-log-v1-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.force_authenticate(user=self.admin_user)
        response_admin = self.client.get(url)
        self.assertEqual(response_admin.status_code, status.HTTP_200_OK)
        self.assertTrue(response_admin.data['success'])
