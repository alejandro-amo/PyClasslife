import json
from unittest.mock import Mock

import pytest
import requests

from pyclasslife import (
    ClasslifeResponse,
    FunctionalResponseError,
    HTTPResponseError,
    MalformedResponseError,
    ResponseError,
)
from pyclasslife._response_handler import _ResponseHandler


def response(status: int, body: object = None) -> requests.Response:
    result = requests.Response()
    result.status_code = status
    result.reason = "reason"
    if body is not None:
        result._content = json.dumps(body).encode()
        result.headers["Content-Type"] = "application/json"
    return result


def test_handle_returns_json_without_endpoint_rules() -> None:
    assert _ResponseHandler().handle(
        response=response(200, {"status": "ok", "message": "ok", "data": {"value": 1}})
    ) == ClasslifeResponse(status="ok", message="ok", data={"value": 1})


def test_handle_returns_none_for_empty_success() -> None:
    assert _ResponseHandler().handle(response=response(204)) == ClasslifeResponse(
        status=None, message=None
    )


def test_handle_rejects_non_success_http_status_without_body_details() -> None:
    with pytest.raises(HTTPResponseError, match="400") as error:
        _ResponseHandler().handle(response=response(400, {"secret": "value"}))
    assert "secret" not in str(error.value)
    assert error.value.status_code == 400


def test_handle_rejects_invalid_json_without_body_details() -> None:
    result = response(200)
    result._content = b"not-json"
    with pytest.raises(ResponseError, match="not valid JSON"):
        _ResponseHandler().handle(response=result)


def test_handle_rejects_functional_error_without_payload_details() -> None:
    with pytest.raises(FunctionalResponseError):
        _ResponseHandler().handle(
            response=response(
                200, {"status": "ko", "message": "failed", "data": {"secret": "value"}}
            )
        )


def test_handle_requires_requests_response() -> None:
    with pytest.raises(ResponseError):
        _ResponseHandler().handle(response=Mock())


@pytest.mark.parametrize("missing", ["status"])
def test_handle_rejects_missing_contract_field(missing: str) -> None:
    body = {"status": "ok", "message": "ok", "data": {}}
    body.pop(missing)
    with pytest.raises(MalformedResponseError, match=missing):
        _ResponseHandler().handle(response=response(200, body))


def test_handle_rejects_unknown_status() -> None:
    with pytest.raises(MalformedResponseError, match="status"):
        _ResponseHandler().handle(
            response=response(200, {"status": "maybe", "message": "ok", "data": None})
        )


def test_handle_returns_none_when_data_is_absent() -> None:
    payload = {"status": "ok", "message": "service available"}
    assert _ResponseHandler().handle(
        response=response(200, payload)
    ) == ClasslifeResponse(status="ok", message="service available")


def test_handle_accepts_missing_message() -> None:
    payload = {"status": "ok", "data": {"value": 1}}
    assert _ResponseHandler().handle(
        response=response(200, payload)
    ) == ClasslifeResponse(status="ok", message=None, data={"value": 1})


@pytest.mark.parametrize("invalid_data", [None, "value", 1, True])
def test_handle_rejects_invalid_data_container(invalid_data: object) -> None:
    payload = {"status": "ok", "data": invalid_data}
    with pytest.raises(MalformedResponseError, match="data"):
        _ResponseHandler().handle(response=response(200, payload))


@pytest.mark.parametrize("valid_data", [{}, []])
def test_handle_accepts_empty_data_containers(valid_data: object) -> None:
    payload = {"status": "ok", "data": valid_data}
    assert _ResponseHandler().handle(response=response(200, payload)).data == valid_data


def test_handle_warns_for_unexpected_envelope_keys(
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = {"status": "ok", "message": "ok", "unexpected": "secret"}
    assert _ResponseHandler().handle(
        response=response(200, payload)
    ) == ClasslifeResponse(status="ok", message="ok")
    assert "unexpected" in caplog.text
    assert "secret" not in caplog.text
