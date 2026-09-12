"""Academic catalogue resource scaffold."""

from ._base import _Resource
from typing import Any


class AcademicResource(_Resource):
    """Access degrees, areas, cycles, terms, sections and curriculum."""

    def list_degrees(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="degrees", page=page, limit=limit, params=filters)

    def get_degree(self, *, degree_id: str) -> Any:
        return self._get(path=f"degrees/{degree_id}")

    def list_areas(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="areas", page=page, limit=limit, params=filters)

    def get_area(self, *, area_id: str) -> Any:
        return self._get(path=f"areas/{area_id}")

    def list_area_grades(self, *, area_id: str, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path=f"areas/{area_id}/grades", page=page, limit=limit, params=filters)

    def list_cycles(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="cycles", page=page, limit=limit, params=filters)

    def get_cycle(self, *, cycle_id: str) -> Any:
        return self._get(path=f"cycles/{cycle_id}")

    def list_terms(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="terms", page=page, limit=limit, params=filters)

    def get_term(self, *, term_id: str) -> Any:
        return self._get(path=f"terms/{term_id}")

    def list_sections(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="sections", page=page, limit=limit, params=filters)

    def get_section(self, *, section_id: str) -> Any:
        return self._get(path=f"sections/{section_id}")

    def list_curriculum(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="curriculum", page=page, limit=limit, params=filters)
