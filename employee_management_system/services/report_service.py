from __future__ import annotations

from typing import Dict, Any

from employee_management_system.services.employee_service import EmployeeService


class ReportService:
    def __init__(self, employee_service: EmployeeService) -> None:
        self.employee_service = employee_service

    def generate_summary(self) -> Dict[str, Any]:
        return {
            "total_employees": len(self.employee_service.list_employees()),
            "department_counts": self.employee_service.get_department_summary(),
            "highest_salary_employee": self._employee_to_dict(self.employee_service.highest_salary_employee()),
            "average_salary_by_department": self.employee_service.average_salary_by_department(),
            "experience_statistics": self.employee_service.experience_statistics(),
        }

    @staticmethod
    def _employee_to_dict(employee: "Optional[object]") -> Any:
        if employee is None:
            return None
        return employee.to_dict()
