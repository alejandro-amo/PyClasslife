"""System catalogue resource scaffold."""

from ._base import _Resource
from typing import Any


class CatalogsResource(_Resource):
    """Access languages, schools and picklists."""

    def list_languages(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="languages", page=page, limit=limit, params=filters)

    def get_language(self, *, language_id: str) -> Any:
        return self._get(path=f"languages/{language_id}")

    def list_schools(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="schools", page=page, limit=limit, params=filters)

    def get_school(self, *, school_id: str) -> Any:
        return self._get(path=f"schools/{school_id}")

    def list_picklists(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="picklists", page=page, limit=limit, params=filters)

    def get_picklist(self, *, picklist_id: str) -> Any:
        return self._get(path=f"picklists/{picklist_id}")
