Employee User Management System (Python Django)
📌 Overview
This project implements a secure enterprise-level user management system using Django. It covers authentication, authorization, custom user models, role-based access control (RBAC), permissions, dashboards, and profile management — essential for any company application requiring secure access.

⚙️ Tech Stack
Python (Django Framework)

Django ORM (Authentication, Authorization, Permissions, Groups)

PostgreSQL

📂 Modules Implemented
Authentication Fundamentals: Login, Logout, Password Verification

Django Authentication System: Built-in User Model, Sessions, Password Hashing, Permissions, Groups

Custom User Model: Email-based login, Employee ID, Phone, Role, Profile Image

User Registration: Validation rules, password strength, unique email/employee ID

Login & Logout: Session-based authentication

Role-Based Access Control: Decorators for Admin, HR, Manager, Employee

Groups & Permissions: Dynamic assignment of permissions

User Dashboard: Role-based dashboard redirection

Password Management: Change password, forgot password, reset via email token

Profile Management: Update profile image, phone, personal details

🧩 Features
Secure User Registration

Login/Logout with session management

RBAC with decorators (@admin_required, @hr_required, etc.)

Groups & Permissions for fine-grained access control

Role-based Dashboards (Admin, HR, Employee)

Password Reset Workflow with email verification

Profile Management (image upload, phone update, personal details)

📊 Dashboards
Admin Dashboard: Total employees, departments, user statistics

HR Dashboard: Employee management, recruitment metrics

Employee Dashboard: Profile, salary info, department


🚀 How to Run
Clone the repository

Install dependencies:

bash
pip install -r requirements.txt
Run migrations:

bash
python manage.py migrate
Start the server:

bash
python manage.py runserver
Access at http://127.0.0.1:8000/
