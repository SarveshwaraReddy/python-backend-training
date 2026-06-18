from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from employee_management_system.models.user import User


class AuthService:
    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file
        self.users: Dict[str, User] = {}
        self.load_users()

    def load_users(self) -> None:
        if not self.data_file.exists():
            self.users = {}
            return

        with self.data_file.open("r", encoding="utf-8") as file:
            user_data = json.load(file)
        self.users = {item["username"]: User(**item) for item in user_data}

    def save_users(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump([user.to_dict() for user in self.users.values()], file, indent=4)

    def register_user(
        self,
        username: str,
        role: str,
        password: str,
        employee_id: int | None = None,
    ) -> User:
        if username in self.users:
            raise ValueError(f"User {username} already exists.")
        if not password:
            raise ValueError("Password is required.")

        user = User(username=username, role=role, employee_id=employee_id, password=password)
        self.users[username] = user
        self.save_users()
        return user

    def get_user(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.get_user(username)
        if user and user.check_password(password):
            return user
        return None

    def list_users(self) -> List[User]:
        return list(self.users.values())
