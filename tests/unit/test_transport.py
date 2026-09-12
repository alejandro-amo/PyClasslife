from unittest.mock import Mock, patch
import pytest
import requests
from pyclasslife import ClasslifeAuthentication, ClasslifeTransport, TransportError


def response(status: int, headers: dict[str, str] | None = None) -> requests.Response:
    result = requests.Response()
    result.status_code = status
    result.headers.update(headers or {})
    return result


def make_transport(session: Mock, **kwargs: object) -> ClasslifeTransport:
    auth = ClasslifeAuthentication(api_key="secret-key", client_id="secret-client")
    return ClasslifeTransport(authentication=auth, session=session, **kwargs)


def test_429_retry_after_and_without_retry_after() -> None:
    session = Mock()
    session.request.side_effect = [
        response(429, {"Retry-After": "3"}),
        response(429),
        response(200),
    ]
    with (
        patch("pyclasslife.transport.time.sleep") as sleep,
        patch("pyclasslife.transport.random.uniform", return_value=0.25) as jitter,
    ):
        result = make_transport(session).request(
            method="GET", url="https://example.test/status"
        )
    assert result.status_code == 200
    sleep.assert_any_call(3.0)
    jitter.assert_called_once_with(0, 2.0)


def test_mutation_429_is_not_retried_unless_enabled() -> None:
    session = Mock()
    session.request.return_value = response(429)
    assert (
        make_transport(session)
        .request(method="POST", url="https://example.test/status")
        .status_code
        == 429
    )
    session.reset_mock()
    session.request.side_effect = [response(429), response(200)]
    with patch("pyclasslife.transport.time.sleep"):
        assert (
            make_transport(session, retry_mutations=True)
            .request(method="POST", url="https://example.test/status")
            .status_code
            == 200
        )


@pytest.mark.parametrize("status", [500, 502, 503, 504])
def test_server_errors_retry_for_safe_methods(status: int) -> None:
    session = Mock()
    session.request.side_effect = [response(status), response(200)]
    with patch("pyclasslife.transport.time.sleep"):
        assert (
            make_transport(session)
            .request(method="GET", url="https://example.test/status")
            .status_code
            == 200
        )


def test_total_timeout_is_overridable_and_limits_retry_sleep() -> None:
    session = Mock()
    session.request.return_value = response(503)
    clock = iter([0, 0, 0, 0, 2, 2, 2, 2, 2, 2])
    with (
        patch("pyclasslife.transport.time.sleep") as sleep,
        patch("pyclasslife.transport.time.monotonic", side_effect=lambda: next(clock)),
    ):
        with pytest.raises(TransportError):
            make_transport(session).request(
                method="GET", url="https://example.test/status", total_timeout=1
            )
    sleep.assert_not_called()


def test_remaining_timeout_is_forwarded_on_each_attempt() -> None:
    session = Mock()
    session.request.side_effect = [response(503), response(200)]
    with (
        patch("pyclasslife.transport.time.sleep"),
        patch("pyclasslife.transport.time.monotonic", return_value=0),
    ):
        make_transport(session, timeout=(10, 60), total_timeout=5).request(
            method="GET", url="https://example.test/status"
        )
    assert all(
        isinstance(call.kwargs["timeout"], tuple)
        for call in session.request.call_args_list
    )


@pytest.mark.parametrize("method", ["", "TRACE", "CONNECT"])
def test_invalid_method_is_rejected(method: str) -> None:
    session = Mock()
    with pytest.raises(ValueError):
        make_transport(session).request(
            method=method, url="https://example.test/status"
        )
    session.request.assert_not_called()


@pytest.mark.parametrize(
    "url",
    [
        "",
        "/status",
        "ftp://example.test/status",
        "https:///status",
        "https://u:p@example.test/status",
    ],
)
def test_invalid_url_is_rejected(url: str) -> None:
    session = Mock()
    with pytest.raises(ValueError):
        make_transport(session).request(method="GET", url=url)
    session.request.assert_not_called()


@pytest.mark.parametrize(
    "timeout", [0, -1, (1,), (1, 0), ("1", 2), True, float("nan"), float("inf")]
)
def test_invalid_timeout_is_rejected(timeout: object) -> None:
    with pytest.raises(ValueError):
        make_transport(Mock(), timeout=timeout)


def test_invalid_session_is_rejected() -> None:
    with pytest.raises(ValueError, match="session"):
        ClasslifeTransport(
            authentication=ClasslifeAuthentication(api_key="key", client_id="client"),
            session=object(),
        )


def test_allow_redirects_cannot_be_enabled() -> None:
    session = Mock()
    with pytest.raises(ValueError, match="redirect"):
        make_transport(session).request(
            method="GET", url="https://example.test/status", allow_redirects=True
        )
    session.request.assert_not_called()


def test_server_redirect_is_rejected_with_clear_error() -> None:
    session = Mock()
    session.request.return_value = response(302)
    with pytest.raises(TransportError, match="redirects are suspicious"):
        make_transport(session).request(method="GET", url="https://example.test/status")


