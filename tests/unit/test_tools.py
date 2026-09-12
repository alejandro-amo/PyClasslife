import pytest

from pyclasslife import ConfigurationError, get_credentials


def test_get_credentials_env_returns_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLASSLIFE_API_KEY", " api-key ")
    monkeypatch.setenv("CLASSLIFE_CLIENT_ID", " client-id ")

    credentials = get_credentials(source="env_vars")

    assert credentials.api_key == "api-key"
    assert credentials.client_id == "client-id"
    assert "api-key" not in repr(credentials)
    assert "client-id" not in repr(credentials)


@pytest.mark.parametrize(
    "missing",
    ["CLASSLIFE_API_KEY", "CLASSLIFE_CLIENT_ID", "both"],
)
def test_get_credentials_env_reports_missing_variables(
    monkeypatch: pytest.MonkeyPatch, missing: str
) -> None:
    monkeypatch.delenv("CLASSLIFE_API_KEY", raising=False)
    monkeypatch.delenv("CLASSLIFE_CLIENT_ID", raising=False)
    if missing != "both":
        monkeypatch.setenv(missing, "available")

    with pytest.raises(ConfigurationError) as error:
        get_credentials(source="env_vars")

    message = str(error.value)
    assert (
        "CLASSLIFE_API_KEY" in message
        if missing != "CLASSLIFE_API_KEY"
        else "CLASSLIFE_API_KEY" not in message
    )
    assert (
        "CLASSLIFE_CLIENT_ID" in message
        if missing != "CLASSLIFE_CLIENT_ID"
        else "CLASSLIFE_CLIENT_ID" not in message
    )
    assert "available" not in message


def test_get_credentials_from_env_file(tmp_path) -> None:
    path = tmp_path / ".env-test.local"
    path.write_text(
        "CLASSLIFE_API_KEY=api-key\nCLASSLIFE_CLIENT_ID='client-id'\n",
        encoding="utf-8",
    )
    credentials = get_credentials(source="env_file", env_file=path)
    assert credentials.api_key == "api-key"
    assert credentials.client_id == "client-id"


def test_get_credentials_rejects_invalid_source_or_missing_env_file() -> None:
    with pytest.raises(ConfigurationError):
        get_credentials(source="other")
    with pytest.raises(ConfigurationError):
        get_credentials(source="env_file")


def test_get_credentials_file_reports_each_missing_credential(tmp_path) -> None:
    path = tmp_path / ".env-test.local"
    path.write_text("CLASSLIFE_API_KEY=api-key\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="CLASSLIFE_CLIENT_ID"):
        get_credentials(source="env_file", env_file=path)
