from unittest.mock import Mock

import pytest

from pyclasslife import ClasslifeClient

GET_FACADE_METHODS = (
    ("students", "get"),
    ("students", "list"),
    ("students", "list_metas"),
    ("students", "list_grades"),
    ("students", "list_enrollments"),
    ("students.roles", "list"),
    ("students.centers", "list"),
    ("teachers", "list"),
    ("teachers", "get"),
    ("teachers", "list_metas"),
    ("academic", "list_degrees"),
    ("academic", "get_degree"),
    ("academic", "list_areas"),
    ("academic", "get_area"),
    ("academic", "list_area_grades"),
    ("academic", "list_cycles"),
    ("academic", "get_cycle"),
    ("academic", "list_terms"),
    ("academic", "get_term"),
    ("academic", "list_sections"),
    ("academic", "get_section"),
    ("academic", "list_curriculum"),
    ("classrooms", "list"),
    ("classrooms", "get"),
    ("classrooms", "list_roles"),
    ("classrooms", "list_students"),
    ("enrollments", "list_groups"),
    ("enrollments", "get_group"),
    ("enrollments", "list_group_grades"),
    ("enrollments", "list"),
    ("enrollments", "get"),
    ("admissions", "get"),
    ("centers", "list"),
    ("centers", "get"),
    ("centers", "list_students"),
    ("roles", "list"),
    ("roles", "get"),
    ("roles", "list_classrooms"),
    ("roles", "list_students"),
    ("users", "list"),
    ("users", "get"),
    ("catalogs", "list_languages"),
    ("catalogs", "get_language"),
    ("catalogs", "list_schools"),
    ("catalogs", "get_school"),
    ("catalogs", "list_picklists"),
    ("catalogs", "get_picklist"),
    ("finance", "list_receipts"),
    ("finance", "get_receipt"),
    ("finance", "list_invoices"),
    ("finance", "get_invoice"),
    ("finance", "list_remittances"),
    ("finance", "get_remittance"),
    ("finance", "list_providers"),
    ("finance", "get_provider"),
    ("finance", "list_provider_teachers"),
    ("finance", "get_provider_teacher"),
    ("finance", "list_provider_metas"),
    ("finance", "list_provider_teacher_metas"),
    ("finance", "list_discounts"),
    ("leads", "list_sources"),
    ("leads", "list_segments"),
    ("leads", "list_commercials"),
    ("leads", "list"),
    ("leads", "get"),
    ("ecommerce", "list_products"),
    ("reports", "list"),
    ("reports", "get"),
    ("reports", "get_interactive_screen"),
    ("drafts", "list"),
    ("drafts", "get"),
)


def _get_nested(value: object, path: str) -> object:
    for part in path.split("."):
        value = getattr(value, part)
    return value


@pytest.mark.parametrize("facade_path, method_name", GET_FACADE_METHODS)
def test_documented_get_is_exposed_by_public_facade(
    facade_path: str, method_name: str
) -> None:
    client = ClasslifeClient(api_key="unit-key", transport=Mock())
    facade = _get_nested(client, facade_path)

    assert callable(getattr(facade, method_name))
