"""Public Classlife resource interfaces."""

from .status import StatusResource
from .academic import AcademicResource
from .admissions import AdmissionsResource
from .catalogs import CatalogsResource
from .centers import CentersResource
from .classrooms import ClassroomsResource
from .contracts import ContractsResource
from .drafts import DraftsResource
from .ecommerce import EcommerceResource
from .enrollments import EnrollmentsResource
from .finance import FinanceResource
from .leads import LeadsResource
from .reports import ReportsResource
from .roles import RolesResource
from .students import StudentsResource
from .teachers import TeachersResource
from .users import UsersResource

__all__ = [
    "StatusResource",
    "AcademicResource",
    "AdmissionsResource",
    "CatalogsResource",
    "CentersResource",
    "ClassroomsResource",
    "ContractsResource",
    "DraftsResource",
    "EcommerceResource",
    "EnrollmentsResource",
    "FinanceResource",
    "LeadsResource",
    "ReportsResource",
    "RolesResource",
    "StudentsResource",
    "TeachersResource",
    "UsersResource",
]
