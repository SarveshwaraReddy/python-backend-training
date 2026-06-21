# Employee Database Management System

A Django project for managing company employees and departments using PostgreSQL database.

## Project Overview

This project is an HR Management Portal built to manage company structure and staff. It provides a comprehensive system to handle:
- **Departments**: Create, organize, and manage different functional groups within the company. Each department can have its own description and tracking.
- **Employees**: Detailed employee records including personal information, contact details, job designation, salary, and their assigned department.

The system was built as part of backend training to learn:
- PostgreSQL database setup
- Django models and migrations
- Django ORM CRUD operations
- Django Admin Panel customization
- HR Management Portal with search and filter

## Project Structure

```
company_portal/
├── manage.py
├── employees/
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   └── templates/
├── departments/
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   └── templates/
├── requirements.txt
└── README.md
```

## Tech Stack

- Python
- Django 6
- PostgreSQL
- HTML / CSS

## PostgreSQL Setup

1. Install PostgreSQL and verify:

```powershell
psql --version
```

2. Open PostgreSQL shell and run:

```sql
CREATE DATABASE employee_management;

CREATE USER employee_admin WITH PASSWORD 'password123';

GRANT ALL PRIVILEGES ON DATABASE employee_management TO employee_admin;
```

3. Database settings are configured in `company_portal/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'employee_management',
        'USER': 'employee_admin',
        'PASSWORD': 'password123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## How to Run

1. Go to project folder:

```powershell
cd Django-projects/company_portal
```

2. Activate virtual environment:

```powershell
..\venv\Scripts\activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Run migrations:

```powershell
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser for admin panel:

```powershell
python manage.py createsuperuser
```

6. Start server:

```powershell
python manage.py runserver
```

7. Open in browser:
- Home: http://127.0.0.1:8000/
- Departments: http://127.0.0.1:8000/departments/
- Employees: http://127.0.0.1:8000/employees/
- Admin Panel: http://127.0.0.1:8000/admin/

## Seed Sample Data (Optional)

You can populate the database with sample data (5 departments, 20 employees by default) using the custom management command:

```powershell
python manage.py seed_data
```

Pass `--departments` and `--employees` to change counts:

```powershell
python manage.py seed_data --departments 5 --employees 20
```

## Models

### Department
- name
- description
- created_at
- updated_at

### Employee
- employee_id
- first_name
- last_name
- email
- phone
- salary
- joining_date
- designation
- department (Foreign Key)
- status
- created_at
- updated_at

## Django ORM Examples

Open Django shell:

```powershell
python manage.py shell
```

Create department:

```python
from departments.models import Department
Department.objects.create(name="Engineering", description="Software development team")
```

Create employee:

```python
from employees.models import Employee
from departments.models import Department

dept = Department.objects.get(name="Engineering")

Employee.objects.create(
    employee_id="EMP001",
    first_name="Ajay",
    last_name="Kumar",
    email="ajay@example.com",
    phone="9876543210",
    salary=50000,
    joining_date="2024-01-15",
    designation="Developer",
    department=dept,
    status="active"
)
```

Sample queries:

```python
Employee.objects.count()
Employee.objects.filter(salary__gt=50000)
Employee.objects.filter(department__name="Engineering")
Employee.objects.order_by("-salary")
```

## Admin Panel Features

- Employee list display with employee_id, name, email, salary, department
- Search employees by employee_id, first_name, email
- Filter employees by department
- Department search by name

## HR Portal Features

### Department Management
- Add Department
- Update Department
- Delete Department
- Search Department

### Employee Management
- Add Employee
- Update Employee
- Delete Employee
- Search Employee
- Filter Employee by Department

## Git Workflow

```powershell
git checkout development
git pull origin development
git checkout -b feature/models-postgresql
```

Suggested commit messages:
- feat: configure PostgreSQL database
- feat: create employee and department models
- feat: implement Django ORM operations
- feat: customize Django admin panel

## Verify Database Tables

```powershell
python manage.py dbshell
```

Inside PostgreSQL shell:

```sql
\dt
```

## Author

Django Backend Developer Trainee
