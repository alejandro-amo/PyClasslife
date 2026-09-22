# PyClasslife API reference

This document describes the public interface currently exposed by
ClasslifeClient. Public arguments are keyword-only.

~~~python
import pyclasslife as cl

classlife = cl.ClasslifeClient(
    api_key="your-api-key",
    client_id="your-client-id",
)
~~~

## Configuration

ClasslifeClient accepts the following keyword-only arguments:

~~~python
classlife = cl.ClasslifeClient(
    api_key="your-api-key",
    client_id="your-client-id",
    base_url=cl.DEFAULT_BASE_URL,
    timeout=(10, 60),
    total_timeout=120.0,
    session=None,
    logger=None,
)
~~~

- api_key is required.
- client_id defaults to an empty string. The default transport sends both
  authentication values on every request.
- base_url defaults to https://api.classlife.io/api/v1/.
- timeout is the per-attempt requests timeout. It may be a number or a
  (connect, read) tuple.
- total_timeout is the deadline for the complete operation.
- session optionally supplies a configured requests.Session.
- logger optionally supplies a standard-library logging.Logger.

When no logger is supplied, PyClasslife uses the pyclasslife package logger
with a NullHandler. Configure classlife.logger, or the package logger, when
application output is required.

Credentials can be loaded without logging their values:

~~~python
credentials = cl.get_credentials(source="env_vars")
classlife = cl.ClasslifeClient(
    api_key=credentials.api_key,
    client_id=credentials.client_id,
)
~~~

source accepts env_vars or env_file. env_file also requires env_file="path".
Both sources require CLASSLIFE_API_KEY and CLASSLIFE_CLIENT_ID.

## Cross-cutting concepts

The following concepts apply across resources and are documented separately
from the resource-specific operations.

### ClasslifeResponse

Non-paginated methods return a frozen ClasslifeResponse:

~~~python
response = classlife.status.get()
response.status
response.message
response.data
~~~

A successful JSON envelope requires status to be "ok" or "ko". message and
data are optional. data is None when Classlife omits it; PyClasslife does not
invent a value. An envelope with status="ko", an HTTP error, invalid JSON, or
an invalid envelope raises an exception.

### Page

Collection methods return one page:

~~~python
page = classlife.students.list(page=1, limit=500)
page.total
page.page
page.limit
page.count
page.items
page.total_pages
page.has_next
page.has_previous
page.next_page
page.previous_page
~~~

Pages are one-based. Collection methods default to page=1 and limit=500.
Callers request later pages explicitly:

~~~python
second_page = classlife.students.list(page=2, limit=500)
~~~

The client does not combine pages and does not create iterators. Additional
keyword arguments are sent as endpoint-specific query filters.

### Filtering

Filters are endpoint-specific query parameters and are not validated against a
universal schema. For example:

~~~python
page = classlife.teachers.list(name="Profesor")
page = classlife.students.list(
    **{"metas.email2": "john.doe@example.com"},
)
~~~

The dotted metas.<key> form must be expanded from a dictionary because it
cannot be written as a Python keyword. Meta keys are installation-specific and
opaque. Unknown or unsupported filters may result in HTTP 400.

### Errors

~~~python
try:
    response = classlife.status.get()
except cl.ConfigurationError:
    ...
except cl.TransportError:
    ...
except cl.HTTPResponseError:
    ...
except cl.FunctionalResponseError:
    ...
except cl.MalformedResponseError:
    ...
except cl.ResponseError:
    ...
~~~

All custom exceptions inherit from ClasslifeError. TransportError covers
network failures and exhausted transport deadlines. HTTPResponseError
represents a non-success HTTP status. FunctionalResponseError represents a
valid Classlife envelope with status="ko". MalformedResponseError means the
common response contract was violated. ResponseError is the general response
base class.

PyClasslife does not sanitize HTML or JavaScript in request or response data.
Applications that handle untrusted content should apply an appropriate
sanitizer, such as nh3, at their trust boundary.

## status

