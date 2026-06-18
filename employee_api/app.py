from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from employee_api.controllers.employee_controller import EmployeeController
from employee_api.services.employee_service import EmployeeService


def run_api_simulator() -> None:
    data_file = Path(__file__).resolve().parent / "database" / "employees.json"
    service = EmployeeService(data_file)
    controller = EmployeeController(service)

    while True:
        print("\n=== Employee API Simulator ===")
        print("1. GET /employees")
        print("2. POST /employees")
        print("3. GET /employees/{id}")
        print("4. PUT /employees/{id}")
        print("5. DELETE /employees/{id}")
        print("6. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                response = controller.get_employees()
            elif choice == "2":
                employee_id = int(input("Employee ID: "))
                name = input("Name: ").strip()
                email = input("Email: ").strip()
                department = input("Department: ").strip()
                salary = float(input("Salary: "))
                experience = float(input("Experience: "))
                employee_data = {
                    "employee_id": employee_id,
                    "name": name,
                    "email": email,
                    "department": department,
                    "salary": salary,
                    "experience": experience,
                }
                response = controller.create_employee(employee_data)
            elif choice == "3":
                employee_id = int(input("Employee ID: "))
                response = controller.get_employee(employee_id)
            elif choice == "4":
                employee_id = int(input("Employee ID: "))
                name = input("Name (leave blank to keep current): ").strip()
                email = input("Email (leave blank to keep current): ").strip()
                department = input("Department (leave blank to keep current): ").strip()
                salary_str = input("Salary (leave blank to keep current): ").strip()
                experience_str = input("Experience (leave blank to keep current): ").strip()
                updates: Dict[str, Any] = {}
                if name:
                    updates["name"] = name
                if email:
                    updates["email"] = email
                if department:
                    updates["department"] = department
                if salary_str:
                    updates["salary"] = float(salary_str)
                if experience_str:
                    updates["experience"] = float(experience_str)
                response = controller.update_employee(employee_id, updates)
            elif choice == "5":
                employee_id = int(input("Employee ID: "))
                response = controller.delete_employee(employee_id)
            elif choice == "6":
                break
            else:
                print("Invalid option.")
                continue

            print("\nResponse:")
            print(response)
        except ValueError as exc:
            print(f"Invalid input: {exc}")
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    run_api_simulator()
