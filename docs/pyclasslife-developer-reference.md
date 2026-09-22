# PyClasslife — Developer Reference

This document describes the architecture and engineering conventions of
PyClasslife for contributors. The public consumer API is documented separately
in [the API reference](pyclasslife-api-reference.md).

## Project structure

```text
src/pyclasslife/
├── client.py              # Public ClasslifeClient entry point
├── authentication.py      # Credentials applied to every request
├── transport.py           # HTTP, retries, deadlines and observability
├── _response_handler.py   # Common Classlife response envelope
├── pagination.py          # Public pagination value objects
├── logging.py             # Logger factory and structured adapter
├── tools.py               # Public credential-loading utilities
├── facades/               # Ergonomic consumer-facing methods
└── resources/             # Endpoint-specific implementation
```

`devdocs/` is part of the local development workspace but is intentionally
ignored by Git and excluded from packages and releases. It contains internal
research, samples and working notes; it is not a substitute for this document.
The folder may be provided to developers who want to collaborate on the
project so they can review the research context and internal samples. It must
remain outside commits, packages and releases.

## Layer responsibilities

`ClasslifeClient` is the composition root. It creates or accepts the transport,
selects the logger, creates the authentication component and exposes the public
facades.

Facades are the consumer-facing API. They provide explicit, ergonomic,
keyword-only methods and translate canonical PyClasslife argument names into
Classlife payload names where necessary.

Resources are implementation components. They are the only components that know
concrete Classlife routes and HTTP operations. Every API request from a resource
must go through the injected transport. Resources must not call `requests`
directly, create their own sessions, or duplicate authentication logic.

The response handler processes the common Classlife response envelope. It
requires `status` and preserves `message` when present. `data` may be absent
and is represented as `None`; when present, its structure is checked according
to the common contract. Resource-specific validation and domain interpretation
belong above the transport layer.

## Public method conventions

All public functions and methods use keyword-only arguments, including methods
that accept only one argument. New facade methods should follow the pattern:

```python
def get(self, *, student_id: int) -> ClasslifeResponse:
    ...
```

Prefer nested subresources such as `classlife.students.roles.delete(...)` over
flat names such as `classlife.students.delete_role(...)`. Keep facades faithful
to operations that exist in the Classlife API; compound workflows and
multi-operation business logic belong in a future service layer.

Use explicit canonical names in the public API. For example, if Classlife uses
`name` in one operation and `student_name` in another, the facade should expose
the name that is appropriate and unambiguous for the PyClasslife contract and
translate it internally.

## Transport

`ClasslifeTransport` is deliberately limited to resilient HTTP behavior:

- `requests` is the only HTTP implementation.
- Supported methods and absolute `http`/`https` URLs are validated before use.
- Embedded URL credentials and redirects are rejected.
- Safe methods (`GET`, `HEAD`, `OPTIONS`) retry `408`, `429`, `500`, `502`,
  `503` and `504` by default.
- Mutations do not retry unless the transport is constructed with
  `retry_mutations=True`.
- Retries use exponential backoff with jitter.
- `Retry-After` is honored for `429` when usable.
- `total_timeout` is an operation deadline and can be overridden per request
  with a keyword-only argument.
- Network failures and exhaustion of the operation deadline are exposed as
  `TransportError`.

The transport does not validate domain payloads, interpret functional business
errors, or impose preventive rate limits. Those responsibilities belong to
higher layers or to the consuming application.

## Authentication

`ClasslifeAuthentication` is immutable and applies the documented `apikey` and
`clientId` headers to every request. Classlife does not require a prior session
token for the current integration model.

`ClasslifeCredentials` keeps sensitive fields out of `repr`. Do not add secrets
to exception messages, logs, fixtures, documentation or distribution artifacts.

## Logging

The client accepts an optional standard-library `logging.Logger`. When one is
not supplied, it uses the package logger `pyclasslife`, configured with a
`NullHandler` and therefore without implicit output. Consumers can configure
`client.logger` with their own handlers, levels and formatters.

`ClasslifeLoggerAdapter` provides shared structured events. Transport events may
include the HTTP method, sanitized endpoint, attempt number, HTTP status and
durations for attempts and the complete operation. Payloads, full headers,
query values and personal data must not be logged. Sensitive URL values are
replaced completely with `[REDACTED]`.

Every class created or used by `ClasslifeClient` accepts logger injection and
propagates the logger or an appropriate child logger.

## Pagination and metas

Paginated resource methods expose `page` and `limit` and may accept additional
keyword-only query filters supported by the corresponding Classlife operation.
Unknown filters may produce an HTTP error and must not be silently invented.

Classlife metas are installation-specific mappings. Treat their keys, types,
semantics and limits as opaque. Facades may expose explicit meta operations,
but must not assume a fixed catalogue of meta fields.

## Tests and quality

Unit tests live in `tests/unit/`. They must not load `.env` files, use real
credentials or access the network; HTTP is isolated with mocks or test servers.

Integration tests live in `tests/integration/`. They require an explicit
environment file whose name contains `TEST` and does not contain `PROD`. The
runner validates this before pytest starts:

```text
python scripts/run_tests.py unit
python scripts/run_tests.py integration --env-file .env-brand-test.local
```

Black is the official formatter and targets Python 3.11:

```text
python -m black --target-version py311 src tests
```

Run tests, formatting, type checks and build validation before submitting a
change. Add or update tests for every behavioral change.

## Documentation and contribution workflow

Public consumer behavior belongs in `docs/pyclasslife-api-reference.md`.
Technical details about private methods and architecture belong in this file.
Research notes, raw samples and installation-specific observations belong in
the Git-ignored `devdocs/` directory.

For collaboration requests, contact hello@alejandroamo.eu.

Before opening a contribution:

1. Inspect existing changes and preserve unrelated work.
2. Confirm the endpoint contract against the maintained Classlife V1 sources.
3. Implement the smallest change in the correct layer.
4. Add unit tests and update public or technical documentation as appropriate.
5. Run formatting, tests and distribution validation.
6. Confirm that credentials, personal data, `devdocs/` and build artifacts are
   absent from the commit.

Builds must produce both an sdist and a wheel. Validate them with `twine check`
and inspect their contents before any publication. Never reuse a published
version.
