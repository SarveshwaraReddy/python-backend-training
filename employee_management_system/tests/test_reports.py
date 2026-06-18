import tempfile
import unittest
from pathlib import Path

from employee_management_system.models.employee import Employee
from employee_management_system.services.employee_service import EmployeeService
from employee_management_system.services.report_service import ReportService


class TestReportService(unittest.TestCase):
    def test_report_summary_counts_and_averages(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            data_file = Path(tmpdirname) / "employees.json"
            service = EmployeeService(data_file)
            service.add_employee(
                Employee(
                    employee_id=1,
                    name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                    salary=80000.0,
                    experience=5.0,
                )
            )
            service.add_employee(
                Employee(
                    employee_id=2,
                    name="Bob",
                    email="bob@example.com",
                    department="Engineering",
                    salary=70000.0,
                    experience=4.0,
                )
            )
            service.add_employee(
                Employee(
                    employee_id=3,
                    name="Cathy",
                    email="cathy@example.com",
                    department="HR",
                    salary=60000.0,
                    experience=3.0,
                )
            )

            report_service = ReportService(service)
            summary = report_service.generate_summary()

            self.assertEqual(summary["total_employees"], 3)
            self.assertEqual(summary["department_counts"]["Engineering"], 2)
            self.assertEqual(summary["average_salary_by_department"]["Engineering"], 75000.0)
            self.assertEqual(summary["highest_salary_employee"]["name"], "Alice")


if __name__ == "__main__":
    unittest.main()
