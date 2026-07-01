# API tests for company_portal
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.test import override_settings
from accounts.models import User
from departments.models import Department
from employees.models import Employee
from audit_logs.models import AuditLog

# Force Celery eager mode during testing to prevent connection attempts to Redis broker
from company_portal.celery import app as celery_app
celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=True,
)

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

    def test_salary_check_constraint(self):
        from django.core.exceptions import ValidationError
        emp = Employee(
            employee_id="EMP990",
            first_name="Short",
            last_name="Paid",
            email="short@company.local",
            phone="9111111111",
            salary=5000.00,  # Invalid salary
            joining_date="2026-01-01",
            designation="Intern",
            department=self.dept,
            status="active"
        )
        with self.assertRaises(ValidationError):
            emp.full_clean()
        
        from django.db import IntegrityError
        with self.assertRaises((IntegrityError, ValidationError)):
            emp.save()

    def test_joining_date_trigger_future(self):
        import datetime
        from django.core.exceptions import ValidationError
        future_date = datetime.date.today() + datetime.timedelta(days=10)
        emp = Employee(
            employee_id="EMP991",
            first_name="Future",
            last_name="Hire",
            email="future@company.local",
            phone="9222222222",
            salary=15000.00,
            joining_date=future_date,
            designation="Developer",
            department=self.dept,
            status="active"
        )
        with self.assertRaises(ValidationError):
            emp.full_clean()
            
        from django.db import InternalError, IntegrityError
        with self.assertRaises((InternalError, IntegrityError, ValidationError)):
            emp.save()

    def test_salary_processing_service_atomicity(self):
        from services.payroll_service import SalaryProcessingService
        from payroll.models import Payroll
        from django.db import IntegrityError
        
        old_salary = self.employee.salary
        month = "2026-06"
        
        payroll_rec = SalaryProcessingService.process_salary(self.employee.employee_id, month, 55000.00)
        self.assertIsNotNone(payroll_rec)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.salary, 55000.00)
        
        with self.assertRaises(IntegrityError):
            SalaryProcessingService.process_salary(self.employee.employee_id, month, 60000.00)
            
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.salary, 55000.00)
        self.assertEqual(Payroll.objects.filter(employee=self.employee, month=month).count(), 1)

    def test_orm_optimization_query_count(self):
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('employee-v1-list')
        
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
        # Should be optimized to avoid N+1 queries. Maximum 5 queries including authentication and count.
        self.assertLessEqual(len(ctx.captured_queries), 5)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_welcome_email_task_trigger_on_employee_create(self):
        from django.core import mail
        self.client.force_authenticate(user=self.admin_user)
        
        mail.outbox = []
        
        url = reverse('employee-v1-list')
        data = {
            "employee_id": "EMP888",
            "first_name": "TestWelcome",
            "last_name": "User",
            "email": "testwelcome@company.local",
            "phone": "9998887776",
            "salary": 35000.00,
            "joining_date": "2026-06-01",
            "designation": "QA Engineer",
            "department": self.dept.id,
            "status": "active"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Welcome to the team!", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ["testwelcome@company.local"])

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_payroll_pdf_and_email_trigger_on_payroll_create(self):
        from django.core import mail
        self.client.force_authenticate(user=self.admin_user)
        mail.outbox = []
        
        url = reverse('payroll-v1-list')
        data = {
            "employee": self.employee.id,
            "month": "2026-07",
            "net_salary": 52000.00
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        import os
        from django.conf import settings
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'payrolls', f"salary_slip_{self.employee.employee_id}_2026-07.pdf")
        self.assertTrue(os.path.exists(pdf_path))
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.employee.email])
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], f"salary_slip_{self.employee.employee_id}_2026-07.pdf")

    def test_task_status_endpoint(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('task-status', args=['dummy-task-id-123'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_id'], 'dummy-task-id-123')
        self.assertIn('status', response.data)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_bulk_employee_import_api_csv(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_authenticate(user=self.admin_user)
        
        csv_content = (
            "employee_id,first_name,last_name,email,phone,salary,joining_date,designation,department_name\n"
            "EMP501,Alice,Smith,alice@company.local,9876543210,45000.00,2026-02-01,Developer,Engineering\n"
            "EMP502,Bob,Jones,bob@company.local,9876543211,48000.00,2026-02-15,Designer,Marketing\n"
        )
        
        uploaded_file = SimpleUploadedFile(
            name="import_employees.csv",
            content=csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        url = reverse('employee-v1-import-bulk')
        response = self.client.post(url, {'file': uploaded_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.data['success'])
        self.assertIn('task_id', response.data['data'])
        
        self.assertTrue(Employee.objects.filter(employee_id="EMP501").exists())
        self.assertTrue(Employee.objects.filter(employee_id="EMP502").exists())
        self.assertEqual(Employee.objects.get(employee_id="EMP501").department.name, "Engineering")

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_async_reports_endpoints(self):
        self.client.force_authenticate(user=self.admin_user)
        
        url_att = reverse('reports-v1', args=['attendance-summary'])
        response_att = self.client.post(url_att, {'month': '2026-06'}, format='json')
        self.assertEqual(response_att.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response_att.data['success'])
        
        url_dept = reverse('reports-v1', args=['department-summary'])
        response_dept = self.client.post(url_dept, format='json')
        self.assertEqual(response_dept.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response_dept.data['success'])


class DjangoORMAndHRAnalyticsTests(APITestCase):
    client: APIClient
    
    def setUp(self):
        self.dept = Department.objects.create(name="Engineering", description="Eng Dept")
        self.dept_sales = Department.objects.create(name="Sales", description="Sales Dept")
        
        self.admin_user = User.objects.create_user(
            email="admin@company.local",
            username="admin@company.local",
            employee_id="ADM001",
            role="ADMIN",
            password="testpassword123"
        )
        
        self.employee1 = Employee.objects.create(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@company.local",
            phone="9123456789",
            salary=50000.00,
            joining_date="2026-06-01",
            designation="Developer",
            department=self.dept,
            status="active"
        )

        self.employee2 = Employee.objects.create(
            employee_id="EMP002",
            first_name="Jane",
            last_name="Smith",
            email="jane@company.local",
            phone="9123456780",
            joining_date="2026-07-01",
            salary=70000.00,
            designation="Manager",
            department=self.dept,
            status="active"
        )

        self.employee3 = Employee.objects.create(
            employee_id="EMP003",
            first_name="Bob",
            last_name="Johnson",
            email="bob@company.local",
            phone="9123456781",
            joining_date="2026-05-15",
            salary=30000.00,
            designation="Intern",
            department=self.dept_sales,
            status="inactive"
        )

    def test_model_relationships_and_serializers(self):
        from employees.models import Skill, EmployeeProfile
        self.client.force_authenticate(user=self.admin_user)
        
        # Test creation of profile and skill via serializer
        url = reverse('employee-v2-list')
        data = {
            "employee_id": "EMP010",
            "first_name": "Alice",
            "last_name": "Green",
            "email": "alice@company.local",
            "phone": "9876543210",
            "salary": 65000.00,
            "joining_date": "2026-07-01",
            "designation": "Developer",
            "department_id": self.dept.id,
            "status": "active",
            "profile": {
                "address": "123 Main St",
                "birth_date": "1995-05-20",
                "emergency_contact": "Bob Green"
            },
            "skills": [
                {"name": "Python", "description": "Programming language"},
                {"name": "Django", "description": "Web framework"}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        emp = Employee.objects.get(employee_id="EMP010")
        self.assertEqual(emp.profile.address, "123 Main St")
        self.assertEqual(emp.skills.count(), 2)
        self.assertEqual(list(emp.skills.values_list('name', flat=True)), ["Python", "Django"])

    def test_custom_managers_and_querysets(self):
        # QuerySet chaining 
        self.assertEqual(Employee.objects.active().count(), 2)
        self.assertEqual(Employee.objects.inactive().count(), 1)
        self.assertEqual(Employee.objects.engineering().count(), 2)
        self.assertEqual(Employee.objects.high_salary().count(), 1)
        self.assertEqual(Employee.objects.active().engineering().high_salary().count(), 1)
        
        # Manager methods
        self.assertEqual(Employee.objects.active_employees().count(), 2)
        self.assertEqual(Employee.objects.inactive_employees().count(), 1)
        self.assertEqual(Employee.objects.highest_salary(), self.employee2)
        self.assertEqual(Employee.objects.new_joiners().count(), 1)

    def test_salary_increment_f_expression(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('employee-v2-list') + "increment-salaries/"
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.employee1.refresh_from_db()
        self.assertEqual(float(self.employee1.salary), 55000.00)

    def test_dashboard_stats_aggregation(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('employee-v2-list') + "dashboard-stats/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total_employees'], 3)
        self.assertEqual(float(response.data['data']['total_salary']), 150000.00)
        self.assertEqual(float(response.data['data']['average_salary']), 50000.00)
        self.assertEqual(float(response.data['data']['max_salary']), 70000.00)
        self.assertEqual(float(response.data['data']['min_salary']), 30000.00)

    def test_department_dashboard_annotation(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('department-v2-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        eng_data = [d for d in response.data['data']['results'] if d['name'] == 'Engineering'][0]
        self.assertEqual(eng_data['employee_count'], 2)
        self.assertEqual(eng_data['average_salary'], 60000.00)
        self.assertEqual(eng_data['highest_salary'], 70000.00)
        self.assertEqual(eng_data['lowest_salary'], 50000.00)

    def test_v2_reports_orm(self):
        self.client.force_authenticate(user=self.admin_user)
        
        url_top = reverse('reports-v2', args=['top-salaries'])
        response_top = self.client.get(url_top)
        self.assertEqual(response_top.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_top.data['data']), 3)
        self.assertEqual(response_top.data['data'][0]['employee_id'], "EMP002")
        
        url_dept = reverse('reports-v2', args=['department-summary'])
        response_dept = self.client.get(url_dept)
        self.assertEqual(response_dept.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_dept.data['data']), 2)
        
        url_join = reverse('reports-v2', args=['joined-this-month'])
        response_join = self.client.get(url_join)
        self.assertEqual(response_join.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_join.data['data']), 1)
        self.assertEqual(response_join.data['data'][0]['employee_id'], "EMP002")

    def test_advanced_search_q_objects(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('employee-v2-list')
        
        response = self.client.get(url, {'department_name': 'Engineering', 'min_salary': 60000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['count'], 1)
        self.assertEqual(response.data['data']['results'][0]['employee_id'], "EMP002")

        response_ex = self.client.get(url, {'exclude_department': 'Sales'})
        self.assertEqual(response_ex.status_code, status.HTTP_200_OK)
        self.assertEqual(response_ex.data['data']['count'], 2)



