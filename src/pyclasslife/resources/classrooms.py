"""Classroom resource."""

from __future__ import annotations

from typing import Any, Mapping

from ._base import _Resource


class ClassroomsResource(_Resource):
    """Access classroom endpoints."""

    def list(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="classrooms", page=page, limit=limit, params=filters)

    def get(self, *, classroom_id: str) -> Any:
        return self._get(path=f"classrooms/{classroom_id}")

    def update(self, *, classroom_id: str, payload: Mapping[str, Any]) -> Any:
        return self._patch(path=f"classrooms/{classroom_id}", payload=payload)

    def delete(self, *, classroom_id: str) -> Any:
        return self._delete(path=f"classrooms/{classroom_id}")

    def list_roles(self, *, classroom_id: str, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(
            path=f"classrooms/{classroom_id}/roles", page=page, limit=limit, params=filters
        )

    def list_students(
        self, *, classroom_id: str, page: int = 1, limit: int = 500, **filters: Any
    ) -> Any:
        return self._get_page(
            path=f"classrooms/{classroom_id}/students", page=page, limit=limit, params=filters
        )

    def update_role(
        self, *, classroom_id: str, role_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._put(
            path=f"classrooms/{classroom_id}/roles/{role_id}", payload=payload
        )

    def delete_role(self, *, classroom_id: str, role_id: str) -> Any:
        return self._delete(path=f"classrooms/{classroom_id}/roles/{role_id}")
