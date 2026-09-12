"""Domain facade scaffolding corresponding to the private resources."""

from __future__ import annotations

from typing import Any, Mapping

from ._base import _Facade


class StatusFacade(_Facade):
    """Public facade for service status."""


class StudentsFacade(_Facade):
    """Public facade for students and their subresources."""

    def __init__(self, *, resource: Any) -> None:
        super().__init__(resource=resource)
        self.roles = _Facade(resource=resource.roles)
        self.centers = _Facade(resource=resource.centers)

    def create(
        self,
        *,
        email: str,
        name: str,
        lastname: str,
        lastnameend: str | None = None,
        uid: str | None = None,
        phone: str | None = None,
        school_id: int | None = None,
        language_code: str | None = None,
        meta_fields: Mapping[str, Any] | None = None,
    ) -> Any:
        """Create a student; ``email``, ``name`` and ``lastname`` are required."""
        return self._invoke(
            name="create",
            payload=self._payload(
                email=email,
                name=name,
                lastname=lastname,
                lastnameend=lastnameend,
                uid=uid,
                phone=phone,
                school_id=school_id,
                language_code=language_code,
                **({"metas": dict(meta_fields)} if meta_fields is not None else {}),
            ),
        )

    def list(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        """Return one page of students; ``page`` starts at 1 and defaults to 500 items."""
        return self._invoke(name="list", page=page, limit=limit, **filters)

    def update(
        self,
        *,
        student_id: str,
        student_name: str | None = None,
        student_lastname: str | None = None,
        student_lastnameend: str | None = None,
        student_email: str | None = None,
        student_uid: str | None = None,
        student_phone: str | None = None,
        school_id: int | None = None,
        language_code: str | None = None,
        meta_fields: Mapping[str, Any] | None = None,
    ) -> Any:
        """Update documented student fields using response-oriented names."""
        values = {
            "name": student_name,
            "lastname": student_lastname,
            "lastnameend": student_lastnameend,
            "email": student_email,
            "uid": student_uid,
            "phone": student_phone,
            "school_id": school_id,
            "language_code": language_code,
        }
        if (
            not any(value is not None for value in values.values())
            and meta_fields is None
        ):
            raise ValueError("student update requires at least one field")
        _validate_student_update(values=values)
        payload = self._payload(**values)
        if meta_fields is not None:
            payload["metas"] = dict(meta_fields)
        return self._invoke(
            name="update",
            student_id=student_id,
            payload=payload,
        )

    def delete(
        self,
        *,
        student_id: int | str | None = None,
        student_ids: list[int | str] | None = None,
    ) -> Any:
        """Delete one student or the students in ``student_ids``."""
        ids = _one_or_many(
            singular_name="student_id",
            singular=student_id,
            plural_name="student_ids",
            plural=student_ids,
        )
        return self._invoke(name="delete", payload={"ids": ids})

    def block(self, *, student_id: str, **fields: Any) -> Any:
        """Block a student (fields inferred, not tested)."""
        return self._invoke(
            name="block", student_id=student_id, payload=self._payload(**fields)
        )

    def disblock(self, *, student_id: str, **fields: Any) -> Any:
        """Unblock a student (fields inferred, not tested)."""
        return self._invoke(
            name="disblock",
            student_id=student_id,
            payload=self._payload(**fields),
        )


class TeachersFacade(_Facade):
    """Public facade for teachers."""

    def __init__(self, *, resource: Any) -> None:
        super().__init__(resource=resource)
        self.contracts = ContractsFacade(resource=resource.contracts)

    def create(
        self,
        *,
        email: str,
        name: str,
        lastname: str,
        lastnameend: str | None = None,
        uid: str | None = None,
        phone: str | None = None,
        school_id: int | None = None,
        language_code: str | None = None,
        meta_fields: Mapping[str, Any] | None = None,
    ) -> Any:
        """Create a teacher; the three identity fields are required by example."""
        return self._invoke(
            name="create",
            payload=self._payload(
                email=email,
                name=name,
                lastname=lastname,
                lastnameend=lastnameend,
                uid=uid,
                phone=phone,
                school_id=school_id,
                language_code=language_code,
                **({"metas": dict(meta_fields)} if meta_fields is not None else {}),
            ),
        )

    def delete(self, *, teacher_id: str) -> Any:
        return self._invoke(name="delete", teacher_id=teacher_id)

    def update(
        self,
        *,
        teacher_id: str,
        name: str | None = None,
        lastname: str | None = None,
        lastnameend: str | None = None,
        email: str | None = None,
        uid: str | None = None,
        phone: str | None = None,
        school_id: int | None = None,
        language_code: str | None = None,
        meta_fields: Mapping[str, Any] | None = None,
    ) -> Any:
        """Update experimentally confirmed teacher fields.

        The accepted fields were verified on teacher ``250`` with synthetic
        values. Length limits and complete nullability rules remain untested.
        """
        values = {
            "name": name,
            "lastname": lastname,
            "lastnameend": lastnameend,
            "email": email,
            "uid": uid,
            "phone": phone,
            "school_id": school_id,
            "language_code": language_code,
        }
        if (
            not any(value is not None for value in values.values())
            and meta_fields is None
        ):
            raise ValueError("teacher update requires at least one field")
        payload = self._payload(**values)
        if meta_fields is not None:
            payload["metas"] = dict(meta_fields)
        return self._invoke(name="update", teacher_id=teacher_id, payload=payload)


class ContractsFacade(_Facade):
    """Public facade for teacher contracts."""

    def create(self, *, teacher_id: str, **fields: Any) -> Any:
        """Create a contract (fields inferred, not tested)."""
        return self._invoke(
            name="create", teacher_id=teacher_id, payload=self._payload(**fields)
        )

    def update(self, *, teacher_id: str, contract_id: str, **fields: Any) -> Any:
        return self._invoke(
            name="update",
            teacher_id=teacher_id,
            contract_id=contract_id,
            payload=self._payload(**fields),
        )


class AcademicFacade(_Facade):
    """Public facade for academic catalogues."""


class ClassroomsFacade(_Facade):
    """Public facade for classrooms."""

    def update(self, *, classroom_id: str, **fields: Any) -> Any:
        """Update a classroom (fields inferred, not tested)."""
        return self._invoke(
            name="update", classroom_id=classroom_id, payload=self._payload(**fields)
        )

    def delete(self, *, classroom_id: str) -> Any:
        return self._invoke(name="delete", classroom_id=classroom_id)

    def update_role(self, *, classroom_id: str, role_id: str, **fields: Any) -> Any:
        return self._invoke(
            name="update_role",
            classroom_id=classroom_id,
            role_id=role_id,
            payload=self._payload(**fields),
        )

    def delete_role(self, *, classroom_id: str, role_id: str) -> Any:
        return self._invoke(
            name="delete_role", classroom_id=classroom_id, role_id=role_id
        )


class EnrollmentsFacade(_Facade):
    """Public facade for enrollments."""

    def list_groups(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        """Return one page of enrollment groups."""
        return self._invoke(name="list_groups", page=page, limit=limit, **filters)

    def create(
        self,
        *,
        student_id: int,
        area_id: int,
        cycle_id: int,
        term_id: int,
        section_id: int,
    ) -> Any:
        """Create an enrollment; all five identifiers are inferred as required."""
        return self._invoke(
            name="create",
            payload=self._payload(
                student_id=student_id,
                area_id=area_id,
                cycle_id=cycle_id,
                term_id=term_id,
                section_id=section_id,
            ),
        )

    def create_for_group(self, *, group_id: int, student_id: int) -> Any:
        """Enroll a required ``student_id`` in the required group."""
        return self._invoke(
            name="create_for_group",
            group_id=group_id,
            payload={"student_id": student_id},
        )

    def enroll_student(self, **fields: Any) -> Any:
        """Enroll a student (fields inferred, not tested)."""
        return self._invoke(name="enroll_student", payload=self._payload(**fields))

    def create_draft(self, **fields: Any) -> Any:
        """Create an enrollment draft (fields inferred, not tested)."""
        return self._invoke(name="create_draft", payload=self._payload(**fields))


class AdmissionsFacade(_Facade):
    """Public facade for admissions."""

    def create(self, *, student_id: int, area_id: int, cycle_id: int) -> Any:
        """Create an admission; identifiers are inferred as required."""
        return self._invoke(
            name="create",
            payload=self._payload(
                student_id=student_id, area_id=area_id, cycle_id=cycle_id
            ),
        )

    def delete(
        self,
        *,
        admission_id: int | str | None = None,
        admission_ids: list[int | str] | None = None,
    ) -> Any:
        """Delete one admission or the admissions in ``admission_ids``."""
        ids = _one_or_many(
            singular_name="admission_id",
            singular=admission_id,
            plural_name="admission_ids",
            plural=admission_ids,
        )
        return self._invoke(name="delete", payload={"ids": ids})

    def create_draft(self, **fields: Any) -> Any:
        """Create an admission draft (fields inferred, not tested)."""
        return self._invoke(name="create_draft", payload=self._payload(**fields))

    def create_student(self, **fields: Any) -> Any:
        """Create an admission and student (fields inferred, not tested)."""
        return self._invoke(name="create_student", payload=self._payload(**fields))

    def create_group_student(self, **fields: Any) -> Any:
        """Create an admission for a group and student (fields inferred, not tested)."""
        return self._invoke(
            name="create_group_student", payload=self._payload(**fields)
        )


class CentersFacade(_Facade):
    """Public facade for centers."""

    def create(self, *, alias: str, title: str) -> Any:
        """Create a center; ``alias`` and ``title`` are inferred as required."""
        return self._invoke(
            name="create", payload=self._payload(alias=alias, title=title)
        )

    def delete(self, *, center_id: str) -> Any:
        return self._invoke(name="delete", center_id=center_id)

    def update(self, *, center_id: str, **fields: Any) -> Any:
        """Update a center (fields inferred, not tested)."""
        return self._invoke(
            name="update", center_id=center_id, payload=self._payload(**fields)
        )


class RolesFacade(_Facade):
    """Public facade for roles."""

    def create(self, **fields: Any) -> Any:
        """Create a role (fields inferred, not tested)."""
        return self._invoke(name="create", payload=self._payload(**fields))

    def delete(self, *, role_id: str) -> Any:
        return self._invoke(name="delete", role_id=role_id)

    def update(self, *, role_id: str, **fields: Any) -> Any:
        """Update a role (fields inferred, not tested)."""
        return self._invoke(
            name="update", role_id=role_id, payload=self._payload(**fields)
        )


class UsersFacade(_Facade):
    """Public facade for users."""


class CatalogsFacade(_Facade):
    """Public facade for system catalogues."""


class FinanceFacade(_Facade):
    """Public facade for finance."""

    def create_provider(self, **fields: Any) -> Any:
        """Create a provider (fields inferred, not tested)."""
        return self._invoke(name="create_provider", payload=self._payload(**fields))

    def create_provider_teacher(self, **fields: Any) -> Any:
        """Create a provider teacher (fields inferred, not tested)."""
        return self._invoke(
            name="create_provider_teacher", payload=self._payload(**fields)
        )

    def delete_provider(self, *, provider_id: str) -> Any:
        return self._invoke(name="delete_provider", provider_id=provider_id)

    def update_provider(self, *, provider_id: str, **fields: Any) -> Any:
        """Update a provider (fields inferred, not tested)."""
        return self._invoke(
            name="update_provider",
            provider_id=provider_id,
            payload=self._payload(**fields),
        )

    def delete_provider_teacher(self, *, teacher_id: str) -> Any:
        return self._invoke(name="delete_provider_teacher", teacher_id=teacher_id)

    def update_provider_teacher(self, *, teacher_id: str, **fields: Any) -> Any:
        return self._invoke(
            name="update_provider_teacher",
            teacher_id=teacher_id,
            payload=self._payload(**fields),
        )


class LeadsFacade(_Facade):
    """Public facade for leads."""

    def create(self, **fields: Any) -> Any:
        """Create a lead (fields inferred, not tested)."""
        return self._invoke(name="create", payload=self._payload(**fields))


class EcommerceFacade(_Facade):
    """Public facade for eCommerce."""

    def create_enrollment(self, **fields: Any) -> Any:
        """Create an eCommerce enrollment (fields inferred, not tested)."""
        return self._invoke(name="create_enrollment", payload=self._payload(**fields))

    def create_admission(self, **fields: Any) -> Any:
        """Create an eCommerce admission (fields inferred, not tested)."""
        return self._invoke(name="create_admission", payload=self._payload(**fields))


class ReportsFacade(_Facade):
    """Public facade for reports."""


class DraftsFacade(_Facade):
    """Public facade for drafts."""

    def create(self, *, model: str, **fields: Any) -> Any:
        """Create a model draft (fields inferred, not tested)."""
        return self._invoke(name="create", model=model, payload=self._payload(**fields))

    def create_root(self, **fields: Any) -> Any:
        """Create a root draft (fields inferred, not tested)."""
        return self._invoke(name="create_root", payload=self._payload(**fields))


def _one_or_many(
    *,
    singular_name: str,
    singular: int | str | None,
    plural_name: str,
    plural: list[int | str] | None,
) -> list[int | str]:
    if (singular is None) == (plural is None):
        raise ValueError(f"provide exactly one of {singular_name} or {plural_name}")
    if singular is not None:
        return [singular]
    assert plural is not None
    return plural


def _validate_student_update(*, values: Mapping[str, Any]) -> None:
    limits = {
        "name": 256,
        "lastname": 256,
        "lastnameend": 256,
        "email": 256,
        "uid": 256,
        "phone": 128,
    }
    for field, limit in limits.items():
        value = values.get(field)
        if value is not None and (not isinstance(value, str) or len(value) > limit):
            raise ValueError(
                f"student field {field!r} must be a string of at most {limit} characters"
            )
