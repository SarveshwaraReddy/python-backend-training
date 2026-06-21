from django.core.management.base import BaseCommand
from departments.models import Department
from employees.models import Employee
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Seed the database with sample departments and employees'

    def add_arguments(self, parser):
        parser.add_argument('--departments', type=int, default=5, help='Number of departments to create')
        parser.add_argument('--employees', type=int, default=20, help='Number of employees to create')

    def handle(self, *args, **options):
        dept_count = options['departments']
        emp_count = options['employees']

        # Simple sample names and designations
        dept_names = [
            'Engineering', 'Human Resources', 'Marketing', 'Finance', 'Support',
            'Sales', 'Research', 'Operations'
        ]

        first_names = ['Ajay', 'Sara', 'Liam', 'Noah', 'Emma', 'Olivia', 'Ava', 'Mia', 'Lucas', 'Ethan']
        last_names = ['Kumar', 'Patel', 'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia']
        designations = ['Developer', 'Manager', 'Analyst', 'Executive', 'Coordinator']

        created_departments = []
        # Create departments
        for i in range(min(dept_count, len(dept_names))):
            name = dept_names[i]
            obj, created = Department.objects.get_or_create(
                name=name,
                defaults={'description': f'{name} department'}
            )
            created_departments.append(obj)

        # If not enough names provided, create generic departments
        while len(created_departments) < dept_count:
            idx = len(created_departments) + 1
            obj, created = Department.objects.get_or_create(
                name=f'Department {idx}',
                defaults={'description': 'Auto generated department'}
            )
            created_departments.append(obj)

        self.stdout.write(self.style.SUCCESS(f'Created {len(created_departments)} departments'))

        # Create employees
        for i in range(emp_count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            employee_id = f'EMP{1000 + i}'
            email = f'{first.lower()}.{last.lower()}{i}@example.com'
            dept = random.choice(created_departments)
            join_date = timezone.now().date()

            emp, created = Employee.objects.get_or_create(
                employee_id=employee_id,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': email,
                    'phone': f'9{random.randint(100000000,999999999)}',
                    'salary': random.randint(30000, 90000),
                    'joining_date': join_date,
                    'designation': random.choice(designations),
                    'department': dept,
                    'status': 'active',
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created or found {emp_count} employees'))
