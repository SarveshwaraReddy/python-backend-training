from django.db import transaction
from employees.models import Employee
from payroll.models import Payroll
from audit_logs.models import AuditLog
from company_portal.middleware import get_current_user, get_current_ip

class SalaryProcessingService:
    @staticmethod
    def process_salary(employee_id, month, net_salary):
        """
        Updates an employee's salary, creates a payroll record for the given month,
        and logs the action in the audit log. The entire process is wrapped in an atomic transaction.
        If any step fails, everything is rolled back.
        """
        with transaction.atomic():
            # 1. Retrieve the employee and lock the row for update
            try:
                employee = Employee.objects.select_for_update().get(employee_id=employee_id)
            except Employee.DoesNotExist:
                raise ValueError(f"Employee with ID {employee_id} does not exist.")

            # 2. Update employee's salary
            old_salary = employee.salary
            employee.salary = net_salary
            employee.save()

            # 3. Create the payroll record
            payroll_record = Payroll.objects.create(
                employee=employee,
                month=month,
                net_salary=net_salary
            )

            # 4. Create the audit log
            user = get_current_user()
            ip = get_current_ip()
            details = (
                f"Processed salary for Employee {employee_id} ({employee.first_name} {employee.last_name}). "
                f"Salary updated from {old_salary} to {net_salary}. Payroll record ID: {payroll_record.id}"
            )
            
            AuditLog.objects.create(
                user=user,
                action="UPDATE",
                module="Employees",
                ip_address=ip,
                details=details
            )

            return payroll_record
