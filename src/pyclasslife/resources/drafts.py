"""Draft resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class DraftsResource(_Resource):
    """Access draft endpoints."""

    def list(self, *, model: str, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(
            path="draft", page=page, limit=limit, params={"model": model, **filters}
        )

    def get(self, *, model: str, object_id: str) -> Any:
        return self._get(path=f"draft/{model}/{object_id}")

    def create(self, *, model: str, payload: Mapping[str, Any]) -> Any:
        return self._post(path=f"draft/{model}", payload=payload)

    def create_root(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="draft", payload=payload)
