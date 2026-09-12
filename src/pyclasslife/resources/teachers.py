"""Teacher resource scaffold."""

from ._base import _Resource
from .contracts import ContractsResource
from typing import Any, Mapping


class TeachersResource(_Resource):
    """Access teacher endpoints."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.contracts = ContractsResource(**kwargs)

    def list(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="teachers", page=page, limit=limit, params=filters)

    def get(self, *, teacher_id: str) -> Any:
        return self._get(path=f"teachers/{teacher_id}")

    def update(self, *, teacher_id: str, payload: Mapping[str, Any]) -> Any:
        return self._patch(path=f"teachers/{teacher_id}", payload=payload)

    def list_metas(self, *, page: int = 1, limit: int = 500) -> Any:
        return self._get(path="teachers/metas")

    def create(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="teachers", payload=payload)

    def delete(self, *, teacher_id: str) -> Any:
        return self._delete(path=f"teachers/{teacher_id}")