def test_retryable_response_is_closed_before_retry() -> None:
    first = response(503)
    first.raw = Mock()
    session = Mock()
    session.request.side_effect = [first, response(200)]
    with patch("pyclasslife.transport.time.sleep"):
        make_transport(session).request(method="GET", url="https://example.test/status")
    first.raw.close.assert_called_once_with()


def test_consumer_authentication_headers_are_ignored_and_warned() -> None:
    session = Mock()
    session.request.return_value = response(200)
    logger = Mock()
    make_transport(session, logger=logger).request(
        method="GET",
        url="https://example.test/status",
        headers={"apikey": "wrong", "Client-ID": "wrong", "X-Test": "ok"},
    )
    sent = session.request.call_args.kwargs["headers"]
    assert sent["apikey"] == "secret-key" and sent["clientId"] == "secret-client"
    assert sent["X-Test"] == "ok"
    assert any(
        call.kwargs["extra"]["event"] == "inappropriate_authentication_headers"
        for call in logger.log.call_args_list
    )


def test_network_retry_is_logged() -> None:
    session = Mock()
    session.request.side_effect = [requests.exceptions.ConnectionError(), response(200)]
    logger = Mock()
    with patch("pyclasslife.transport.time.sleep"):
        assert (
            make_transport(session, logger=logger)
            .request(method="GET", url="https://example.test/status")
            .status_code
            == 200
        )
    assert any(
        call.kwargs["extra"].get("http_status") is None
        for call in logger.log.call_args_list
    )


@pytest.mark.parametrize("value", [True, 1.5, -1, "3"])
def test_invalid_max_retries_is_rejected(value: object) -> None:
    with pytest.raises(ValueError):
        make_transport(Mock(), max_retries=value)


@pytest.mark.parametrize("value", [0, -1, True, float("nan"), float("inf"), "3"])
def test_invalid_total_timeout_is_rejected(value: object) -> None:
    with pytest.raises(ValueError):
        make_transport(Mock(), total_timeout=value)


@pytest.mark.parametrize("value", [-1, True, float("nan"), float("inf"), "1"])
def test_invalid_backoff_is_rejected(value: object) -> None:
    with pytest.raises(ValueError):
        make_transport(Mock()).request(
            method="GET", url="https://example.test/status", backoff=value
        )


def test_logging_is_structured_and_redacted() -> None:
    session = Mock()
    session.request.return_value = response(200)
    logger = Mock()
    make_transport(session, logger=logger).request(
        method="GET",
        url="https://example.test/status?apikey=secret-key&clientId=secret-client",
    )
    calls = logger.log.call_args_list
    rendered = repr(calls)
    assert "secret-key" not in rendered and "secret-client" not in rendered
    debug_extras = [
        call.kwargs["extra"] for call in logger.log.call_args_list if call.args[0] == 10
    ]
    assert any(
        {"method", "endpoint", "attempt"} <= extra.keys() for extra in debug_extras
    )
    assert any(
        {"method", "endpoint", "attempt", "duration_seconds", "http_status"}
        <= extra.keys()
        for extra in debug_extras
    )
    assert any(
        {"method", "endpoint", "duration_seconds"} <= extra.keys()
        for extra in debug_extras
    )


def test_total_timeout_during_retry_sleep_logs_operation_duration() -> None:
    session = Mock()
    session.request.return_value = response(503)
    logger = Mock()
    clock = iter([0, 0, 0, 0, 2, 2, 2, 2, 2, 2])
    with (
        patch("pyclasslife.transport.time.sleep"),
        patch("pyclasslife.transport.time.monotonic", side_effect=lambda: next(clock)),
    ):
        with pytest.raises(TransportError):
            make_transport(session, logger=logger).request(
                method="GET", url="https://example.test/status", total_timeout=1
            )
    assert any(
        call.args[1] == "Classlife operation finished"
        and "duration_seconds" in call.kwargs["extra"]
        for call in logger.log.call_args_list
    )


def test_sensitive_query_string_is_redacted_and_warned() -> None:
    session = Mock()
    session.request.return_value = response(200)
    logger = Mock()
    make_transport(session, logger=logger).request(
        method="GET", url="https://example.test/status?page=1&apikey=secret-key"
    )
    assert "secret-key" not in repr(logger.log.call_args_list)
    assert any(
        call.kwargs.get("extra", {}).get("event") == "sensitive_query_string"
        for call in logger.log.call_args_list
    )


def test_default_request_does_not_warn_about_redirects() -> None:
    session = Mock()
    session.request.return_value = response(200)
    logger = Mock()
    make_transport(session, logger=logger).request(
        method="GET", url="https://example.test/status"
    )
    assert not any(
        call.kwargs.get("extra", {}).get("event") == "redirects_blocked"
        for call in logger.log.call_args_list
    )


def test_non_string_header_name_is_rejected() -> None:
    with pytest.raises(ValueError, match="keys"):
        make_transport(Mock()).request(
            method="GET", url="https://example.test/status", headers={1: "value"}
        )
