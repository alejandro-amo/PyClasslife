"""Exceptions exposed by PyClasslife."""


class ClasslifeError(Exception):
    """Base exception for PyClasslife."""


class ConfigurationError(ClasslifeError):
    """Raised when client configuration is invalid."""


class TransportError(ClasslifeError):
    """Raised when the HTTP transport cannot complete a request."""


class ResponseError(ClasslifeError):
    """Raised when a response cannot be interpreted safely."""


class HTTPResponseError(ResponseError):
    """Raised when Classlife returns a non-success HTTP status."""

    def __init__(self, *, status_code: int) -> None:
        super().__init__(f"HTTP response status {status_code}")
        self.status_code = status_code


class FunctionalResponseError(ResponseError):
    """Raised when a successful HTTP response reports ``status=ko``."""


class MalformedResponseError(ResponseError):
    """Raised when a response violates Classlife's common JSON envelope."""

    def __init__(self, *, detail: str) -> None:
        super().__init__(f"Classlife response contract violation: {detail}")
