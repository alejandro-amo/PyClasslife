"""Status resource for the Classlife API."""

from __future__ import annotations

from typing import Any

from .._response_handler import _ResponseHandler
from ..transport import ClasslifeTransport


class StatusResource:
    """Expose the Classlife service status endpoint."""

    def __init__(
        self,
        *,
        base_url: str,
        transport: ClasslifeTransport,
        response_handler: _ResponseHandler,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.transport = transport
        self.response_handler = response_handler

    def get(self) -> Any:
        """Return validated ``data``, or ``None`` when it is absent."""
        response = self.transport.request(method="GET", url=f"{self.base_url}status")
        return self.response_handler.handle(response=response)
