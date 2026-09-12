"""Logging helpers shared by PyClasslife components."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

PACKAGE_LOGGER_NAME = "pyclasslife"


def _package_logger() -> logging.Logger:
    logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    if not any(isinstance(handler, logging.NullHandler) for handler in logger.handlers):
        logger.addHandler(logging.NullHandler())
    return logger


class ClasslifeLoggerAdapter(logging.LoggerAdapter):
    """Small, shared vocabulary for PyClasslife structured log events.

    The wrapped object remains a standard :class:`logging.Logger`, so callers
    can configure handlers and filters using the normal logging facilities.
    """

    def __init__(
        self,
        *,
        logger: logging.Logger,
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(logger, dict(extra or {}))

    def process(self, msg: Any, kwargs: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
        """Merge event fields with adapter context without dropping either."""
        event_extra = dict(kwargs.get("extra") or {})
        event_extra = {**self.extra, **event_extra}
        kwargs["extra"] = event_extra
        return msg, kwargs

    def _debug_event(self, message: str, extra: Mapping[str, Any]) -> None:
        self.log(logging.DEBUG, message, extra={**self.extra, **extra})

    def _warning_event(self, message: str, extra: Mapping[str, Any]) -> None:
        self.log(logging.WARNING, message, extra={**self.extra, **extra})

    def _error_event(self, message: str, extra: Mapping[str, Any]) -> None:
        self.log(logging.ERROR, message, extra={**self.extra, **extra})

    def request_started(self, *, method: str, endpoint: str, attempt: int) -> None:
        self._debug_event(
            "Classlife request started",
            extra={"method": method, "endpoint": endpoint, "attempt": attempt},
        )

    def attempt_finished(
        self,
        *,
        method: str,
        endpoint: str,
        attempt: int,
        duration_seconds: float,
        http_status: int | None,
    ) -> None:
        self._debug_event(
            "Classlife request attempt finished",
            extra={
                "method": method,
                "endpoint": endpoint,
                "attempt": attempt,
                "duration_seconds": duration_seconds,
                "http_status": http_status,
            },
        )

    def retry_scheduled(
        self,
        *,
        method: str,
        endpoint: str,
        attempt: int,
        http_status: int | None,
        retry_delay_seconds: float,
    ) -> None:
        self._warning_event(
            "Classlife request retry scheduled",
            extra={
                "method": method,
                "endpoint": endpoint,
                "attempt": attempt,
                "http_status": http_status,
                "retry_delay_seconds": retry_delay_seconds,
            },
        )

    def operation_finished(
        self, *, method: str, endpoint: str, duration_seconds: float
    ) -> None:
        self._debug_event(
            "Classlife operation finished",
            extra={
                "method": method,
                "endpoint": endpoint,
                "duration_seconds": duration_seconds,
            },
        )

    def sensitive_query_string(self, *, method: str, endpoint: str) -> None:
        self._warning_event(
            "Sensitive query string is not compliant with the Classlife API standard",
            extra={
                "method": method,
                "endpoint": endpoint,
                "event": "sensitive_query_string",
            },
        )

    def inappropriate_authentication_headers(
        self, *, method: str, endpoint: str
    ) -> None:
        self._warning_event(
            "Authentication headers supplied by the consumer are ignored; use ClasslifeAuthentication",
            extra={
                "method": method,
                "endpoint": endpoint,
                "event": "inappropriate_authentication_headers",
            },
        )

    def redirects_blocked(self, *, method: str, endpoint: str) -> None:
        self._warning_event(
            "HTTP redirects are disabled by ClasslifeTransport",
            extra={
                "method": method,
                "endpoint": endpoint,
                "event": "redirects_blocked",
            },
        )

    def response_contract_violation(self, *, http_status: int, detail: str) -> None:
        self._error_event(
            "Classlife response contract violation",
            extra={
                "event": "response_contract_violation",
                "http_status": http_status,
                "detail": detail,
            },
        )


def get_logger(
    *, name: str | None = None, parent: logging.Logger | None = None
) -> logging.Logger:
    """Return a standard-library logger for a PyClasslife component."""
    if parent is not None:
        return parent if name is None else parent.getChild(name)
    package_logger = _package_logger()
    return package_logger if name is None else package_logger.getChild(name)
