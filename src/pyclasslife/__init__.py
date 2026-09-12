"""Public package interface for PyClasslife."""

from .client import ClasslifeClient
from .authentication import ClasslifeAuthentication
from .exceptions import (
    ClasslifeError,
    ConfigurationError,
    FunctionalResponseError,
    HTTPResponseError,
    MalformedResponseError,
    ResponseError,
    TransportError,
)
from ._response_handler import ClasslifeResponse
from .transport import ClasslifeTransport
from .logging import ClasslifeLoggerAdapter, get_logger
from .tools import (
    ClasslifeCredentials,
    get_credentials,
)
from .constants import DEFAULT_BASE_URL
from .pagination import Page, Pagination

__all__ = [
    "ClasslifeAuthentication",
    "ClasslifeClient",
    "ClasslifeTransport",
    "get_logger",
    "ClasslifeLoggerAdapter",
    "ClasslifeCredentials",
    "get_credentials",
    "DEFAULT_BASE_URL",
    "Page",
    "Pagination",
    "ClasslifeError",
    "ConfigurationError",
    "TransportError",
    "ResponseError",
    "HTTPResponseError",
    "FunctionalResponseError",
    "MalformedResponseError",
    "ClasslifeResponse",
]
