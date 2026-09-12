"""Public entry point for the PyClasslife client."""

from __future__ import annotations

import logging
from typing import Any

from ._response_handler import _ResponseHandler
from .authentication import ClasslifeAuthentication
from .constants import DEFAULT_BASE_URL
from .facades import (
    AcademicFacade,
    AdmissionsFacade,
    CatalogsFacade,
    CentersFacade,
    ClassroomsFacade,
    ContractsFacade,
    DraftsFacade,
    EcommerceFacade,
    EnrollmentsFacade,
    FinanceFacade,
    LeadsFacade,
    ReportsFacade,
    RolesFacade,
    StatusFacade,
    StudentsFacade,
    TeachersFacade,
    UsersFacade,
)
from .logging import get_logger
from .resources import (
    AcademicResource,
    AdmissionsResource,
    CatalogsResource,
    CentersResource,
    ClassroomsResource,
    ContractsResource,
    DraftsResource,
    EcommerceResource,
    EnrollmentsResource,
    FinanceResource,
    LeadsResource,
    ReportsResource,
    RolesResource,
    StatusResource,
    StudentsResource,
    TeachersResource,
    UsersResource,
)
from .transport import ClasslifeTransport


class ClasslifeClient:
    """Configure authentication and expose the public domain facades."""

    def __init__(
        self,
        *,
        api_key: str,
        client_id: str = "",
        base_url: str = DEFAULT_BASE_URL,
        transport: ClasslifeTransport | Any | None = None,
        timeout: float | tuple[float, float] = (10, 60),
        total_timeout: float | None = 120.0,
        session: Any | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.logger = logger or get_logger()
        self.api_key = api_key.strip() if isinstance(api_key, str) else api_key
        self.client_id = client_id.strip() if isinstance(client_id, str) else client_id
        self.base_url = base_url.rstrip("/") + "/"
        self.authentication = (
            ClasslifeAuthentication(
                api_key=self.api_key,
                client_id=self.client_id or "unit-client",
                logger=self.logger,
            )
            if transport is None
            else None
        )
        self.transport = transport or ClasslifeTransport(
            authentication=self.authentication,
            timeout=timeout,
            total_timeout=total_timeout,
            session=session,
            logger=self.logger,
        )
        handler = _ResponseHandler(logger=self.logger)
        common = dict(
            base_url=self.base_url,
            transport=self.transport,
            response_handler=handler,
            logger=self.logger,
        )

        self.status = StatusFacade(
            resource=StatusResource(
                **{k: common[k] for k in ("base_url", "transport", "response_handler")}
            )
        )
        self.students = StudentsFacade(resource=StudentsResource(**common))
        self.teachers = TeachersFacade(resource=TeachersResource(**common))
        self.academic = AcademicFacade(resource=AcademicResource(**common))
        self.classrooms = ClassroomsFacade(resource=ClassroomsResource(**common))
        self.enrollments = EnrollmentsFacade(resource=EnrollmentsResource(**common))
        self.admissions = AdmissionsFacade(resource=AdmissionsResource(**common))
        self.centers = CentersFacade(resource=CentersResource(**common))
        self.roles = RolesFacade(resource=RolesResource(**common))
        self.users = UsersFacade(resource=UsersResource(**common))
        self.catalogs = CatalogsFacade(resource=CatalogsResource(**common))
        self.finance = FinanceFacade(resource=FinanceResource(**common))
        self.leads = LeadsFacade(resource=LeadsResource(**common))
        self.ecommerce = EcommerceFacade(resource=EcommerceResource(**common))
        self.reports = ReportsFacade(resource=ReportsResource(**common))
        self.drafts = DraftsFacade(resource=DraftsResource(**common))

    def __repr__(self) -> str:
        return f"ClasslifeClient(base_url={self.base_url!r})"
