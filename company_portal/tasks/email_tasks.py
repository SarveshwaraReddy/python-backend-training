import logging
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from celery import shared_task
from employees.models import Employee
from payroll.models import Payroll
import os

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def send_welcome_email(self, employee_id):
    """
    Sends a welcome email to the newly registered employee.
    Retries up to 5 times with 30 seconds delay if an error occurs.
    """
    logger.info(f"Starting welcome email task for employee ID: {employee_id}")
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        subject = "Welcome to Company Portal!"
        message = (
            f"Dear {employee.first_name},\n\n"
            f"Welcome to the team! Your employee ID is {employee.employee_id}.\n"
            f"We are excited to have you join us as a {employee.designation}.\n\n"
            f"Best regards,\nHR Team"
        )
        recipient_list = [employee.email]
        
        # Simulating external email provider failure for testing retry
        if employee.email.startswith("fail-retry"):
            raise ConnectionError("SMTP server is temporarily unreachable.")
            
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'admin@company.local',
            recipient_list,
            fail_silently=False,
        )
        logger.info(f"Welcome email successfully sent to {employee.email}")
        return f"Welcome email sent to {employee.email}"
    except Employee.DoesNotExist as e:
        logger.error(f"Employee with ID {employee_id} does not exist.")
        raise e
    except Exception as e:
        logger.warning(f"Error sending welcome email for {employee_id}. Retrying in 30 seconds... (Attempt {self.request.retries + 1}/5). Error: {e}")
        raise self.retry(exc=e)

@shared_task
def send_salary_email(employee_id, payroll_id):
    """
    Sends the salary slip to the employee, attaching the salary PDF if it exists.
    """
    logger.info(f"Sending salary email for employee ID: {employee_id}, payroll ID: {payroll_id}")
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        payroll = Payroll.objects.get(id=payroll_id)
        
        subject = f"Salary Slip for {payroll.month}"
        body = (
            f"Dear {employee.first_name},\n\n"
            f"Please find attached your salary slip for the month of {payroll.month}.\n"
            f"Net Salary: {payroll.net_salary}\n\n"
            f"Best regards,\nPayroll Team"
        )
        
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'payroll@company.local',
            to=[employee.email],
        )
        
        # Check if the PDF slip is generated and saved under media/payrolls
        pdf_filename = f"salary_slip_{employee.employee_id}_{payroll.month}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'payrolls', pdf_filename)
        
        if os.path.exists(pdf_path):
            email.attach_file(pdf_path)
            logger.info(f"Attached generated PDF from {pdf_path}")
        else:
            logger.warning(f"PDF salary slip not found at {pdf_path}. Sending email without attachment.")
            
        email.send(fail_silently=False)
        logger.info(f"Salary email sent to {employee.email} for month {payroll.month}")
        return f"Salary email sent to {employee.email}"
    except (Employee.DoesNotExist, Payroll.DoesNotExist) as e:
        logger.error(f"Employee or payroll record not found: {e}")
        raise e
