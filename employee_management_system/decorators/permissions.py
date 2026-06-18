from __future__ import annotations

import functools
from typing import Callable, Any

from employee_management_system.models.user import User


def admin_required(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        user: User = kwargs.get("user")
        if not user or user.role.lower() != "admin":
            raise PermissionError("Admin privileges required.")
        return func(*args, **kwargs)

    return wrapper


def hr_or_admin_required(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        user: User = kwargs.get("user")
        if not user or user.role.lower() not in {"admin", "hr"}:
            raise PermissionError("HR or Admin privileges required.")
        return func(*args, **kwargs)

    return wrapper


def employee_self_or_higher(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        user: User = kwargs.get("user")
        employee_id: int = kwargs.get("employee_id")
        if not user:
            raise PermissionError("User authentication required.")
        if user.role.lower() == "employee" and user.employee_id != employee_id:
            raise PermissionError("Employees can view only their own profile.")
        return func(*args, **kwargs)

    return wrapper
