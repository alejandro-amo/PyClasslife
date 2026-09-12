import logging
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from pyclasslife import DEFAULT_BASE_URL
from pyclasslife._response_handler import _ResponseHandler
from pyclasslife.resources.academic import AcademicResource
from pyclasslife.resources.admissions import AdmissionsResource
from pyclasslife.resources.catalogs import CatalogsResource
from pyclasslife.resources.centers import CentersResource
from pyclasslife.resources.classrooms import ClassroomsResource
from pyclasslife.resources.contracts import ContractsResource
from pyclasslife.resources.drafts import DraftsResource
from pyclasslife.resources.ecommerce import EcommerceResource
from pyclasslife.resources.enrollments import EnrollmentsResource
from pyclasslife.resources.finance import FinanceResource
from pyclasslife.resources.leads import LeadsResource
from pyclasslife.resources.reports import ReportsResource
from pyclasslife.resources.roles import RolesResource
from pyclasslife.resources.students import StudentsResource
from pyclasslife.resources.teachers import TeachersResource
from pyclasslife.resources.users import UsersResource


def _resource(resource_type):
    transport = Mock()
    response = requests.Response()
    response.status_code = 200
    fixture_path = Path(__file__).parents[1] / "fixtures" / "responses" / "details.json"
    detail = json.loads(fixture_path.read_text(encoding="utf-8"))["generic"]
    response._content = json.dumps({"status": "ok", "data": detail}).encode()
    transport.request.return_value = response
    resource = resource_type(
        base_url=DEFAULT_BASE_URL,
        transport=transport,
        response_handler=_ResponseHandler(),
        logger=logging.getLogger("test"),
    )
    return resource, transport


def _page_response(transport, path):
    fixture_path = (
        Path(__file__).parents[1] / "fixtures" / "responses" / "paginated.json"
    )
    fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))
    sample = fixtures.get(path, fixtures["generic"])
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps({"status": "ok", "data": sample}).encode()
    transport.request.return_value = response


PAGED_CASES = [
    (AcademicResource, "list_degrees", {}, "degrees"),
    (AcademicResource, "list_areas", {}, "areas"),
    (AcademicResource, "list_area_grades", {"area_id": "1"}, "areas/1/grades"),
    (AcademicResource, "list_cycles", {}, "cycles"),
    (AcademicResource, "list_terms", {}, "terms"),
    (AcademicResource, "list_sections", {}, "sections"),
    (AcademicResource, "list_curriculum", {}, "curriculum"),
    (CatalogsResource, "list_languages", {}, "languages"),
    (CatalogsResource, "list_schools", {}, "schools"),
    (CatalogsResource, "list_picklists", {}, "picklists"),
    (ClassroomsResource, "list", {}, "classrooms"),
    (ClassroomsResource, "list_roles", {"classroom_id": "1"}, "classrooms/1/roles"),
    (
        ClassroomsResource,
        "list_students",
        {"classroom_id": "1"},
        "classrooms/1/students",
    ),
    (CentersResource, "list", {}, "centers"),
    (CentersResource, "list_students", {"center_id": "1"}, "centers/1/students"),
    (ContractsResource, "list", {"teacher_id": "1"}, "teachers/1/contracts"),
    (EnrollmentsResource, "list_groups", {}, "enroll_groups"),
    (
        EnrollmentsResource,
        "list_group_grades",
        {"group_id": "1"},
        "enroll_groups/1/grades",
    ),
    (EnrollmentsResource, "list", {}, "enrollments"),
    (FinanceResource, "list_receipts", {}, "receipts"),
    (FinanceResource, "list_invoices", {}, "invoices"),
    (FinanceResource, "list_remittances", {}, "remittances"),
    (FinanceResource, "list_providers", {}, "providers"),
    (FinanceResource, "list_provider_teachers", {}, "providers/teachers"),
    (FinanceResource, "list_discounts", {}, "finance/discounts"),
    (LeadsResource, "list_sources", {}, "leads_sources"),
    (LeadsResource, "list_segments", {}, "leads_segments"),
    (LeadsResource, "list_commercials", {}, "leads_commercials"),
    (LeadsResource, "list", {}, "leads"),
    (EcommerceResource, "list_products", {}, "ecommerce/products"),
    (ReportsResource, "list", {}, "reports"),
    (DraftsResource, "list", {"model": "students"}, "draft"),
    (RolesResource, "list", {}, "roles"),
    (RolesResource, "list_classrooms", {"role_id": "1"}, "roles/1/classrooms"),
    (RolesResource, "list_students", {"role_id": "1"}, "roles/1/students"),
    (StudentsResource, "list", {}, "students"),
    (StudentsResource, "list_grades", {"student_id": "1"}, "students/1/grades"),
    (
        StudentsResource,
        "list_enrollments",
        {"student_id": "1"},
        "students/1/enrollments",
    ),
    (TeachersResource, "list", {}, "teachers"),
]


