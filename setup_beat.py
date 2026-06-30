import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_portal.settings')
django.setup()

from django_celery_beat.models import PeriodicTask, CrontabSchedule

def setup_periodic_tasks():
    print("Setting up crontab and interval schedules...")
    
    # 1. Daily at 8:00 PM (20:00) for attendance report
    daily_crontab, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='20',
        day_of_week='*',
        day_of_month='*',
        month_of_year='*'
    )
    
    # 2. Weekly at Sunday Midnight for department summary report
    weekly_crontab, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='0',
        day_of_week='0',  # Sunday
        day_of_month='*',
        month_of_year='*'
    )
    
    # 3. Monthly on the 1st at 9:00 AM for payroll slip generation
    monthly_crontab, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='9',
        day_of_week='*',
        day_of_month='1',  # 1st of the month
        month_of_year='*'
    )
    
    # 4. Hourly for clearing temporary files
    hourly_crontab, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='*',
        day_of_week='*',
        day_of_month='*',
        month_of_year='*'
    )

    print("Creating periodic tasks...")
    
    # Create or update periodic tasks
    PeriodicTask.objects.update_or_create(
        name='Daily Attendance Summary Report',
        defaults={
            'crontab': daily_crontab,
            'task': 'company_portal.tasks.report_tasks.generate_attendance_report',
        }
    )
    
    PeriodicTask.objects.update_or_create(
        name='Weekly Department Summary Report',
        defaults={
            'crontab': weekly_crontab,
            'task': 'company_portal.tasks.report_tasks.generate_department_report',
        }
    )
    
    PeriodicTask.objects.update_or_create(
        name='Monthly Payroll Generation',
        defaults={
            'crontab': monthly_crontab,
            'task': 'company_portal.tasks.payroll_tasks.run_monthly_payroll_generation',
        }
    )
    
    PeriodicTask.objects.update_or_create(
        name='Hourly Clear Temporary Files',
        defaults={
            'crontab': hourly_crontab,
            'task': 'company_portal.tasks.report_tasks.clear_temporary_files',
        }
    )

    print("Periodic tasks set up successfully!")

if __name__ == '__main__':
    setup_periodic_tasks()