### get

~~~python
response = classlife.status.get()
~~~

GET /status. Returns ClasslifeResponse.

## students

### Create

#### create

~~~python
response = classlife.students.create(
    email="john.doe@example.com",
    name="Ada",
    lastname="Lovelace",
    lastnameend=None,
    uid=None,
    phone=None,
    school_id=None,
    language_code=None,
    meta_fields={"custom_field": "value"},
)
~~~

POST /students. email, name, and lastname are required. meta_fields is sent
under Classlife's metas object. The response must be inspected for the
identifier returned by the installation.

### Read

#### list

~~~python
page = classlife.students.list(page=1, limit=500, student_name="Ada")
~~~

GET /students. Returns Page.

#### get

~~~python
response = classlife.students.get(student_id="123")
~~~

GET /students/{student_id}. Returns ClasslifeResponse.

#### list_metas

~~~python
response = classlife.students.list_metas(page=1, limit=500)
~~~

GET /students/metas. This returns installation meta definitions, not the meta
values of one student. Read a student's values from the metas field in get or
list.

#### list_grades

~~~python
page = classlife.students.list_grades(
    student_id="123",
    page=1,
    limit=500,
)
~~~

GET /students/{student_id}/grades. Returns Page.

#### list_enrollments

~~~python
page = classlife.students.list_enrollments(
    student_id="123",
    page=1,
    limit=500,
)
~~~

GET /students/{student_id}/enrollments. Returns Page.

#### roles.list

~~~python
page = classlife.students.roles.list(
    student_id="123",
    page=1,
    limit=500,
)
~~~

GET /students/{student_id}/roles. Returns Page.

#### centers.list

~~~python
page = classlife.students.centers.list(
    student_id="123",
    page=1,
    limit=500,
)
~~~

GET /students/{student_id}/centers. Returns Page.

### Update

#### update

~~~python
response = classlife.students.update(
    student_id="123",
    student_name="Ada",
    student_lastname="Lovelace",
    student_email="john.doe@example.com",
    meta_fields={"custom_field": "new value"},
)
~~~

PATCH /students/{student_id}. At least one update value is required. The
public response-oriented names are student_name, student_lastname,
student_lastnameend, student_email, student_uid, and student_phone. The other
explicit values are school_id, language_code, and meta_fields.

#### roles.update

~~~python
response = classlife.students.roles.update(
    student_id="123",
    role_id="456",
    payload={"role": "value"},
)
~~~

PUT /students/{student_id}/roles/{role_id}.

#### centers.update

~~~python
response = classlife.students.centers.update(
    student_id="123",
    center_id="456",
    payload={"center": "value"},
)
~~~

PUT /students/{student_id}/centers/{center_id}.

### Delete

#### delete

~~~python
classlife.students.delete(student_id="123")
classlife.students.delete(student_ids=["123", "124"])
~~~

DELETE /students. Exactly one of student_id or student_ids is required.

#### roles.delete

~~~python
classlife.students.roles.delete(student_id="123", role_id="456")
~~~

DELETE /students/{student_id}/roles/{role_id}.

#### centers.delete

~~~python
classlife.students.centers.delete(student_id="123", center_id="456")
~~~

DELETE /students/{student_id}/centers/{center_id}.

### Other operations

#### block and disblock

~~~python
classlife.students.block(student_id="123")
classlife.students.disblock(student_id="123")
~~~

POST /students/{student_id}/block and POST
/students/{student_id}/disblock. The public facade currently accepts optional
additional keyword fields for compatibility with the endpoint.

## teachers

### Create

#### create

~~~python
response = classlife.teachers.create(
    email="john.doe@example.com",
    name="Ada",
    lastname="Lovelace",
    meta_fields={"custom_field": "value"},
)
~~~

POST /teachers. email, name, and lastname are required. Optional teacher
fields are lastnameend, uid, phone, school_id, language_code, and meta_fields.

### Read

#### list

~~~python
page = classlife.teachers.list(page=1, limit=500, name="Profesor")
~~~

