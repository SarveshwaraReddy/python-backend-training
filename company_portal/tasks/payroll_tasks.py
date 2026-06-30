import os
import logging
import csv
from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model
from celery import shared_task
from payroll.models import Payroll
from employees.models import Employee
from departments.models import Department
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def generate_salary_pdf(payroll_id):
    """
    Generates a salary slip PDF for the given payroll record, saves it to disk,
    and then triggers sending the salary slip email.
    """
    logger.info(f"Generating salary slip PDF for payroll ID: {payroll_id}")
    try:
        payroll = Payroll.objects.select_related('employee', 'employee__department').get(id=payroll_id)
        employee = payroll.employee
        
        # Ensure target directory exists
        payrolls_dir = os.path.join(settings.MEDIA_ROOT, 'payrolls')
        os.makedirs(payrolls_dir, exist_ok=True)
        
        pdf_filename = f"salary_slip_{employee.employee_id}_{payroll.month}.pdf"
        pdf_path = os.path.join(payrolls_dir, pdf_filename)
        
        # Generate the PDF using reportlab
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story: list = []
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=15
        )
        
        normal_style = styles['Normal']
        
        story.append(Paragraph("<b>COMPANY PORTAL - SALARY SLIP</b>", title_style))
        story.append(Spacer(1, 10))
        
        data = [
            [Paragraph("<b>Employee ID:</b>", normal_style), Paragraph(employee.employee_id, normal_style),
             Paragraph("<b>Month:</b>", normal_style), Paragraph(payroll.month, normal_style)],
            [Paragraph("<b>Employee Name:</b>", normal_style), Paragraph(f"{employee.first_name} {employee.last_name}", normal_style),
             Paragraph("<b>Designation:</b>", normal_style), Paragraph(employee.designation, normal_style)],
            [Paragraph("<b>Department:</b>", normal_style), Paragraph(employee.department.name, normal_style),
             Paragraph("<b>Joining Date:</b>", normal_style), Paragraph(str(employee.joining_date), normal_style)],
            [Paragraph("<b>Basic/Net Salary:</b>", normal_style), Paragraph(f"${payroll.net_salary}", normal_style),
             Paragraph("<b>Payment Status:</b>", normal_style), Paragraph("Paid", normal_style)],
        ]
        
        t = Table(data, colWidths=[120, 150, 100, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8F9FA')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ECF0F1')),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        story.append(t)
        story.append(Spacer(1, 30))
        story.append(Paragraph("This is a computer-generated salary slip and does not require a signature.", styles['Italic']))
        
        doc.build(story)
        logger.info(f"Salary slip PDF generated successfully at {pdf_path}")
        
        # Trigger sending email asynchronously
        from company_portal.tasks.email_tasks import send_salary_email
        getattr(send_salary_email, 'delay')(employee.employee_id, payroll.id)
        
        return pdf_path
    except Payroll.DoesNotExist as e:
        logger.error(f"Payroll record {payroll_id} not found.")
        raise e
    except Exception as e:
        logger.error(f"Error generating salary PDF for payroll {payroll_id}: {e}")
        raise e

