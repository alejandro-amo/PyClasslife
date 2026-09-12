"""Internal, endpoint-agnostic Classlife response interpretation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import requests

from .exceptions import (
    FunctionalResponseError,
    HTTPResponseError,
    MalformedResponseError,
    ResponseError,
)
from .logging import ClasslifeLoggerAdapter, get_logger


@dataclass(frozen=True, slots=True)
class ClasslifeResponse:
    """Validated common response envelope returned by Classlife."""

    status: str | None
    message: str | None
    data: Any = None


class _ResponseHandler:
    """Interpret HTTP and common Classlife response envelopes."""

    def __init__(self, *, logger: logging.Logger | None = None) -> None:
        self.logger = ClasslifeLoggerAdapter(
            logger=logger or get_logger(name="responses")
        )

    def handle(self, *, response: requests.Response) -> ClasslifeResponse:
        """Return the validated response envelope or raise a safe exception."""
        if not isinstance(response, requests.Response):
            raise ResponseError("response must be a requests.Response")
        if not 200 <= response.status_code < 300:
            self.logger.warning(
                "Classlife response rejected",
                extra={
                    "event": "http_response_error",
                    "http_status": response.status_code,
                },
            )
            raise HTTPResponseError(status_code=response.status_code)
        if response.status_code == 204 or not response.content:
            self.logger.debug(
                "Classlife response handled without content",
                extra={
                    "event": "response_handled",
                    "http_status": response.status_code,
                },
            )
            return ClasslifeResponse(status=None, message=None)
        try:
            data = response.json()
        except (ValueError, requests.exceptions.JSONDecodeError) as error:
            self.logger.warning(
                "Classlife response is not valid JSON",
                extra={"event": "invalid_json", "http_status": response.status_code},
            )
            raise ResponseError("Classlife response is not valid JSON") from error
        if not isinstance(data, dict):
            return self._contract_error(
                response=response, detail="response envelope must be a JSON object"
            )
        missing = ["status"] if "status" not in data else []
        if missing:
            return self._contract_error(
                response=response, detail=f"missing field(s): {', '.join(missing)}"
            )
        status = data["status"]
        if not isinstance(status, str) or status.lower() not in {"ok", "ko"}:
            return self._contract_error(
                response=response, detail="field 'status' must be 'ok' or 'ko'"
            )
        if status.lower() == "ko":
            self.logger.warning(
                "Classlife response reports a functional error",
                extra={
                    "event": "functional_error",
                    "http_status": response.status_code,
                },
            )
            raise FunctionalResponseError(
                "Classlife response reports a functional error"
            )
        unexpected_keys = set(data) - {"status", "message", "data"}
        for key in sorted(unexpected_keys):
            self.logger.warning(
                "Classlife response contains an unexpected envelope key",
                extra={
                    "event": "unexpected_response_key",
                    "http_status": response.status_code,
                    "response_key": key,
                },
            )
        if "data" in data and not isinstance(data["data"], (dict, list)):
            return self._contract_error(
                response=response,
                detail="field 'data' must be a JSON object or array when present",
            )
        self.logger.debug(
            "Classlife response handled",
            extra={"event": "response_handled", "http_status": response.status_code},
        )
        message = data.get("message")
        if message is not None and not isinstance(message, str):
            return self._contract_error(
                response=response,
                detail="field 'message' must be a string when present",
            )
        return ClasslifeResponse(
            status=status,
            message=message,
            data=data.get("data"),
        )

    def _contract_error(self, *, response: requests.Response, detail: str) -> Any:
        self.logger.response_contract_violation(
            http_status=response.status_code, detail=detail
        )
        raise MalformedResponseError(detail=detail)
