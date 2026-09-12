"""Enrollment resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class EnrollmentsResource(_Resource):
    """Access enrollment and enrollment-group endpoints."""

    def list_groups(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        """Return one paginated page of enrollment groups."""
        return self._get_page(path="enroll_groups", page=page, limit=limit, params=filters)

    def get_group(self, *, group_id: str) -> Any:
        return self._get(path=f"enroll_groups/{group_id}")

    def list_group_grades(
        self, *, group_id: str, page: int = 1, limit: int = 500, **filters: Any
    ) -> Any:
        return self._get_page(
            path=f"enroll_groups/{group_id}/grades", page=page, limit=limit, params=filters
        )

    def list(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="enrollments", page=page, limit=limit, params=filters)

    def get(self, *, enrollment_id: str) -> Any:
        return self._get(path=f"enrollments/{enrollment_id}")

    def create(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="enrollments", payload=payload)

    def create_for_group(self, *, group_id: str, payload: Mapping[str, Any]) -> Any:
        return self._post(path=f"enroll_groups/{group_id}/enrollments", payload=payload)

    def enroll_student(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="enroll-student", payload=payload)

    def create_draft(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="enrollments/draft", payload=payload)