GET /teachers. Returns Page.

#### get

~~~python
response = classlife.teachers.get(teacher_id="123")
~~~

GET /teachers/{teacher_id}. Returns ClasslifeResponse.

#### list_metas

~~~python
response = classlife.teachers.list_metas(page=1, limit=500)
~~~

GET /teachers/metas. Returns teacher meta definitions, not one teacher's
values. Read values from the metas field of get or list.

#### contracts.list

~~~python
page = classlife.teachers.contracts.list(
    teacher_id="123",
    page=1,
    limit=500,
)
~~~

GET /teachers/{teacher_id}/contracts. Returns Page.

#### contracts.get

~~~python
response = classlife.teachers.contracts.get(
    teacher_id="123",
    contract_id="456",
)
~~~

GET /teachers/{teacher_id}/contracts/{contract_id}.

#### contracts.list_metas

~~~python
response = classlife.teachers.contracts.list_metas(page=1, limit=500)
~~~

GET /contracts/metas. Returns contract meta definitions, not one contract's
values.

### Update

#### update

~~~python
response = classlife.teachers.update(
    teacher_id="123",
    name="Ada",
    email="john.doe@example.com",
    meta_fields={"custom_field": "new value"},
)
~~~

PATCH /teachers/{teacher_id}. At least one field is required. Supported
explicit fields are name, lastname, lastnameend, email, uid, phone, school_id,
language_code, and meta_fields.

#### contracts.update

~~~python
response = classlife.teachers.contracts.update(
    teacher_id="123",
    contract_id="456",
    field="value",
)
~~~

PATCH /teachers/{teacher_id}/contracts/{contract_id}. Additional keyword
arguments are placed in the request payload.

### Delete

#### delete

~~~python
classlife.teachers.delete(teacher_id="123")
~~~

DELETE /teachers/{teacher_id}.

Contract deletion is intentionally not exposed because Classlife's observed
contract-delete behavior is inconsistent.

## academic

Academic operations are read-only catalogue operations.

| Method | Route | Return |
| --- | --- | --- |
| list_degrees(page=1, limit=500, **filters) | GET /degrees | Page |
| get_degree(degree_id=...) | GET /degrees/{degree_id} | ClasslifeResponse |
| list_areas(page=1, limit=500, **filters) | GET /areas | Page |
| get_area(area_id=...) | GET /areas/{area_id} | ClasslifeResponse |
| list_area_grades(area_id=..., page=1, limit=500, **filters) | GET /areas/{area_id}/grades | Page |
| list_cycles(page=1, limit=500, **filters) | GET /cycles | Page |
| get_cycle(cycle_id=...) | GET /cycles/{cycle_id} | ClasslifeResponse |
| list_terms(page=1, limit=500, **filters) | GET /terms | Page |
| get_term(term_id=...) | GET /terms/{term_id} | ClasslifeResponse |
| list_sections(page=1, limit=500, **filters) | GET /sections | Page |
| get_section(section_id=...) | GET /sections/{section_id} | ClasslifeResponse |
| list_curriculum(page=1, limit=500, **filters) | GET /curriculum | Page |

## classrooms

| Method | Route | Return |
| --- | --- | --- |
| list(page=1, limit=500, **filters) | GET /classrooms | Page |
| get(classroom_id=...) | GET /classrooms/{classroom_id} | ClasslifeResponse |
| list_roles(classroom_id=..., page=1, limit=500, **filters) | GET /classrooms/{classroom_id}/roles | Page |
| list_students(classroom_id=..., page=1, limit=500, **filters) | GET /classrooms/{classroom_id}/students | Page |
| update(classroom_id=..., **fields) | PATCH /classrooms/{classroom_id} | ClasslifeResponse |
| update_role(classroom_id=..., role_id=..., **fields) | PUT /classrooms/{classroom_id}/roles/{role_id} | ClasslifeResponse |
| delete(classroom_id=...) | DELETE /classrooms/{classroom_id} | ClasslifeResponse |
| delete_role(classroom_id=..., role_id=...) | DELETE /classrooms/{classroom_id}/roles/{role_id} | ClasslifeResponse |

