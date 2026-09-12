"""Role resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class RolesResource(_Resource):
    """Access role endpoints."""

    def list(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="roles", page=page, limit=limit, params=filters)

    def get(self, *, role_id: str) -> Any:
        return self._get(path=f"roles/{role_id}")

    def update(self, *, role_id: str, payload: Mapping[str, Any]) -> Any:
        return self._patch(path=f"roles/{role_id}", payload=payload)

    def list_classrooms(self, *, role_id: str, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(
            path=f"roles/{role_id}/classrooms", page=page, limit=limit, params=filters
        )

    def list_students(self, *, role_id: str, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path=f"roles/{role_id}/students", page=page, limit=limit, params=filters)

    def create(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="roles", payload=payload)

    def delete(self, *, role_id: str) -> Any:
        return self._delete(path=f"roles/{role_id}")
