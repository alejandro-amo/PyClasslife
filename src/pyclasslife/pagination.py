"""Shared pagination models for Classlife collection endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any, Generic, Mapping, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Pagination:
    """Validated page request; Classlife pages are one-based."""

    page: int = 1
    limit: int = 500

    def __post_init__(self) -> None:
        if (
            isinstance(self.page, bool)
            or not isinstance(self.page, int)
            or self.page < 1
        ):
            raise ValueError("page must be an integer greater than or equal to 1")
        if (
            isinstance(self.limit, bool)
            or not isinstance(self.limit, int)
            or self.limit < 1
        ):
            raise ValueError("limit must be an integer greater than or equal to 1")


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    """A single Classlife collection page."""

    total: int
    page: int
    limit: int
    count: int
    items: list[T]

    @property
    def total_pages(self) -> int:
        """Return the number of pages implied by ``total`` and ``limit``."""
        return ceil(self.total / self.limit)

    @property
    def has_next(self) -> bool:
        """Whether another page exists after this one."""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Whether a page exists before this one."""
        return self.page > 1 and self.total_pages > 0

    @property
    def next_page(self) -> int | None:
        """Return the next page number, if one exists."""
        return self.page + 1 if self.has_next else None

    @property
    def previous_page(self) -> int | None:
        """Return the previous page number, if one exists."""
        return self.page - 1 if self.has_previous else None

    @classmethod
    def from_data(cls, *, data: Mapping[str, Any]) -> "Page[Any]":
        required = ("total", "page", "limit", "count", "items")
        missing = [name for name in required if name not in data]
        if missing:
            raise ValueError(
                f"paginated response missing field(s): {', '.join(missing)}"
            )
        items = data["items"]
        if not isinstance(items, list):
            raise ValueError("paginated response field 'items' must be an array")
        values = {name: data[name] for name in required if name != "items"}
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in values.values()
        ):
            raise ValueError("pagination metadata must contain non-negative integers")
        return cls(items=items, **values)