## enrollments

### Create

#### create

~~~python
response = classlife.enrollments.create(
    student_id=123,
    area_id=456,
    cycle_id=789,
    term_id=12,
    section_id=34,
)
~~~

POST /enrollments. The five identifiers are explicit required parameters.

#### create_for_group

~~~python
response = classlife.enrollments.create_for_group(
    group_id=123,
    student_id=456,
)
~~~

POST /enroll_groups/{group_id}/enrollments.

#### enroll_student

~~~python
response = classlife.enrollments.enroll_student(
    student_id=123,
    enroll_group_id=456,
)
~~~

POST /enroll-student. Keyword arguments become the payload.

#### create_draft

~~~python
response = classlife.enrollments.create_draft(student_id=123)
~~~

POST /enrollments/draft.

### Read

| Method | Route | Return |
| --- | --- | --- |
| list_groups(page=1, limit=500, **filters) | GET /enroll_groups | Page |
| get_group(group_id=...) | GET /enroll_groups/{group_id} | ClasslifeResponse |
| list_group_grades(group_id=..., page=1, limit=500, **filters) | GET /enroll_groups/{group_id}/grades | Page |
| list(page=1, limit=500, **filters) | GET /enrollments | Page |
| get(enrollment_id=...) | GET /enrollments/{enrollment_id} | ClasslifeResponse |

## admissions

| Method | Route | Return |
| --- | --- | --- |
| create(student_id=..., area_id=..., cycle_id=...) | POST /admissions | ClasslifeResponse |
| create_draft(**fields) | POST /admissions/draft | ClasslifeResponse |
| create_student(**fields) | POST /admission-student | ClasslifeResponse |
| create_group_student(**fields) | POST /admission-group-student | ClasslifeResponse |
| get(admission_id=...) | GET /admissions/{admission_id} | ClasslifeResponse |
| delete(admission_id=...) or delete(admission_ids=...) | DELETE /admissions | ClasslifeResponse |

The delete method requires exactly one of admission_id or admission_ids.

## centers

| Method | Route | Return |
| --- | --- | --- |
| list(page=1, limit=500, **filters) | GET /centers | Page |
| get(center_id=...) | GET /centers/{center_id} | ClasslifeResponse |
| list_students(center_id=..., page=1, limit=500, **filters) | GET /centers/{center_id}/students | Page |
| create(alias=..., title=...) | POST /centers | ClasslifeResponse |
| update(center_id=..., **fields) | PATCH /centers/{center_id} | ClasslifeResponse |
| delete(center_id=...) | DELETE /centers/{center_id} | ClasslifeResponse |

## roles

| Method | Route | Return |
| --- | --- | --- |
| list(page=1, limit=500, **filters) | GET /roles | Page |
| get(role_id=...) | GET /roles/{role_id} | ClasslifeResponse |
| list_classrooms(role_id=..., page=1, limit=500, **filters) | GET /roles/{role_id}/classrooms | Page |
| list_students(role_id=..., page=1, limit=500, **filters) | GET /roles/{role_id}/students | Page |
| create(**fields) | POST /roles | ClasslifeResponse |
| update(role_id=..., **fields) | PATCH /roles/{role_id} | ClasslifeResponse |
| delete(role_id=...) | DELETE /roles/{role_id} | ClasslifeResponse |

## users

| Method | Route | Return |
| --- | --- | --- |
| list(page=1, limit=500, **filters) | GET /users | Page |
| get(user_id=...) | GET /users/{user_id} | ClasslifeResponse |

## catalogs

