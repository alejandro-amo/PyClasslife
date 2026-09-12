import pytest
import logging

from pyclasslife import ClasslifeAuthentication, ClasslifeClient, ConfigurationError
from pyclasslife import DEFAULT_BASE_URL


def test_authentication_builds_headers() -> None:
    authentication = ClasslifeAuthentication(
        api_key=" api-key ", client_id=" client-id "
    )
    assert authentication.headers() == {"apikey": "api-key", "clientId": "client-id"}


@pytest.mark.parametrize("field", ["api_key", "client_id"])
def test_authentication_rejects_empty_values(field: str) -> None:
    values = {"api_key": "api-key", "client_id": "client-id"}
    values[field] = "  "
    with pytest.raises(ConfigurationError):
        ClasslifeAuthentication(**values)


def test_client_accepts_keyword_only_configuration() -> None:
    client = ClasslifeClient(api_key="test-key", client_id="test-client")
    assert client.api_key == "test-key"
    assert client.client_id == "test-client"
    assert client.base_url == DEFAULT_BASE_URL
    assert client.status is not None
    assert "test-key" not in repr(client)
    assert "test-client" not in repr(client)
    assert client.base_url in repr(client)


def test_authentication_repr_does_not_expose_credentials() -> None:
    authentication = ClasslifeAuthentication(
        api_key="test-key", client_id="test-client"
    )
    rendered = repr(authentication)
    assert "test-key" not in rendered
    assert "test-client" not in rendered


def test_client_default_logger_is_configurable_package_logger() -> None:
    client = ClasslifeClient(api_key="test-key", client_id="test-client")
    assert client.logger.name == "pyclasslife"
    assert any(
        isinstance(handler, logging.NullHandler) for handler in client.logger.handlers
    )


def test_contracts_are_exposed_as_teacher_subresource() -> None:
    from unittest.mock import Mock

    client = ClasslifeClient(
        api_key="test-key", client_id="test-client", transport=Mock()
    )

    assert client.teachers is not None
    assert client.teachers.contracts is not None
    with pytest.raises(AttributeError):
        _ = client.contracts


def test_logger_adapter_constructor_is_keyword_only() -> None:
    from pyclasslife import ClasslifeLoggerAdapter

    with pytest.raises(TypeError):
        ClasslifeLoggerAdapter(logging.getLogger("test"))  # type: ignore[call-arg]


def test_students_facade_update_maps_response_names_and_omits_none() -> None:
    from unittest.mock import Mock
    from pyclasslife.facades.domains import StudentsFacade

    resource = Mock()
    facade = StudentsFacade(resource=resource)

    facade.update(
        student_id="1",
        student_name="Ada",
        student_email="ada@example.invalid",
        student_phone=None,
    )

    resource.update.assert_called_once_with(
        student_id="1",
        payload={"name": "Ada", "email": "ada@example.invalid"},
    )


def test_students_facade_delete_uses_object_specific_ids() -> None:
    from unittest.mock import Mock
    from pyclasslife.facades.domains import StudentsFacade

    resource = Mock()
    StudentsFacade(resource=resource).delete(student_ids=[1, 2])

    resource.delete.assert_called_once_with(payload={"ids": [1, 2]})


def test_students_facade_delete_accepts_one_student_id() -> None:
    from unittest.mock import Mock
    from pyclasslife.facades.domains import StudentsFacade

    resource = Mock()
    StudentsFacade(resource=resource).delete(student_id=1)

    resource.delete.assert_called_once_with(payload={"ids": [1]})


@pytest.mark.parametrize(
    "kwargs",
    [{}, {"student_id": 1, "student_ids": [2]}],
)
def test_students_facade_delete_requires_exactly_one_id_source(kwargs) -> None:
    from unittest.mock import Mock
    from pyclasslife.facades.domains import StudentsFacade

    with pytest.raises(ValueError, match="exactly one"):
        StudentsFacade(resource=Mock()).delete(**kwargs)


def test_admissions_facade_delete_accepts_one_admission_id() -> None:
    from unittest.mock import Mock
    from pyclasslife.facades.domains import AdmissionsFacade

    resource = Mock()
    AdmissionsFacade(resource=resource).delete(admission_id=1)

    resource.delete.assert_called_once_with(payload={"ids": [1]})


def test_facade_does_not_expose_resource_state() -> None:
    from unittest.mock import Mock
    from pyclasslife.facades.domains import StudentsFacade

    resource = Mock()
    resource.transport = object()
    facade = StudentsFacade(resource=resource)

    with pytest.raises(AttributeError):
        _ = facade.transport


@pytest.mark.parametrize(
    ("field", "value"),
    [("student_name", "x" * 257), ("student_phone", "x" * 129)],
)
def test_students_facade_update_enforces_known_lengths(field: str, value: str) -> None:
    from unittest.mock import Mock
    from pyclasslife.facades.domains import StudentsFacade

    facade = StudentsFacade(resource=Mock())
    with pytest.raises(ValueError):
        facade.update(student_id="1", **{field: value})
