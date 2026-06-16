from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class User:
    username: str
    role: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
