"""Shared implementation for public domain facades."""

from __future__ import annotations

from typing import Any


class _Facade:
    """Public facade delegating operations to one private resource."""

    def __init__(self, *, resource: Any) -> None:
        self._resource = resource

    def __getattr__(self, name: str) -> Any:
        """Delegate only public callable resource operations during migration."""
        if name.startswith("_"):
            raise AttributeError(name)
        candidate = getattr(self._resource, name)
        if not callable(candidate):
            raise AttributeError(
                f"{type(self).__name__!s} does not expose resource attribute {name!r}"
            )
        return candidate

    def _invoke(self, *, name: str, **kwargs: Any) -> Any:
        return getattr(self._resource, name)(**kwargs)

    @staticmethod
    def _payload(**values: Any) -> dict[str, Any]:
        return {key: value for key, value in values.items() if value is not None}
