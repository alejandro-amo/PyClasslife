"""User resource scaffold."""

from ._base import _Resource
from typing import Any


class UsersResource(_Resource):
    """Access user endpoints."""

    def list(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="users", page=page, limit=limit, params=filters)

    def get(self, *, user_id: str) -> Any:
        return self._get(path=f"users/{user_id}")
