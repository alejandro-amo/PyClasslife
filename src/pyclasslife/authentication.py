"""Authentication data and headers for the Classlife API."""

from dataclasses import dataclass, field
from logging import Logger

from .exceptions import ConfigurationError
from .logging import ClasslifeLoggerAdapter, get_logger


@dataclass(frozen=True, slots=True)
class ClasslifeAuthentication:
    """Credentials required by every authenticated Classlife request."""

    api_key: str = field(repr=False)
    client_id: str = field(repr=False)
    logger: ClasslifeLoggerAdapter

    def __init__(
        self, *, api_key: str, client_id: str, logger: Logger | None = None
    ) -> None:
        if not isinstance(api_key, str) or not isinstance(client_id, str):
            raise ConfigurationError("api_key and client_id must be strings")
        normalized_api_key = api_key.strip()
        normalized_client_id = client_id.strip()
        if not normalized_api_key:
            raise ConfigurationError("api_key must not be empty")
        if not normalized_client_id:
            raise ConfigurationError("client_id must not be empty")

        object.__setattr__(self, "api_key", normalized_api_key)
        object.__setattr__(self, "client_id", normalized_client_id)
        object.__setattr__(
            self,
            "logger",
            ClasslifeLoggerAdapter(logger=logger or get_logger(name="authentication")),
        )
        self.logger.debug("Classlife authentication configured")

    def headers(self) -> dict[str, str]:
        """Return authentication headers for one Classlife API request."""

        headers = {
            "apikey": self.api_key,
            "clientId": self.client_id,
        }
        self.logger.debug("Classlife authentication headers prepared")
        return headers
