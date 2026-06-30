import os
import logging
import datetime
from django.conf import settings
from django.db import connection
from celery import shared_task
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def generate_attendance_report(self, month=None):
    """
    Asynchronously queries attendance summary and generates a PDF report stored in /media/reports/.
    """
    if not month:
        month = datetime.date.today().strftime('%Y-%m')
        
    logger.info(f"Generating attendance report for month {month}")
    try:
        # Raw SQL query to aggregate attendance
        query = """
            SELECT e.employee_id, e.first_name, e.last_name,
                   COUNT(CASE WHEN a.status = 'present' THEN 1 END) AS present_count,
                   COUNT(CASE WHEN a.status = 'absent' THEN 1 END) AS absent_count,
                   COUNT(CASE WHEN a.status = 'leave' THEN 1 END) AS leave_count
            FROM employees_employee e
            LEFT JOIN attendance_attendance a ON e.id = a.employee_id AND TO_CHAR(a.date, 'YYYY-MM') = %s
            GROUP BY e.employee_id, e.first_name, e.last_name
            ORDER BY e.employee_id;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query, [month])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        pdf_filename = f"attendance_report_{month}_{self.request.id}.pdf"
        pdf_path = os.path.join(reports_dir, pdf_filename)
        
        # Build PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story: list = []
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#2980B9'),
            spaceAfter=15
        )
        normal_style = styles['Normal']
        header_style = ParagraphStyle('HeaderStyle', parent=normal_style, fontName='Helvetica-Bold')
        
        story.append(Paragraph(f"<b>ATTENDANCE REPORT - {month}</b>", title_style))
        story.append(Spacer(1, 10))
        
        # Table data
        table_data = [[
            Paragraph("<b>Emp ID</b>", header_style),
            Paragraph("<b>Name</b>", header_style),
            Paragraph("<b>Present</b>", header_style),
            Paragraph("<b>Absent</b>", header_style),
            Paragraph("<b>Leave</b>", header_style)
        ]]
        
        for res in results:
            table_data.append([
                Paragraph(res['employee_id'], normal_style),
                Paragraph(f"{res['first_name']} {res['last_name']}", normal_style),
                Paragraph(str(res['present_count']), normal_style),
                Paragraph(str(res['absent_count']), normal_style),
                Paragraph(str(res['leave_count']), normal_style)
            ])
            
        t = Table(table_data, colWidths=[100, 180, 80, 80, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2980B9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F2F4F4')]),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ECF0F1')),
        ]))
        
        story.append(t)
        doc.build(story)
        
        logger.info(f"Attendance report PDF generated successfully: {pdf_path}")
        return {
            "month": month,
            "pdf_path": pdf_path,
            "filename": pdf_filename
        }
    except Exception as e:
        logger.error(f"Error generating attendance report: {e}")
        raise e

@shared_task(bind=True)
def generate_department_report(self):
    """
    Asynchronously queries department summaries and generates a PDF report stored in /media/reports/.
    """
    logger.info("Generating department summary report")
    try:
        query = """
            SELECT d.name AS department_name, 
                   COUNT(e.id) AS total_employees,
                   COALESCE(AVG(e.salary), 0.0) AS average_salary
            FROM departments_department d
            LEFT JOIN employees_employee e ON e.department_id = d.id
            GROUP BY d.name
            ORDER BY d.name;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        pdf_filename = f"department_report_{self.request.id}.pdf"
        pdf_path = os.path.join(reports_dir, pdf_filename)
        
        # Build PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story: list = []
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#27AE60'),
            spaceAfter=15
        )
        normal_style = styles['Normal']
        header_style = ParagraphStyle('HeaderStyle', parent=normal_style, fontName='Helvetica-Bold')
        
        story.append(Paragraph("<b>DEPARTMENT SUMMARY REPORT</b>", title_style))
        story.append(Spacer(1, 10))
        
        # Table data
        table_data = [[
            Paragraph("<b>Department Name</b>", header_style),
            Paragraph("<b>Total Employees</b>", header_style),
            Paragraph("<b>Average Salary</b>", header_style)
        ]]
        
        for res in results:
            table_data.append([
                Paragraph(res['department_name'], normal_style),
                Paragraph(str(res['total_employees']), normal_style),
                Paragraph(f"${float(res['average_salary']):.2f}", normal_style)
            ])
            
        t = Table(table_data, colWidths=[240, 140, 140])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#E8F8F5')]),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ECF0F1')),
        ]))
        
        story.append(t)
        doc.build(story)
        
        logger.info(f"Department report PDF generated successfully: {pdf_path}")
        return {
            "pdf_path": pdf_path,
            "filename": pdf_filename
        }
    except Exception as e:
        logger.error(f"Error generating department report: {e}")
        raise e

@shared_task
def clear_temporary_files():
    """
    Cleans up old reports and payroll files older than 24 hours to optimize disk space.
    """
    logger.info("Cleaning up temporary and old files...")
    now = datetime.datetime.now()
    cleaned_count = 0
    
    for folder in ['reports', 'payrolls']:
        folder_path = os.path.join(settings.MEDIA_ROOT, folder)
        if not os.path.exists(folder_path):
            continue
            
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if not os.path.isfile(file_path):
                continue
                
            file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if now - file_mtime > datetime.timedelta(hours=24):
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")
                    
    logger.info(f"Cleanup finished. Deleted {cleaned_count} old files.")
    return f"Deleted {cleaned_count} files."
