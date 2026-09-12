"""Shared implementation details for Classlife resources."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from .._response_handler import _ResponseHandler
from ..logging import ClasslifeLoggerAdapter
from ..transport import ClasslifeTransport
from ..pagination import Page, Pagination


class _Resource:
    """Base for resources; HTTP is deliberately delegated to the transport."""

    def __init__(
        self,
        *,
        base_url: str,
        transport: ClasslifeTransport,
        response_handler: _ResponseHandler,
        logger: logging.Logger,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.transport = transport
        self.response_handler = response_handler
        self.logger = ClasslifeLoggerAdapter(logger=logger).logger

    def _post(self, *, path: str, payload: Mapping[str, Any]) -> Any:
        response = self.transport.request(
            method="POST", url=f"{self.base_url}{path.lstrip('/')}", json=payload
        )
        return self.response_handler.handle(response=response)

    def _put(self, *, path: str, payload: Mapping[str, Any]) -> Any:
        response = self.transport.request(
            method="PUT", url=f"{self.base_url}{path.lstrip('/')}", json=payload
        )
        return self.response_handler.handle(response=response)

    def _patch(self, *, path: str, payload: Mapping[str, Any]) -> Any:
        response = self.transport.request(
            method="PATCH", url=f"{self.base_url}{path.lstrip('/')}", json=payload
        )
        return self.response_handler.handle(response=response)

    def _get_page(
        self,
        *,
        path: str,
        page: int = 1,
        limit: int = 500,
        params: Mapping[str, Any] | None = None,
    ) -> Page[Any]:
        pagination = Pagination(page=page, limit=limit)
        query = dict(params or {})
        query.update({"page": pagination.page, "limit": pagination.limit})
        response = self.transport.request(
            method="GET", url=f"{self.base_url}{path.lstrip('/')}", params=query
        )
        envelope = self.response_handler.handle(response=response)
        data = envelope.data
        if not isinstance(data, Mapping):
            raise ValueError("paginated endpoint did not return an object")
        return Page.from_data(data=data)

    def _get(self, *, path: str, params: Mapping[str, Any] | None = None) -> Any:
        """Execute and handle a read-only detail request."""
        kwargs = {} if params is None else {"params": params}
        response = self.transport.request(
            method="GET", url=f"{self.base_url}{path.lstrip('/')}", **kwargs
        )
        return self.response_handler.handle(response=response)

    def _delete(self, *, path: str, payload: Mapping[str, Any] | None = None) -> Any:
        kwargs: dict[str, Any] = {}
        if payload is not None:
            kwargs["json"] = payload
        response = self.transport.request(
            method="DELETE", url=f"{self.base_url}{path.lstrip('/')}", **kwargs
        )
        return self.response_handler.handle(response=response)
