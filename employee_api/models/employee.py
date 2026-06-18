from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass
class Employee:
    employee_id: int
    name: str
    email: str
    department: str
    salary: float
    experience: float

    def __post_init__(self) -> None:
        if self.employee_id <= 0:
            raise ValueError("Employee ID must be greater than 0.")
        if self.salary < 0:
            raise ValueError("Salary must be non-negative.")
        if self.experience < 0:
            raise ValueError("Experience must be non-negative.")
        if "@" not in self.email or "." not in self.email:
            raise ValueError("Email must be valid.")
        if not self.department.strip():
            raise ValueError("Department cannot be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
