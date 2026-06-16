from __future__ import annotations

from pathlib import Path

from employee_management_system.models.employee import Employee
from employee_management_system.services.auth_service import AuthService
from employee_management_system.services.employee_service import EmployeeService
from employee_management_system.services.report_service import ReportService
from employee_management_system.utils.logger import configure_logger, get_logger
from employee_management_system.decorators.permissions import (
    admin_required,
    hr_or_admin_required,
    employee_self_or_higher,
)


DATA_DIR = Path(__file__).resolve().parent / "data"
LOG_DIR = Path(__file__).resolve().parent / "logs"


def print_employee(employee: Employee) -> None:
    print(
        f"ID: {employee.employee_id} | Name: {employee.name} | Email: {employee.email} | "
        f"Department: {employee.department} | Salary: {employee.salary:.2f} | Experience: {employee.experience:.1f}"
    )


def select_user(auth_service: AuthService) -> None:
    logger = get_logger()
    username = input("Enter username: ").strip()
    user = auth_service.authenticate(username)
    if not user:
        print("User not found. Please register first.")
        logger.warning("Invalid login attempt for username=%s", username)
        return

    print(f"Authenticated as {user.username} ({user.role})")
    logger.info("User logged in: %s", user.username)
    run_user_menu(user)


def register_user(auth_service: AuthService) -> None:
    logger = get_logger()
    username = input("Register new username: ").strip()
    if auth_service.get_user(username):
        print("User already exists.")
        return
    role = input("Role [admin/hr/employee]: ").strip().lower()
    if role not in {"admin", "hr", "employee"}:
        print("Invalid role.")
        return
    
    employee_id = None
    if role == "employee":
        try:
            employee_id = int(input("Enter your Employee ID: "))
        except ValueError:
            print("Invalid Employee ID.")
            logger.error("Invalid employee ID during registration")
            return
    
    auth_service.register_user(username, role, employee_id=employee_id)
    logger.info("Registered new user: %s role=%s employee_id=%s", username, role, employee_id)
    print("User registered successfully.")


@admin_required
def add_employee(employee_service: EmployeeService, user: object, **kwargs: object) -> None:
    logger = get_logger()
    try:
        employee_id = int(input("Employee ID: "))
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        department = input("Department: ").strip()
        salary = float(input("Salary: "))
        experience = float(input("Experience: "))
    except ValueError:
        print("Invalid input. Employee creation aborted.")
        logger.error("Invalid employee creation input by %s", user.username)
        return

    employee = Employee(
        employee_id=employee_id,
        name=name,
        email=email,
        department=department,
        salary=salary,
        experience=experience,
    )
    try:
        employee_service.add_employee(employee)
        print("Employee added successfully.")
        logger.info("Employee created: %s", employee.to_dict())
    except ValueError as exc:
        print(exc)
        logger.error("Employee add error: %s", exc)


@hr_or_admin_required
def update_employee(employee_service: EmployeeService, user: object, **kwargs: object) -> None:
    logger = get_logger()
    try:
        employee_id = int(input("Employee ID to update: "))
    except ValueError:
        print("Invalid ID.")
        return

    employee = employee_service.get_employee(employee_id)
    if not employee:
        print("Employee not found.")
        return

    updates = {}
    name = input(f"Name [{employee.name}]: ").strip()
    if name:
        updates["name"] = name
    email = input(f"Email [{employee.email}]: ").strip()
    if email:
        updates["email"] = email
    department = input(f"Department [{employee.department}]: ").strip()
    if department:
        updates["department"] = department
    salary = input(f"Salary [{employee.salary}]: ").strip()
    if salary:
        updates["salary"] = float(salary)
    experience = input(f"Experience [{employee.experience}]: ").strip()
    if experience:
        updates["experience"] = float(experience)

    employee_service.update_employee(employee_id, updates)
    print("Employee updated successfully.")
    logger.info("Employee updated by %s: %s", user.username, updates)


@admin_required
def delete_employee(employee_service: EmployeeService, user: object, **kwargs: object) -> None:
    logger = get_logger()
    try:
        employee_id = int(input("Employee ID to delete: "))
    except ValueError:
        print("Invalid ID.")
        return

    if employee_service.delete_employee(employee_id):
        print("Employee deleted successfully.")
        logger.info("Employee deleted by %s: %s", user.username, employee_id)
    else:
        print("Employee not found.")
        logger.warning("Delete failed for employee_id=%s by %s", employee_id, user.username)


