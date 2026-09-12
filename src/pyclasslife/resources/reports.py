"""Report resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class ReportsResource(_Resource):
    """Access report endpoints."""

    def list(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="reports", page=page, limit=limit, params=filters)

    def get(self, *, report_id: str) -> Any:
        return self._get(path=f"reports/{report_id}")

    def get_interactive_screen(self, *, params: Mapping[str, Any] | None = None) -> Any:
        return self._get(path="interactivescreen", params=params)
