"""Admission resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class AdmissionsResource(_Resource):
    """Access admission endpoints."""

    def get(self, *, admission_id: str) -> Any:
        return self._get(path=f"admissions/{admission_id}")

    def create(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="admissions", payload=payload)

    def create_draft(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="admissions/draft", payload=payload)

    def create_student(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="admission-student", payload=payload)

    def create_group_student(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="admission-group-student", payload=payload)

    def delete(self, *, payload: Mapping[str, Any]) -> Any:
        return self._delete(path="admissions", payload=payload)