@shared_task(bind=True)
def bulk_employee_import_task(self, file_path, user_id):
    """
    Parses a CSV or Excel (XLSX) file containing employee records,
    creates or updates Employee records in the database, and triggers welcome emails.
    Generates a detailed summary report.
    """
    logger.info(f"Starting bulk employee import task for file: {file_path}")
    import_summary = {
        "total_rows": 0,
        "success_count": 0,
        "failed_count": 0,
        "errors": []
    }
    
    # Check extension
    _, ext = os.path.splitext(file_path.lower())
    rows = []
    
    try:
        if ext == '.csv':
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    rows.append(r)
        elif ext in ['.xlsx', '.xls']:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            if sheet is None:
                raise ValueError("Excel file contains no active sheet")
            # Get headers from first row
            headers = [cell.value for cell in sheet[1]]
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if any(row):  # skip completely empty rows
                    row_dict = dict(zip(headers, row))
                    rows.append(row_dict)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        import_summary["total_rows"] = len(rows)
        
        # Prepare to call send_welcome_email tasks
        from company_portal.tasks.email_tasks import send_welcome_email
        from company_portal.tasks.notification_tasks import notify_hr
        
        for idx, row in enumerate(rows, start=1):
            try:
                # Basic validation
                emp_id = str(row.get('employee_id') or '').strip()
                first_name = str(row.get('first_name') or '').strip()
                last_name = str(row.get('last_name') or '').strip()
                email = str(row.get('email') or '').strip()
                phone = str(row.get('phone') or '').strip()
                salary = row.get('salary')
                joining_date = str(row.get('joining_date') or '').strip()
                designation = str(row.get('designation') or '').strip()
                dept_name = str(row.get('department_name') or row.get('department') or '').strip()
                
                if not emp_id or not first_name or not email or not dept_name:
                    raise ValueError(f"Missing required fields (employee_id, first_name, email, department_name)")
                
                # Fetch or create department
                dept, _ = Department.objects.get_or_create(
                    name=dept_name,
                    defaults={'description': f'Auto-created department: {dept_name}'}
                )
                
                # Clean joining date format
                if hasattr(joining_date, 'strftime'):
                    joining_date_str = joining_date.strftime('%Y-%m-%d')
                else:
                    joining_date_str = joining_date.split(' ')[0]
                    
                # Clean salary
                try:
                    salary_val = float(salary) if salary is not None else 10000.0
                except (ValueError, TypeError):
                    salary_val = 10000.0
                
                with transaction.atomic():
                    # Create or update Employee
                    employee, created = Employee.objects.update_or_create(
                        employee_id=emp_id,
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                            'phone': phone,
                            'salary': salary_val,
                            'joining_date': joining_date_str,
                            'designation': designation,
                            'department': dept,
                            'status': 'active'
                        }
                    )
                    
                    # Auto-create User account if not exists
                    user_email = email
                    user_model = User
                    if not user_model.objects.filter(email=user_email).exists():
                        from django.utils.crypto import get_random_string
                        getattr(user_model.objects, 'create_user')(
                            email=user_email,
                            employee_id=emp_id,
                            first_name=first_name,
                            last_name=last_name,
                            role='EMPLOYEE',
                            password=get_random_string(length=12)
                        )
                
                # Trigger welcome email asynchronously
                getattr(send_welcome_email, 'delay')(emp_id)
                import_summary["success_count"] += 1
                
            except Exception as row_error:
                logger.warning(f"Error processing row {idx}: {row_error}")
                import_summary["failed_count"] += 1
                import_summary["errors"].append({
                    "row": idx,
                    "data": row,
                    "error": str(row_error)
                })
                
        # Generate detailed import report file
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        report_filename = f"import_report_{self.request.id}.txt"
        report_path = os.path.join(reports_dir, report_filename)
        
        with open(report_path, mode='w', encoding='utf-8') as rf:
            rf.write("BULK EMPLOYEE IMPORT REPORT\n")
            rf.write("===========================\n")
            rf.write(f"Task ID: {self.request.id}\n")
            rf.write(f"Total Rows: {import_summary['total_rows']}\n")
            rf.write(f"Successfully Imported: {import_summary['success_count']}\n")
            rf.write(f"Failed Rows: {import_summary['failed_count']}\n\n")
            
            if import_summary["errors"]:
                rf.write("Failed Rows Details:\n")
                rf.write("--------------------\n")
                for err in import_summary["errors"]:
                    rf.write(f"Row {err['row']}: Error: {err['error']}\n")
                    rf.write(f"Data: {err['data']}\n\n")
                    
        logger.info(f"Bulk employee import finished. Report saved at {report_path}")
        
        # Notify HR about bulk import completion
        getattr(notify_hr, 'delay')(
            action_type="BULK_IMPORT",
            details=f"Bulk employee import completed. Total: {import_summary['total_rows']}, Success: {import_summary['success_count']}, Failed: {import_summary['failed_count']}. Report: {report_filename}"
        )
        
        return {
            "total_rows": import_summary["total_rows"],
            "success_count": import_summary["success_count"],
            "failed_count": import_summary["failed_count"],
            "report_file": report_filename
        }
        
    except Exception as e:
        logger.error(f"Bulk employee import failed: {e}")
        raise e

@shared_task
def run_monthly_payroll_generation():
    """
    Periodic task run monthly. Generates payroll records and triggers salary slip PDFs
    for all active employees for the current month.
    """
    import datetime
    current_month = datetime.date.today().strftime('%Y-%m')
    logger.info(f"Triggering monthly payroll generation for month: {current_month}")
    
    active_employees = Employee.objects.filter(status='active')
    triggered_count = 0
    
    for employee in active_employees:
        payroll, created = Payroll.objects.get_or_create(
            employee=employee,
            month=current_month,
            defaults={'net_salary': employee.salary}
        )
        
        # Trigger PDF generation (which also sends email)
        getattr(generate_salary_pdf, 'delay')(payroll.id)
        triggered_count += 1
        
    logger.info(f"Completed scheduling payroll generation for {triggered_count} employees.")
    return f"Scheduled {triggered_count} payroll slip tasks."
