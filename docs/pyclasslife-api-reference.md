# PyClasslife API reference

## Inicialización

```python
import pyclasslife as cl

classlife = cl.ClasslifeClient(
    api_key="your-api-key",
    client_id="your-client-id",
)
```

Los métodos de la interfaz pública utilizan argumentos con nombre. Las
respuestas conservan el resultado interpretado por Classlife, incluyendo sus
metadatos de paginación cuando el endpoint los proporciona.

## Enrollments

### list_groups

```python
response = classlife.enrollments.list_groups(page=1, limit=500)
```

Solicita una página de grupos de matrícula mediante `GET /enroll_groups`.
`page` empieza en `1` y `limit` controla el tamaño solicitado de la página.
La respuesta paginada expone normalmente `total`, `page`, `limit`, `count` e
`items` dentro de `response.data`.

Cada elemento de `items` representa un grupo de matrícula. En muestras reales
se han observado, entre otros, estos campos:

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

La instalación puede añadir campos de configuración propios, incluidos
campos con nombres localizados o espacios. También puede devolver `null` para
campos no configurados. Por ello, los consumidores deben tratar los campos
no esenciales como opcionales y no deben asumir que todos los elementos tienen
exactamente las mismas claves o tipos. Los campos `metas` son extensiones
personalizables y deben tratarse como un mapa opaco cuando aparezcan.

Para solicitar otra página, se vuelve a llamar al mismo método usando el
número de página indicado por `response.data["page"]` y los mismos límites:

```python
second_page = classlife.enrollments.list_groups(page=2, limit=500)
```

`list_groups` devuelve una página; no combina páginas ni crea un iterador.

#### Filtros de listados

Los métodos de listado aceptan filtros adicionales como argumentos con nombre;
se envían como parámetros de consulta junto con `page` y `limit`:

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

La API de Classlife no aplica una política uniforme a todos los atributos. La
lista completa de filtros observados experimentalmente, junto con sus
cardinalidades y limitaciones, se mantiene en la documentación interna del
proyecto. Las claves de
`metas` son específicas de cada instalación y se pueden consultar con la
notación `metas.<clave>` cuando la instalación las expone, por ejemplo
`metas.email2=...`. Los filtros no reconocidos pueden producir HTTP 400.

#### Filtros observados por resource

La siguiente tabla resume los filtros que han producido una reducción
observable en pruebas GET. Es evidencia de comportamiento de Classlife, no una
garantía contractual para todas las instalaciones.

| Resource | Filtros observados |
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

Los filtros de texto observados admiten búsquedas parciales y, en los casos
probados, insensibles a mayúsculas/minúsculas. El carácter `%` se comporta
como comodín en `teachers.name`. La combinación de filtros se comporta como
una conjunción (`AND`). Los filtros booleanos no deben convertirse según la
truthiness de Python: Classlife puede exigir representaciones como `1` o `0`
según el campo. Los filtros `metas.<clave>` son posibles cuando la instalación
expone esa meta, pero sus nombres y semántica no son portables.

Como `metas.<clave>` contiene un punto y no puede escribirse como un keyword
Python normal, se puede pasar mediante expansión de diccionario:

```python
students_with_email = classlife.students.list(
    **{"metas.email2": "example.invalid"},
)
```

### get_group

```python
response = classlife.enrollments.get_group(group_id=123)
```

Obtiene un grupo concreto mediante `GET /enroll_groups/{id}`. Su estructura de
datos comparte los campos del listado, aunque la instalación puede poblar
campos opcionales de forma diferente.

### list_group_grades

```python
response = classlife.enrollments.list_group_grades(group_id=123, page=1, limit=500)
```

Obtiene una página de calificaciones del grupo mediante
`GET /enroll_groups/{id}/grades`.