| Method | Route | Return |
| --- | --- | --- |
| list_languages(page=1, limit=500, **filters) | GET /languages | Page |
| get_language(language_id=...) | GET /languages/{language_id} | ClasslifeResponse |
| list_schools(page=1, limit=500, **filters) | GET /schools | Page |
| get_school(school_id=...) | GET /schools/{school_id} | ClasslifeResponse |
| list_picklists(page=1, limit=500, **filters) | GET /picklists | Page |
| get_picklist(picklist_id=...) | GET /picklists/{picklist_id} | ClasslifeResponse |

## finance

| Method | Route | Return |
| --- | --- | --- |
| list_provider_metas(page=1, limit=500) | GET /providers/metas | ClasslifeResponse |
| list_provider_teacher_metas(page=1, limit=500) | GET /providers/teachers/metas | ClasslifeResponse |
| list_receipts(page=1, limit=500, **filters) | GET /receipts | Page |
| get_receipt(receipt_id=...) | GET /receipts/{receipt_id} | ClasslifeResponse |
| list_invoices(page=1, limit=500, **filters) | GET /invoices | Page |
| get_invoice(invoice_id=...) | GET /invoices/{invoice_id} | ClasslifeResponse |
| list_remittances(page=1, limit=500, **filters) | GET /remittances | Page |
| get_remittance(remittance_id=...) | GET /remittances/{remittance_id} | ClasslifeResponse |
| list_providers(page=1, limit=500, **filters) | GET /providers | Page |
| get_provider(provider_id=...) | GET /providers/{provider_id} | ClasslifeResponse |
| list_provider_teachers(page=1, limit=500, **filters) | GET /providers/teachers | Page |
| get_provider_teacher(teacher_id=...) | GET /providers/teachers/{teacher_id} | ClasslifeResponse |
| list_discounts(page=1, limit=500, **filters) | GET /finance/discounts | Page |
| create_provider(**fields) | POST /providers | ClasslifeResponse |
| create_provider_teacher(**fields) | POST /providers/teachers | ClasslifeResponse |
| update_provider(provider_id=..., **fields) | PATCH /providers/{provider_id} | ClasslifeResponse |
| update_provider_teacher(teacher_id=..., **fields) | PATCH /providers/teachers/{teacher_id} | ClasslifeResponse |
| delete_provider(provider_id=...) | DELETE /providers/{provider_id} | ClasslifeResponse |
| delete_provider_teacher(teacher_id=...) | DELETE /providers/teachers/{teacher_id} | ClasslifeResponse |

The two provider meta methods return definitions, not values for one provider.

## leads

| Method | Route | Return |
| --- | --- | --- |
| list_sources(page=1, limit=500, **filters) | GET /leads_sources | Page |
| list_segments(page=1, limit=500, **filters) | GET /leads_segments | Page |
| list_commercials(page=1, limit=500, **filters) | GET /leads_commercials | Page |
| list(page=1, limit=500, **filters) | GET /leads | Page |
| get(lead_id=...) | GET /leads/{lead_id} | ClasslifeResponse |
| create(**fields) | POST /leads | ClasslifeResponse |

## ecommerce

| Method | Route | Return |
| --- | --- | --- |
| list_products(page=1, limit=500, **filters) | GET /ecommerce/products | Page |
| create_enrollment(**fields) | POST /ecommerce/enrollment | ClasslifeResponse |
| create_admission(**fields) | POST /ecommerce/admission | ClasslifeResponse |

## reports

| Method | Route | Return |
| --- | --- | --- |
| list(page=1, limit=500, **filters) | GET /reports | Page |
| get(report_id=...) | GET /reports/{report_id} | ClasslifeResponse |
| get_interactive_screen(params=None) | GET /interactivescreen | ClasslifeResponse |

params is an optional mapping forwarded as query parameters.

## drafts

| Method | Route | Return |
| --- | --- | --- |
| list(model=..., page=1, limit=500, **filters) | GET /draft | Page |
| get(model=..., object_id=...) | GET /draft/{model}/{object_id} | ClasslifeResponse |
| create(model=..., **fields) | POST /draft/{model} | ClasslifeResponse |
| create_root(**fields) | POST /draft | ClasslifeResponse |
