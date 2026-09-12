import logging
from unittest.mock import Mock

import pytest
import requests

from pyclasslife import DEFAULT_BASE_URL
from pyclasslife._response_handler import _ResponseHandler
from pyclasslife.resources.admissions import AdmissionsResource
from pyclasslife.resources.centers import CentersResource
from pyclasslife.resources.contracts import ContractsResource
from pyclasslife.resources.classrooms import ClassroomsResource
from pyclasslife.resources.drafts import DraftsResource
from pyclasslife.resources.ecommerce import EcommerceResource
from pyclasslife.resources.enrollments import EnrollmentsResource
from pyclasslife.resources.finance import FinanceResource
from pyclasslife.resources.leads import LeadsResource
from pyclasslife.resources.roles import RolesResource
from pyclasslife.resources.students import StudentsResource
from pyclasslife.resources.teachers import TeachersResource

CASES = [
    (
        StudentsResource,
        "update",
        {"student_id": "1", "payload": {"name": "x"}},
        "PATCH",
        "students/1",
    ),
    (StudentsResource, "create", {"payload": {"x": 1}}, "POST", "students"),
    (
        StudentsResource,
        "block",
        {"student_id": "1", "payload": {}},
        "POST",
        "students/1/block",
    ),
    (
        StudentsResource,
        "disblock",
        {"student_id": "1", "payload": {}},
        "POST",
        "students/1/disblock",
    ),
    (StudentsResource, "delete", {"payload": {"ids": [1]}}, "DELETE", "students"),
    (TeachersResource, "create", {"payload": {}}, "POST", "teachers"),
    (
        TeachersResource,
        "update",
        {"teacher_id": "1", "payload": {}},
        "PATCH",
        "teachers/1",
    ),
    (TeachersResource, "delete", {"teacher_id": "1"}, "DELETE", "teachers/1"),
    (
        ContractsResource,
        "create",
        {"teacher_id": "1", "payload": {}},
        "POST",
        "teachers/1/contracts",
    ),
    (
        ContractsResource,
        "update",
        {"teacher_id": "1", "contract_id": "2", "payload": {}},
        "PATCH",
        "teachers/1/contracts/2",
    ),
    (
        ClassroomsResource,
        "update",
        {"classroom_id": "1", "payload": {}},
        "PATCH",
        "classrooms/1",
    ),
    (ClassroomsResource, "delete", {"classroom_id": "1"}, "DELETE", "classrooms/1"),
    (
        ClassroomsResource,
        "update_role",
        {"classroom_id": "1", "role_id": "2", "payload": {}},
        "PUT",
        "classrooms/1/roles/2",
    ),
    (
        ClassroomsResource,
        "delete_role",
        {"classroom_id": "1", "role_id": "2"},
        "DELETE",
        "classrooms/1/roles/2",
    ),
    (EnrollmentsResource, "create", {"payload": {}}, "POST", "enrollments"),
    (
        EnrollmentsResource,
        "create_for_group",
        {"group_id": "1", "payload": {}},
        "POST",
        "enroll_groups/1/enrollments",
    ),
    (EnrollmentsResource, "enroll_student", {"payload": {}}, "POST", "enroll-student"),
    (EnrollmentsResource, "create_draft", {"payload": {}}, "POST", "enrollments/draft"),
    (AdmissionsResource, "create", {"payload": {}}, "POST", "admissions"),
    (AdmissionsResource, "create_draft", {"payload": {}}, "POST", "admissions/draft"),
    (
        AdmissionsResource,
        "create_student",
        {"payload": {}},
        "POST",
        "admission-student",
    ),
    (
        AdmissionsResource,
        "create_group_student",
        {"payload": {}},
        "POST",
        "admission-group-student",
    ),
    (AdmissionsResource, "delete", {"payload": {}}, "DELETE", "admissions"),
    (CentersResource, "create", {"payload": {}}, "POST", "centers"),
    (CentersResource, "delete", {"center_id": "1"}, "DELETE", "centers/1"),
    (RolesResource, "create", {"payload": {}}, "POST", "roles"),
    (RolesResource, "delete", {"role_id": "1"}, "DELETE", "roles/1"),
    (FinanceResource, "create_provider", {"payload": {}}, "POST", "providers"),
    (
        FinanceResource,
        "create_provider_teacher",
        {"payload": {}},
        "POST",
        "providers/teachers",
    ),
    (FinanceResource, "delete_provider", {"provider_id": "1"}, "DELETE", "providers/1"),
    (
        FinanceResource,
        "delete_provider_teacher",
        {"teacher_id": "1"},
        "DELETE",
        "providers/teachers/1",
    ),
    (LeadsResource, "create", {"payload": {}}, "POST", "leads"),
    (
        EcommerceResource,
        "create_enrollment",
        {"payload": {}},
        "POST",
        "ecommerce/enrollment",
    ),
    (
        EcommerceResource,
        "create_admission",
        {"payload": {}},
        "POST",
        "ecommerce/admission",
    ),
    (
        DraftsResource,
        "create",
        {"model": "students", "payload": {}},
        "POST",
        "draft/students",
    ),
    (DraftsResource, "create_root", {"payload": {}}, "POST", "draft"),
]


def _resource(resource_type):
    transport = Mock()
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"status":"ok","data":{}}'
    transport.request.return_value = response
    return (
        resource_type(
            base_url=DEFAULT_BASE_URL,
            transport=transport,
            response_handler=_ResponseHandler(),
            logger=logging.getLogger("test"),
        ),
        transport,
    )


@pytest.mark.parametrize("resource_type, method_name, kwargs, http_method, path", CASES)
def test_mutating_resource_methods_delegate_to_transport(
    resource_type, method_name, kwargs, http_method, path
) -> None:
    resource, transport = _resource(resource_type)

    getattr(resource, method_name)(**kwargs)

    expected = {"method": http_method, "url": f"{DEFAULT_BASE_URL}{path}"}
    if "payload" in kwargs:
        expected["json"] = kwargs["payload"]
    transport.request.assert_called_once_with(**expected)
