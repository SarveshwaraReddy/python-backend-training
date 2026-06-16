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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
