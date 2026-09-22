# PyClasslife API reference

## Initialization

```python
import pyclasslife as cl

classlife = cl.ClasslifeClient(
    api_key="your-api-key",
    client_id="your-client-id",
)
```

Public interface methods use keyword arguments. Responses preserve the result
interpreted from Classlife, including pagination metadata when the endpoint
provides it.

## Enrollments

### list_groups

```python
response = classlife.enrollments.list_groups(page=1, limit=500)
```

Requests one page of enrollment groups through `GET /enroll_groups`.
`page` starts at `1` and `limit` controls the requested page size. A paginated
response normally exposes `total`, `page`, `limit`, `count`, and `items` inside
`response.data`.

Each `items` element represents an enrollment group. Real samples have exposed,
among others, the following fields:

```python
{
    "enroll_group_id": 123,
    "enroll_alias": "...",
    "enroll_group_name": "...",
    "school_name": "...",
    "degree_title": "...",
    "area_title": "...",
    "ciclo_title": "...",
    "section_title": "...",
    "term_title": "...",
    "year": 2025,
    "enroll_ini": "...",
    "enroll_end": "...",
    "school_id": 1,
    "degree_id": 2,
    "area_id": 3,
    "ciclo_id": 4,
    "section_id": 5,
    "term_id": 6,
    "plazas": 0,
    "creditos": 0,
    "codigo_programa": "...",
    "destinatarios": "...",
    "building_id": None,
    "building_title": None,
    "fecha_creacion": "...",
    "ultima_actualizacion": "...",
    "counters": {
        "enroll_group_id": 123,
        "seats": 0,
        "enrolled": "...",
        "pre_enrolled": "...",
        "availables": "...",
    },
}
```

An installation may add custom configuration fields, including fields with
localized names or spaces. It may also return `null` for unconfigured fields.
Consumers should therefore treat non-essential fields as optional and must not
assume that every item has exactly the same keys or types. `metas` fields are
customizable extensions and must be treated as an opaque mapping when present.

To request another page, call the same method again with the page number from
`response.data["page"]` and the same limits:

```python
second_page = classlife.enrollments.list_groups(page=2, limit=500)
```

`list_groups` returns one page; it does not combine pages or create an iterator.

#### List filters

List methods accept additional filters as keyword arguments; they are sent as
query parameters together with `page` and `limit`:

```python
students_page = classlife.students.list(
    student_name="Ada",
    student_email="example.invalid",
)
teachers_page = classlife.teachers.list(name="Profesor")
groups_page = classlife.enrollments.list_groups(
    degree_id=2,
    section_id=5,
)
```

The Classlife API does not apply a uniform policy to every attribute. The full
list of experimentally observed filters, together with their cardinalities and
limitations, is maintained in the project's internal documentation. `metas`
keys are installation-specific and can be queried with `metas.<key>` when the
installation exposes them, for example `metas.email2=...`. Unknown filters may
produce HTTP 400.

#### Observed filters by resource

The following table summarizes filters that produced an observable reduction
in GET tests. This is evidence of observed Classlife behavior, not a contractual
guarantee for every installation.

| Resource | Observed filters |
| --- | --- |
| `students` | `student_id`, `student_key`, `student_full_name`, `student_name`, `student_lastname`, `student_lastnameend`, `student_email`, `student_phone`, `student_uid` |
| `teachers` | `id`, `name`, `lastname`, `email`, `uid`, `language_code`, `registration_date` |
| `enrollments` | `enroll_id`, `enroll_group` |
| `enroll_groups` | `enroll_group_id`, `enroll_alias`, `enroll_group_name`, `degree_title`, `area_title`, `ciclo_title`, `section_title`, `term_title`, `nombre_del_programa_oficial_completo` |
| `degrees` | `degree_id`, `degree_alias`, `degree_title` |
| `areas` | `area_id`, `area_alias`, `area_type`, `area_title`, `creditos_euneiz`, `area_ects`, `degree_id` |
| `cycles` | `cycle_id`, `cycle_alias`, `cycle_title`, `start_date`, `end_date` |
| `terms` | `term_id`, `term_alias`, `term_title` |
| `sections` | `section_id`, `section_alias`, `section_title` |
| `languages` | `language_id`, `language_code`, `language_name` |
| `schools` | `school_id` |
| `picklists` | `id`, `name`, `key` |
| `classrooms` | `classroom_id`, `classroom_title`, `academic_group`, `date_ini`, `date_end`, `ciclo_title`, `term_title`, `section_title`, `degree_title`, `area_title`, `area_length`, `program_title`, `course_title`, `course_length`, `degree_alias`, `program_alias`, `course_alias`, `ciclo_alias`, `term_alias`, `section_alias`, `degree_id`, `area_id`, `program_id`, `course_id`, `ciclo_id`, `term_id`, `section_id` |
| `receipts` | `receipt_id`, `enroll_id`, `student_id`, `invoice_id`, `payment_method_id`, `receipt_price`, `receipt_status_id`, `receipt_total`, `remittance_id` |
| `invoices` | `invoice_id`, `enroll_id`, `area_id`, `student_id`, `payment_method_id`, `remittance_id`, `status_id` |
| `remittances` | `remittance_id`, `remittance_status`, `emission_date`, `end_date`, `remittance_paid`, `remittance_registers`, `remittance_returned`, `remittance_total` |
| `providers` | `id`, `tax_number`, `zip_code`, `country` |
| `finance.discounts` | `discount_id`, `discount_type`, `discount_code`, `discount_amount`, `discount_code_type`, `discount_start`, `discount_end`, `discount_usage_limit`, `ciclo_id` |
| `leads` | `lead_id`, `lead_source_id` |
| `leads_commercials` | `user_id` |
| `users` | `user_id`, `user_role_id`, `user_active` |
| `curriculum` | `degree_id`, `area_id`, `program_id`, `course_id` |

The observed text filters support partial searches and, in the tested cases,
are case-insensitive. The `%` character behaves as a wildcard for
`teachers.name`. Combining filters behaves as a conjunction (`AND`). Boolean
filters must not be converted according to Python truthiness: Classlife may
require representations such as `1` or `0` depending on the field.
`metas.<key>` filters are possible when the installation exposes that meta, but
their names and semantics are not portable.

Because `metas.<key>` contains a dot and cannot be written as a normal Python
keyword, pass it by expanding a dictionary:

```python
students_with_email = classlife.students.list(
    **{"metas.email2": "example.invalid"},
)
```

### get_group

```python
response = classlife.enrollments.get_group(group_id=123)
```

Gets one enrollment group through `GET /enroll_groups/{id}`. Its data structure
shares the fields of the list response, although an installation may populate
optional fields differently.

### list_group_grades

```python
response = classlife.enrollments.list_group_grades(group_id=123, page=1, limit=500)
```

Gets one page of group grades through `GET /enroll_groups/{id}/grades`.
