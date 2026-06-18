from __future__ import annotations

from typing import Any, Dict, List

from employee_api.services.employee_service import EmployeeService


class EmployeeController:
    def __init__(self, service: EmployeeService) -> None:
        self.service = service

    def get_employees(self) -> Dict[str, Any]:
        employees = [employee.to_dict() for employee in self.service.list_employees()]
        return {"status": 200, "data": employees}

    def create_employee(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        employee = self.service.add_employee(employee_data)
        return {"status": 201, "message": "Employee created.", "data": employee.to_dict()}

    def get_employee(self, employee_id: int) -> Dict[str, Any]:
        employee = self.service.get_employee(employee_id)
        if not employee:
            return {"status": 404, "message": "Employee not found."}
        return {"status": 200, "data": employee.to_dict()}

    def update_employee(self, employee_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        employee = self.service.update_employee(employee_id, updates)
        if not employee:
            return {"status": 404, "message": "Employee not found."}
        return {"status": 200, "message": "Employee updated.", "data": employee.to_dict()}

    def delete_employee(self, employee_id: int) -> Dict[str, Any]:
        deleted = self.service.delete_employee(employee_id)
        if not deleted:
            return {"status": 404, "message": "Employee not found."}
        return {"status": 200, "message": "Employee deleted."}
