"""Lead resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class LeadsResource(_Resource):
    """Access lead endpoints."""

    def list_sources(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="leads_sources", page=page, limit=limit, params=filters)

    def list_segments(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="leads_segments", page=page, limit=limit, params=filters)

    def list_commercials(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="leads_commercials", page=page, limit=limit, params=filters)

    def list(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="leads", page=page, limit=limit, params=filters)

    def get(self, *, lead_id: str) -> Any:
        return self._get(path=f"leads/{lead_id}")

    def create(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="leads", payload=payload)
