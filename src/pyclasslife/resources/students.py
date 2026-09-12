"""Student resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class StudentsResource(_Resource):
    """Access student endpoints."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.roles = _StudentRolesResource(**kwargs)
        self.centers = _StudentCentersResource(**kwargs)

    def create(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="students", payload=payload)

    def list(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        """Return one paginated page of students."""
        return self._get_page(path="students", page=page, limit=limit, params=filters)

    def get(self, *, student_id: str) -> Any:
        return self._get(path=f"students/{student_id}")

    def update(self, *, student_id: str, payload: Mapping[str, Any]) -> Any:
        return self._patch(path=f"students/{student_id}", payload=payload)

    def list_metas(self, *, page: int = 1, limit: int = 500) -> Any:
        return self._get(path="students/metas")

    def list_grades(self, *, student_id: str, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(
            path=f"students/{student_id}/grades", page=page, limit=limit, params=filters
        )

    def list_enrollments(
        self, *, student_id: str, page: int = 1, limit: int = 500, **filters: Any
    ) -> Any:
        return self._get_page(
            path=f"students/{student_id}/enrollments", page=page, limit=limit, params=filters
        )

    def block(self, *, student_id: str, payload: Mapping[str, Any]) -> Any:
        return self._post(path=f"students/{student_id}/block", payload=payload)

    def disblock(self, *, student_id: str, payload: Mapping[str, Any]) -> Any:
        return self._post(path=f"students/{student_id}/disblock", payload=payload)

    def delete(self, *, payload: Mapping[str, Any]) -> Any:
        return self._delete(path="students", payload=payload)


class _StudentRolesResource(_Resource):
    """Access roles belonging to a student."""

    def list(self, *, student_id: str, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(
            path=f"students/{student_id}/roles", page=page, limit=limit, params=filters
        )

    def delete(self, *, student_id: str, role_id: str) -> Any:
        return self._delete(path=f"students/{student_id}/roles/{role_id}")

    def update(
        self, *, student_id: str, role_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._put(path=f"students/{student_id}/roles/{role_id}", payload=payload)


class _StudentCentersResource(_Resource):
    """Access centers belonging to a student."""

    def list(self, *, student_id: str, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(
            path=f"students/{student_id}/centers", page=page, limit=limit, params=filters
        )

    def delete(self, *, student_id: str, center_id: str) -> Any:
        return self._delete(path=f"students/{student_id}/centers/{center_id}")

    def update(
        self, *, student_id: str, center_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._put(
            path=f"students/{student_id}/centers/{center_id}", payload=payload
        )
