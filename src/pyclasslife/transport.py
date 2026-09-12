"""Resilient, authenticated HTTP transport for Classlife."""

from __future__ import annotations

# Standard library
import email.utils
import logging
import math
import random
import time
from datetime import datetime, timezone
from collections.abc import Mapping
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Third party
import requests

# Local
from .authentication import ClasslifeAuthentication
from .exceptions import TransportError
from .logging import ClasslifeLoggerAdapter, get_logger

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_SECONDS = 1.0
MAX_RETRY_DELAY_SECONDS = 60.0
RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
SUPPORTED_METHODS = frozenset(
    {"GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"}
)
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
RETRYABLE_EXCEPTIONS = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
)
SENSITIVE_QUERY_KEYS = frozenset(
    {"apikey", "api_key", "clientid", "client_id", "token", "authorization", "cookie"}
)


class ClasslifeTransport:
    """Centralize authenticated and resilient HTTP requests."""

    def __init__(
        self,
        *,
        authentication: ClasslifeAuthentication,
        timeout: float | tuple[float, float] = (10, 60),
        total_timeout: float | None = 120.0,
        session: requests.Session | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_mutations: bool = False,
        logger: logging.Logger | None = None,
    ) -> None:
        _validate_timeout(timeout=timeout)
        _validate_max_retries(max_retries=max_retries)
        _validate_total_timeout(total_timeout=total_timeout)
        _validate_session(session=session)
        self.authentication = authentication
        self.session = session if session is not None else requests.Session()
        self.timeout, self.total_timeout = timeout, total_timeout
        self.max_retries, self.retry_mutations = max_retries, retry_mutations
        self.logger = ClasslifeLoggerAdapter(
            logger=logger or get_logger(name="transport")
        )

    def request(
        self,
        *,
        method: str,
        url: str,
        backoff: float = DEFAULT_RETRY_BACKOFF_SECONDS,
        total_timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Execute an authenticated request with bounded transient retries."""
        method = _validate_method(method=method)
        _validate_url(url=url)
        _validate_backoff(backoff=backoff)
        operation_timeout = (
            self.total_timeout if total_timeout is None else total_timeout
        )
        _validate_total_timeout(total_timeout=operation_timeout)
        retries = (
            self.max_retries if method in SAFE_METHODS or self.retry_mutations else 0
        )
        safe_url = _safe_url(url=url)
        kwargs = self._prepare_request_kwargs(
            method=method, url=url, safe_url=safe_url, kwargs=kwargs
        )
        started = time.monotonic()
        deadline = None if operation_timeout is None else started + operation_timeout
        if _has_sensitive_query(url=url):
            self.logger.sensitive_query_string(method=method, endpoint=safe_url)
        for attempt in range(1, retries + 2):
            if deadline is not None and time.monotonic() >= deadline:
                _log_operation_finished(
                    logger=self.logger,
                    method=method,
                    endpoint=safe_url,
                    duration_seconds=time.monotonic() - started,
                )
                raise TransportError(f"Total timeout exceeded for {method} {safe_url}")
            attempt_started = time.monotonic()
            kwargs["timeout"] = _remaining_timeout(
                timeout=self.timeout, deadline=deadline
            )
            self.logger.request_started(
                method=method, endpoint=safe_url, attempt=attempt
            )
            try:
                response = self.session.request(method, url, **kwargs)
            except RETRYABLE_EXCEPTIONS as exc:
                duration = time.monotonic() - attempt_started
                self.logger.attempt_finished(
                    method=method,
                    endpoint=safe_url,
                    attempt=attempt,
                    duration_seconds=duration,
                    http_status=None,
                )
                if attempt > retries:
                    _log_operation_finished(
                        logger=self.logger,
                        method=method,
                        endpoint=safe_url,
                        duration_seconds=time.monotonic() - started,
                    )
                    raise TransportError(
                        f"Network error for {method} {safe_url}"
                    ) from exc
                delay = _exponential_jitter(attempt=attempt, backoff=backoff)
                self.logger.retry_scheduled(
                    method=method,
                    endpoint=safe_url,
                    attempt=attempt,
                    http_status=None,
                    retry_delay_seconds=delay,
                )
                try:
                    _sleep_with_deadline(delay=delay, deadline=deadline)
                except TransportError:
                    _log_operation_finished(
                        logger=self.logger,
                        method=method,
                        endpoint=safe_url,
                        duration_seconds=time.monotonic() - started,
                    )
                    raise
                continue
            except requests.exceptions.RequestException as exc:
                self.logger.attempt_finished(
                    method=method,
                    endpoint=safe_url,
                    attempt=attempt,
                    duration_seconds=time.monotonic() - attempt_started,
                    http_status=None,
                )
                _log_operation_finished(
                    logger=self.logger,
                    method=method,
                    endpoint=safe_url,
                    duration_seconds=time.monotonic() - started,
                )
                raise TransportError(f"Network error for {method} {safe_url}") from exc
            self.logger.attempt_finished(
                method=method,
                endpoint=safe_url,
                attempt=attempt,
                duration_seconds=time.monotonic() - attempt_started,
                http_status=response.status_code,
            )
            if 300 <= response.status_code < 400:
                _close_response(response=response)
                _log_operation_finished(
                    logger=self.logger,
                    method=method,
                    endpoint=safe_url,
                    duration_seconds=time.monotonic() - started,
                )
                raise TransportError(
                    "Classlife endpoints are predictable and well-known; "
                    "redirects are suspicious and are not permitted"
                )
            if response.status_code not in RETRYABLE_STATUS_CODES or attempt > retries:
                _log_operation_finished(
                    logger=self.logger,
                    method=method,
                    endpoint=safe_url,
                    duration_seconds=time.monotonic() - started,
                )
                return response
            try:
                delay = _retry_delay(
                    response=response, attempt=attempt, backoff=backoff
                )
            except TransportError:
                _close_response(response=response)
                _log_operation_finished(
                    logger=self.logger,
                    method=method,
                    endpoint=safe_url,
                    duration_seconds=time.monotonic() - started,
                )
                raise
            _close_response(response=response)
            self.logger.retry_scheduled(
                method=method,
                endpoint=safe_url,
                attempt=attempt,
                http_status=response.status_code,
                retry_delay_seconds=delay,
            )
            try:
                _sleep_with_deadline(delay=delay, deadline=deadline)
            except TransportError:
                _log_operation_finished(
                    logger=self.logger,
                    method=method,
                    endpoint=safe_url,
                    duration_seconds=time.monotonic() - started,
                )
                raise
        raise TransportError("Classlife operation finished without a response")

    def _prepare_request_kwargs(
        self, *, method: str, url: str, safe_url: str, kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        supplied_headers = kwargs.pop("headers", {})
        if not isinstance(supplied_headers, Mapping):
            raise ValueError("headers must be a mapping")
        headers = dict(supplied_headers)
        auth_header_names = {"apikey", "clientid"}
        if any(not isinstance(name, str) for name in headers):
            raise ValueError("headers keys must be strings")
        if any(_normalize_key(key=name) in auth_header_names for name in headers):
            self.logger.inappropriate_authentication_headers(
                method=method, endpoint=safe_url
            )
            headers = {
                name: value
                for name, value in headers.items()
                if _normalize_key(key=name) not in auth_header_names
            }
        kwargs["headers"] = {**headers, **self.authentication.headers()}
        if kwargs.get("allow_redirects") is True:
            raise ValueError(
                "allow_redirects=True is not permitted for Classlife requests; "
                "Classlife endpoints are predictable and well-known, so a "
                "redirect is suspicious"
            )
        kwargs["allow_redirects"] = False
        return kwargs


def _validate_method(*, method: str) -> str:
    if (
        not isinstance(method, str)
        or not method.strip()
        or method.strip().upper() not in SUPPORTED_METHODS
    ):
        raise ValueError(f"unsupported HTTP method: {method!r}")
    return method.strip().upper()


def _validate_url(*, url: str) -> None:
    parsed = urlsplit(url) if isinstance(url, str) else None
    if (
        parsed is None
        or parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(
            "url must be an absolute HTTP(S) URL without embedded credentials"
        )


def _validate_timeout(*, timeout: float | tuple[float, float]) -> None:
    if isinstance(timeout, tuple):
        if len(timeout) != 2 or any(
            not _is_finite_positive(value=value) for value in timeout
        ):
            raise ValueError("timeout tuple must contain two positive numbers")
    elif not _is_finite_positive(value=timeout):
        raise ValueError("timeout must be a positive number or a (connect, read) tuple")


def _safe_url(*, url: str) -> str:
    parsed = urlsplit(url)
    query = [
        (k, "[REDACTED]" if _normalize_key(key=k) in SENSITIVE_QUERY_KEYS else v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=True)
    ]
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), ""))


def _has_sensitive_query(*, url: str) -> bool:
    parsed = urlsplit(url)
    return any(
        _normalize_key(key=key) in SENSITIVE_QUERY_KEYS
        for key, _ in parse_qsl(parsed.query, keep_blank_values=True)
    )


def _exponential_jitter(*, attempt: int, backoff: float) -> float:
    return random.uniform(
        0, min(MAX_RETRY_DELAY_SECONDS, backoff * (2 ** (attempt - 1)))
    )


def _retry_delay(*, response: requests.Response, attempt: int, backoff: float) -> float:
    header = response.headers.get("Retry-After")
    if header:
        delay = _parse_retry_after(value=header)
        if delay is not None:
            if delay > MAX_RETRY_DELAY_SECONDS:
                raise TransportError(f"Retry-After is too long: {delay:.0f} seconds")
            return max(0.0, delay)
    return _exponential_jitter(attempt=attempt, backoff=backoff)


def _parse_retry_after(*, value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        pass
    try:
        target = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if target.tzinfo is None:
        target = target.replace(tzinfo=timezone.utc)
    return (target - datetime.now(timezone.utc)).total_seconds()


def _remaining_timeout(
    *, timeout: float | tuple[float, float], deadline: float | None
) -> float | tuple[float, float]:
    if deadline is None:
        return timeout
    remaining = max(0.001, deadline - time.monotonic())
    return (
        (min(timeout[0], remaining), min(timeout[1], remaining))
        if isinstance(timeout, tuple)
        else min(timeout, remaining)
    )


def _sleep_with_deadline(*, delay: float, deadline: float | None) -> None:
    if deadline is None:
        time.sleep(delay)
        return
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TransportError("Total timeout exceeded while retrying")
    time.sleep(min(delay, remaining))


def _log_operation_finished(
    *,
    logger: ClasslifeLoggerAdapter,
    method: str,
    endpoint: str,
    duration_seconds: float,
) -> None:
    logger.operation_finished(
        method=method, endpoint=endpoint, duration_seconds=duration_seconds
    )


def _normalize_key(*, key: str) -> str:
    return key.lower().replace("-", "").replace("_", "")


def _is_finite_positive(*, value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def _validate_max_retries(*, max_retries: object) -> None:
    if (
        not isinstance(max_retries, int)
        or isinstance(max_retries, bool)
        or max_retries < 0
    ):
        raise ValueError("max_retries must be a non-negative integer")


def _validate_total_timeout(*, total_timeout: object) -> None:
    if total_timeout is not None and not _is_finite_positive(value=total_timeout):
        raise ValueError("total_timeout must be a positive finite number or None")


def _validate_backoff(*, backoff: object) -> None:
    if (
        not isinstance(backoff, (int, float))
        or isinstance(backoff, bool)
        or not math.isfinite(backoff)
        or backoff < 0
    ):
        raise ValueError("backoff must be a non-negative finite number")


def _close_response(*, response: requests.Response) -> None:
    """Release a retryable response without masking the retry decision."""
    if getattr(response, "raw", None) is None:
        return
    response.close()


def _validate_session(*, session: object | None) -> None:
    if session is not None and not callable(getattr(session, "request", None)):
        raise ValueError("session must provide a callable request method")