@hr_or_admin_required
def view_all_employees(employee_service: EmployeeService, user: object, **kwargs: object) -> None:
    employees = employee_service.list_employees()
    if not employees:
        print("No employees available.")
        return
    for employee in employees:
        print_employee(employee)


@employee_self_or_higher
def view_employee_profile(employee_service: EmployeeService, user: object, employee_id: int, **kwargs: object) -> None:
    employee = employee_service.get_employee(employee_id)
    if not employee:
        print("Employee not found.")
        return
    print_employee(employee)


def view_reports(report_service: ReportService, user: object) -> None:
    summary = report_service.generate_summary()
    print("\n=== Employee Report ===")
    print(f"Total employees: {summary['total_employees']}")
    print("Employees by department:")
    for department, count in summary["department_counts"].items():
        print(f" - {department}: {count}")
    print("Highest salary employee:")
    if summary["highest_salary_employee"]:
        for key, value in summary["highest_salary_employee"].items():
            print(f"   {key}: {value}")
    print("Average salary by department:")
    for department, average in summary["average_salary_by_department"].items():
        print(f" - {department}: {average:.2f}")
    print("Experience statistics:")
    for key, value in summary["experience_statistics"].items():
        print(f" - {key}: {value:.2f}")


def run_user_menu(user: object) -> None:
    employee_service = EmployeeService(DATA_DIR / "employees.json")
    report_service = ReportService(employee_service)

    while True:
        print("\n=== MENU ===")
        if user.role.lower() == "admin":
            print("1. Add employee")
            print("2. Update employee")
            print("3. Delete employee")
            print("4. View all employees")
            print("5. View employee profile")
            print("6. View reports")
            print("7. Logout")
        elif user.role.lower() == "hr":
            print("1. Add employee")
            print("2. Update employee")
            print("3. View all employees")
            print("4. View employee profile")
            print("5. View reports")
            print("6. Logout")
        else:
            print("1. View your profile")
            print("2. Logout")

        choice = input("Choose an option: ").strip()

        try:
            if user.role.lower() == "admin":
                if choice == "1":
                    add_employee(employee_service=employee_service, user=user)
                elif choice == "2":
                    update_employee(employee_service=employee_service, user=user)
                elif choice == "3":
                    delete_employee(employee_service=employee_service, user=user)
                elif choice == "4":
                    view_all_employees(employee_service=employee_service, user=user)
                elif choice == "5":
                    employee_id = int(input("Employee ID to view: "))
                    view_employee_profile(employee_service=employee_service, user=user, employee_id=employee_id)
                elif choice == "6":
                    view_reports(report_service=report_service, user=user)
                elif choice == "7":
                    break
                else:
                    print("Invalid option.")
            elif user.role.lower() == "hr":
                if choice == "1":
                    add_employee(employee_service=employee_service, user=user)
                elif choice == "2":
                    update_employee(employee_service=employee_service, user=user)
                elif choice == "3":
                    view_all_employees(employee_service=employee_service, user=user)
                elif choice == "4":
                    employee_id = int(input("Employee ID to view: "))
                    view_employee_profile(employee_service=employee_service, user=user, employee_id=employee_id)
                elif choice == "5":
                    view_reports(report_service=report_service, user=user)
                elif choice == "6":
                    break
                else:
                    print("Invalid option.")
            else:
                if choice == "1":
                    try:
                        employee_id = int(input("Enter your Employee ID: "))
                        view_employee_profile(employee_service=employee_service, user=user, employee_id=employee_id)
                    except ValueError:
                        print("Invalid ID.")
                elif choice == "2":
                    break
                else:
                    print("Invalid option.")
        except PermissionError as exc:
            print(exc)
            get_logger().warning("Permission denied for %s: %s", user.username, exc)
        except ValueError:
            print("Invalid numeric value.")


def main() -> None:
    configure_logger(LOG_DIR)
    auth_service = AuthService(DATA_DIR / "users.json")
    print("=== Employee Management System ===")
    while True:
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            select_user(auth_service=auth_service)
        elif choice == "2":
            register_user(auth_service=auth_service)
        elif choice == "3":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
