from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


@dataclass
class User:
    username: str
    role: str
    employee_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
