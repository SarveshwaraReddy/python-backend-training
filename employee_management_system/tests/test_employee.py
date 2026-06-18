import tempfile
import unittest
from pathlib import Path

from employee_management_system.models.employee import Employee
from employee_management_system.services.employee_service import EmployeeService


class TestEmployeeModule(unittest.TestCase):
    def test_employee_creation_valid(self):
        employee = Employee(
            employee_id=10,
            name="Jane Smith",
            email="jane.smith@example.com",
            department="Engineering",
            salary=60000.0,
            experience=4.0,
        )

        self.assertEqual(employee.employee_id, 10)
        self.assertEqual(employee.name, "Jane Smith")
        self.assertEqual(employee.salary, 60000.0)

    def test_employee_creation_invalid_email(self):
        with self.assertRaises(ValueError) as context:
            Employee(
                employee_id=11,
                name="Sam",
                email="sam-at-example.com",
                department="HR",
                salary=45000.0,
                experience=2.0,
            )
        self.assertIn("Email must be valid", str(context.exception))

    def test_salary_bonus_calculation(self):
        employee = Employee(
            employee_id=12,
            name="Tina",
            email="tina@example.com",
            department="Sales",
            salary=50000.0,
            experience=3.0,
        )

        self.assertEqual(employee.calculate_bonus(0.1), 5000.0)
        self.assertEqual(employee.annual_compensation(0.15), 57500.0)


class TestEmployeeService(unittest.TestCase):
    def test_employee_service_add_and_get(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            data_file = Path(tmpdirname) / "employees.json"
            service = EmployeeService(data_file)

            employee = Employee(
                employee_id=100,
                name="Alice",
                email="alice@example.com",
                department="Finance",
                salary=70000.0,
                experience=5.0,
            )
            service.add_employee(employee)

            loaded = service.get_employee(100)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.name, "Alice")

    def test_employee_service_duplicate_add_raises(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            data_file = Path(tmpdirname) / "employees.json"
            service = EmployeeService(data_file)
            employee = Employee(
                employee_id=101,
                name="Bob",
                email="bob@example.com",
                department="IT",
                salary=55000.0,
                experience=3.0,
            )
            service.add_employee(employee)

            with self.assertRaises(ValueError) as context:
                service.add_employee(employee)
            self.assertIn("already exists", str(context.exception))


if __name__ == "__main__":
    unittest.main()
