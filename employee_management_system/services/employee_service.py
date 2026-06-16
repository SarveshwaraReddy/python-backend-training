from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Optional

from employee_management_system.models.employee import Employee


class EmployeeService:
    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file
        self.employees: List[Employee] = []
        self.load_employees()

    def load_employees(self) -> None:
        if not self.data_file.exists():
            self.employees = []
            return

        with self.data_file.open("r", encoding="utf-8") as file:
            employee_data = json.load(file)
        self.employees = [Employee(**item) for item in employee_data]

    def save_employees(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump([employee.to_dict() for employee in self.employees], file, indent=4)

    def add_employee(self, employee: Employee) -> None:
        if self.get_employee(employee.employee_id):
            raise ValueError(f"Employee with ID {employee.employee_id} already exists.")
        self.employees.append(employee)
        self.save_employees()

    def update_employee(self, employee_id: int, updates: Dict[str, object]) -> Optional[Employee]:
        employee = self.get_employee(employee_id)
        if not employee:
            return None
        for key, value in updates.items():
            if hasattr(employee, key) and value is not None:
                setattr(employee, key, value)
        self.save_employees()
        return employee

    def delete_employee(self, employee_id: int) -> bool:
        employee = self.get_employee(employee_id)
        if not employee:
            return False
        self.employees.remove(employee)
        self.save_employees()
        return True

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        return next((employee for employee in self.employees if employee.employee_id == employee_id), None)

    def list_employees(self) -> List[Employee]:
        return list(self.employees)

    def filter_by_department(self, department: str) -> List[Employee]:
        return [employee for employee in self.employees if employee.department.lower() == department.lower()]

    def sort_by_salary(self, reverse: bool = False) -> List[Employee]:
        return sorted(self.employees, key=lambda employee: employee.salary, reverse=reverse)

    def get_department_summary(self) -> Dict[str, int]:
        summary: Dict[str, int] = {}
        for employee in self.employees:
            summary[employee.department] = summary.get(employee.department, 0) + 1
        return summary

    def highest_salary_employee(self) -> Optional[Employee]:
        return max(self.employees, key=lambda employee: employee.salary, default=None)

    def average_salary_by_department(self) -> Dict[str, float]:
        totals: Dict[str, float] = {}
        counts: Dict[str, int] = {}
        for employee in self.employees:
            totals[employee.department] = totals.get(employee.department, 0.0) + employee.salary
            counts[employee.department] = counts.get(employee.department, 0) + 1
        return {department: totals[department] / counts[department] for department in totals}

    def experience_statistics(self) -> Dict[str, float]:
        stats: Dict[str, float] = {
            "min_experience": min((employee.experience for employee in self.employees), default=0.0),
            "max_experience": max((employee.experience for employee in self.employees), default=0.0),
            "average_experience": sum((employee.experience for employee in self.employees), 0.0) / max(len(self.employees), 1),
        }
        return stats
