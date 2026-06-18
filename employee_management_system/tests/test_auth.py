import tempfile
import unittest
from pathlib import Path

from employee_management_system.services.auth_service import AuthService


class TestAuthService(unittest.TestCase):
    def test_register_and_authenticate_user(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            data_file = Path(tmpdirname) / "users.json"
            auth_service = AuthService(data_file)

            user = auth_service.register_user("tester", "employee", "secret", employee_id=20)
            self.assertEqual(user.username, "tester")

            authenticated = auth_service.authenticate("tester", "secret")
            self.assertIsNotNone(authenticated)
            self.assertEqual(authenticated.username, "tester")

    def test_authenticate_with_wrong_password_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            data_file = Path(tmpdirname) / "users.json"
            auth_service = AuthService(data_file)
            auth_service.register_user("tester2", "admin", "supersecret")

            self.assertIsNone(auth_service.authenticate("tester2", "wrongpass"))

    def test_register_existing_user_raises(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            data_file = Path(tmpdirname) / "users.json"
            auth_service = AuthService(data_file)
            auth_service.register_user("tester3", "hr", "pass123")

            with self.assertRaises(ValueError) as context:
                auth_service.register_user("tester3", "hr", "pass123")
            self.assertIn("already exists", str(context.exception))


if __name__ == "__main__":
    unittest.main()
