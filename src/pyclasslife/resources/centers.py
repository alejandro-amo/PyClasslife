"""Center resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class CentersResource(_Resource):
    """Access center endpoints."""

    def list(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="centers", page=page, limit=limit, params=filters)

    def get(self, *, center_id: str) -> Any:
        return self._get(path=f"centers/{center_id}")

    def update(self, *, center_id: str, payload: Mapping[str, Any]) -> Any:
        return self._patch(path=f"centers/{center_id}", payload=payload)

    def list_students(self, *, center_id: str, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(
            path=f"centers/{center_id}/students", page=page, limit=limit, params=filters
        )

    def create(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="centers", payload=payload)

    def delete(self, *, center_id: str) -> Any:
        return self._delete(path=f"centers/{center_id}")
