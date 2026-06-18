from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Employee":
        return cls(**data)

    def calculate_bonus(self, rate: float = 0.1) -> float:
        return self.salary * rate

    def annual_compensation(self, bonus_rate: float = 0.1) -> float:
        return self.salary + self.calculate_bonus(bonus_rate)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