@pytest.mark.parametrize("resource_type, method_name, ids, path", PAGED_CASES)
def test_paginated_get_resource_methods_delegate_to_transport(
    resource_type, method_name, ids, path
) -> None:
    resource, transport = _resource(resource_type)
    _page_response(transport, path)

    getattr(resource, method_name)(**ids)

    expected_params = {"page": 1, "limit": 500}
    if method_name == "list":
        expected_params.update({})
    if method_name == "list" and resource_type is DraftsResource:
        expected_params["model"] = "students"
    transport.request.assert_called_once_with(
        method="GET", url=f"{DEFAULT_BASE_URL}{path}", params=expected_params
    )


DETAIL_CASES = [
    (AdmissionsResource, "get", {"admission_id": "1"}, "admissions/1"),
    (AcademicResource, "get_degree", {"degree_id": "1"}, "degrees/1"),
    (AcademicResource, "get_area", {"area_id": "1"}, "areas/1"),
    (AcademicResource, "get_cycle", {"cycle_id": "1"}, "cycles/1"),
    (AcademicResource, "get_term", {"term_id": "1"}, "terms/1"),
    (AcademicResource, "get_section", {"section_id": "1"}, "sections/1"),
    (CatalogsResource, "get_language", {"language_id": "1"}, "languages/1"),
    (CatalogsResource, "get_school", {"school_id": "1"}, "schools/1"),
    (CatalogsResource, "get_picklist", {"picklist_id": "1"}, "picklists/1"),
    (ClassroomsResource, "get", {"classroom_id": "1"}, "classrooms/1"),
    (CentersResource, "get", {"center_id": "1"}, "centers/1"),
    (
        ContractsResource,
        "get",
        {"teacher_id": "1", "contract_id": "2"},
        "teachers/1/contracts/2",
    ),
    (EnrollmentsResource, "get_group", {"group_id": "1"}, "enroll_groups/1"),
    (EnrollmentsResource, "get", {"enrollment_id": "1"}, "enrollments/1"),
    (FinanceResource, "get_receipt", {"receipt_id": "1"}, "receipts/1"),
    (FinanceResource, "get_invoice", {"invoice_id": "1"}, "invoices/1"),
    (FinanceResource, "get_remittance", {"remittance_id": "1"}, "remittances/1"),
    (FinanceResource, "get_provider", {"provider_id": "1"}, "providers/1"),
    (
        FinanceResource,
        "get_provider_teacher",
        {"teacher_id": "1"},
        "providers/teachers/1",
    ),
    (LeadsResource, "get", {"lead_id": "1"}, "leads/1"),
    (ReportsResource, "get", {"report_id": "1"}, "reports/1"),
    (
        DraftsResource,
        "get",
        {"model": "students", "object_id": "1"},
        "draft/students/1",
    ),
    (RolesResource, "get", {"role_id": "1"}, "roles/1"),
    (StudentsResource, "get", {"student_id": "1"}, "students/1"),
    (StudentsResource, "list_metas", {}, "students/metas"),
    (TeachersResource, "get", {"teacher_id": "1"}, "teachers/1"),
    (TeachersResource, "list_metas", {}, "teachers/metas"),
    (ContractsResource, "list_metas", {}, "contracts/metas"),
    (FinanceResource, "list_provider_metas", {}, "providers/metas"),
    (FinanceResource, "list_provider_teacher_metas", {}, "providers/teachers/metas"),
    (UsersResource, "get", {"user_id": "1"}, "users/1"),
    (ReportsResource, "get_interactive_screen", {}, "interactivescreen"),
]


@pytest.mark.parametrize("resource_type, method_name, ids, path", DETAIL_CASES)
def test_detail_get_resource_methods_delegate_to_transport(
    resource_type, method_name, ids, path
) -> None:
    resource, transport = _resource(resource_type)

    getattr(resource, method_name)(**ids)

    transport.request.assert_called_once_with(
        method="GET", url=f"{DEFAULT_BASE_URL}{path}"
    )


def test_student_subresource_get_lists_delegate_to_transport() -> None:
    resource, transport = _resource(StudentsResource)
    _page_response(transport, "students")

    resource.roles.list(student_id="1")
    resource.centers.list(student_id="1")

    assert transport.request.call_count == 2
    assert transport.request.call_args_list[0].args == ()
    assert transport.request.call_args_list[0].kwargs["url"] == (
        f"{DEFAULT_BASE_URL}students/1/roles"
    )
    assert transport.request.call_args_list[1].kwargs["url"] == (
        f"{DEFAULT_BASE_URL}students/1/centers"
    )
