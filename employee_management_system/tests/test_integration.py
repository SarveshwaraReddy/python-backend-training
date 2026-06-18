import tempfile
import unittest
from pathlib import Path

from employee_api.controllers.employee_controller import EmployeeController
from employee_api.services.employee_service import EmployeeService


class TestApiSimulator(unittest.TestCase):
    def test_api_simulator_crud_flow(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            data_file = Path(tmpdirname) / "employees.json"
            service = EmployeeService(data_file)
            controller = EmployeeController(service)

            create_response = controller.create_employee(
                {
                    "employee_id": 201,
                    "name": "Dana",
                    "email": "dana@example.com",
                    "department": "Support",
                    "salary": 45000.0,
                    "experience": 2.5,
                }
            )
            self.assertEqual(create_response["status"], 201)

            get_response = controller.get_employee(201)
            self.assertEqual(get_response["status"], 200)
            self.assertEqual(get_response["data"]["name"], "Dana")

            update_response = controller.update_employee(201, {"salary": 47000.0})
            self.assertEqual(update_response["status"], 200)
            self.assertEqual(update_response["data"]["salary"], 47000.0)

            delete_response = controller.delete_employee(201)
            self.assertEqual(delete_response["status"], 200)

            not_found_response = controller.get_employee(201)
            self.assertEqual(not_found_response["status"], 404)


if __name__ == "__main__":
    unittest.main()
