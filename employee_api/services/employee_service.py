from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from employee_api.models.employee import Employee


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

    def list_employees(self) -> List[Employee]:
        return list(self.employees)

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        return next((employee for employee in self.employees if employee.employee_id == employee_id), None)

    def add_employee(self, employee_data: Dict[str, Any]) -> Employee:
        employee = Employee(**employee_data)
        if self.get_employee(employee.employee_id):
            raise ValueError(f"Employee with ID {employee.employee_id} already exists.")
        self.employees.append(employee)
        self.save_employees()
        return employee

    def update_employee(self, employee_id: int, updates: Dict[str, Any]) -> Optional[Employee]:
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
