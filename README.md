HRMS Background Processing Platform (Django + Celery + Redis)
📌 Overview
This project demonstrates how to build enterprise-grade asynchronous systems using Celery + Redis + Django. It focuses on background processing, scheduled jobs, email queues, report generation, notifications, retries, monitoring, and task optimization — essential for production-ready HRMS applications.

🎯 Training Goal
Prevent long-running operations (emails, payroll, reports) from blocking user requests by offloading them to background tasks.

⚙️ Tech Stack
Python 3.x

Django (Web framework)

Celery (Distributed task queue)

Redis (Message broker)

django-celery-results (Task result backend)

django-celery-beat (Scheduler)

Flower (Task monitoring dashboard)

📂 Modules Implemented
Asynchronous Processing: Save data, create Celery task, return response immediately

Celery Architecture: Django → Redis Broker → Celery Worker → Result Backend

Package Installation: celery, redis, django-celery-results, django-celery-beat

Celery Configuration: Broker, backend, task discovery, logging

Background Tasks: Welcome emails, salary slip PDFs, attendance reports, notifications

Task States: PENDING, STARTED, SUCCESS, FAILURE, RETRY

Scheduled Tasks: Daily, weekly, monthly, hourly jobs

Retry Mechanism: Retry failed tasks with delay and max retries

Email Queue: Bulk employee import with queued welcome emails

Report Generation: Payroll, attendance, department reports stored in /media/reports/

Monitoring: Flower dashboard for tasks, retries, workers, queue length

Production Optimizations: Separate queues, multiple workers, rate limiting, task priorities

📊 Business Scenario Solved
Sending 5,000 welcome emails without blocking requests

Generating monthly payroll PDFs asynchronously

Creating attendance reports in background

Sending salary slips in parallel

Delivering notifications without delays

📂 Project Structure
Code
company_portal/
│
├── celery.py
│
├── tasks/
│   ├── email_tasks.py
│   ├── payroll_tasks.py
│   ├── report_tasks.py
│   ├── attendance_tasks.py
│   └── notification_tasks.py
│
├── services/
├── reports/
├── media/
└── logs/
🚀 Setup & Installation
Clone the repository

bash
git clone <repo-url>
cd company_portal
Install dependencies

bash
pip install -r requirements.txt
Start Redis server

bash
redis-server
Run Celery worker

bash
celery -A company_portal worker -l info
Run Celery beat (scheduler)

bash
celery -A company_portal beat -l info
Run Django server

bash
python manage.py runserver
🧩 Practical Tasks Implemented
send_welcome_email()

generate_salary_pdf()

send_salary_email()

notify_hr()

generate_attendance_report()

Task status API: /api/tasks/{task_id}

Scheduled jobs with Celery Beat

Retry mechanism for failed tasks

Bulk employee import with queued emails

📊 Monitoring
Run Flower:

bash
celery -A company_portal flower
Access dashboard: http://localhost:5555

Monitor:

Running tasks

Failed tasks

Retries

Workers

Queue length

📌 Learning Outcomes
Build scalable asynchronous systems

Implement enterprise HRMS background processing

Optimize tasks with queues, workers, priorities, and retries

Monitor and manage tasks in production environments
