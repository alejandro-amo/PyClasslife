"""Contract resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class ContractsResource(_Resource):
    """Access teacher contract endpoints."""

    def list_metas(self, *, page: int = 1, limit: int = 500) -> Any:
        return self._get(path="contracts/metas")

    def list(self, *, teacher_id: str, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(
            path=f"teachers/{teacher_id}/contracts", page=page, limit=limit, params=filters
        )

    def get(self, *, teacher_id: str, contract_id: str) -> Any:
        return self._get(path=f"teachers/{teacher_id}/contracts/{contract_id}")

    def update(
        self, *, teacher_id: str, contract_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._patch(
            path=f"teachers/{teacher_id}/contracts/{contract_id}", payload=payload
        )

    def create(self, *, teacher_id: str, payload: Mapping[str, Any]) -> Any:
        return self._post(path=f"teachers/{teacher_id}/contracts", payload=payload)
