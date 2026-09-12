# PyClasslife — agent instructions

## Objective

PyClasslife is a typed Python 3 library for the Classlife API. The project must
install as a standard package, produce valid PyPI artifacts, and support
controlled publication.

## Principles

- Keep source code under `src/pyclasslife/` and separate code, tests, and configuration.
- Keep the public API small, explicit, and backward-compatible where possible.
- Require keyword-only arguments for every public function and method, including single-argument calls. Use `*` in signatures.
- The main public class is `ClasslifeClient`.
- Use type hints, docstrings, and clear names. Do not expose internal APIs accidentally.
- Keep public documentation and technical documentation for private methods in separate files. Public documentation describes only the consumer API; implementation details, invariants, and private helpers belong in technical documentation.
- Document public `pyclasslife.tools` utilities with the main public class in public documentation.
- Do not include credentials, tokens, cookies, sensitive Classlife responses, or personal data in the repository, logs, fixtures, or artifacts.
- Keep sensitive data out of `repr`; apply `repr=False` only to sensitive fields and retain useful non-sensitive debugging information.
- Document breaking changes as version changes.
- Prefer minimal dependencies with compatible licenses.
- `devdocs/` is part of the local workspace and must remain inside this directory, but is explicitly ignored by Git and excluded from packages and releases.

## Initial architecture

- Keep replaceable layers small: `transport` handles only HTTP requests and resilience; `authentication` prepares credentials for each request; domain resources implement Classlife operations.
- Organize public domain facades and internal resources under `src/pyclasslife/resources/`. Resources delegate HTTP to `transport` and common envelopes to the response handler.
- Keep public facades separate from internal resources: facades provide ergonomic methods and build parameters; resources alone know concrete routes and may call `transport`.
- When Classlife uses different names for writing and reading, public facades must use explicit canonical response names. For example, PyClasslife uses `student_name` and the resource translates it to Classlife's `name` payload field.
- Prefer hierarchical subresources such as `client.students.roles.delete(...)` over flat methods such as `client.students.delete_role(...)`.
- Expose only operations corresponding to real Classlife endpoints. Reserve compound workflows for a future `services` layer; do not add convenience iterators or workflows to facades.
- `devdocs/cobertura_crud.md` contains the resource/CRUD matrix of Classlife's API V1. Update it whenever a documented operation is implemented.
- `transport` centralizes per-attempt timeouts, total operation deadlines, network errors, retries, backoff, jitter, retry limits, and safe observability. The total limit must support a keyword-only per-request override. It must not know domain resources or print secrets.
- `authentication` applies `apiKey` and `clientId` to every request because the documented API does not use a prior session token.
- Keep `transport` and `authentication` injectable so resources can be tested without real credentials or network access.
- Every class created or used by `ClasslifeClient` must accept an injectable `logging.Logger` and send useful diagnostic messages there. Messages must never contain credentials, full headers, sensitive bodies, or personal data.
- The default logger is the `pyclasslife` package logger with a `NullHandler`; `ClasslifeClient.logger` is exposed so consumers can configure handlers, levels, and formats. Use `ClasslifeLoggerAdapter` for structured events and logger propagation.
- Do not add preventive rate limiting by default; transport only reacts in a bounded way to `429`.
- The common response handler validates the response envelope, interprets `status`, and creates response errors. Resource-specific schema validation and final public-API mapping belong to higher layers.
- Add new layers only after confirming their contract against Classlife V1 documentation.
- List methods expose `page` and `limit` explicitly and accept additional
  query filters as keyword-only arguments. These filters are forwarded by the
  resource to `_get_page()` and then to transport; they must not be assembled
  as raw payloads by callers. The confirmed experimental filter inventory and
  endpoint-specific behavior are maintained in `devdocs/filter-research.md`.
  Do not assume that every response attribute is a valid filter: unknown keys
  may produce HTTP 400, and Classlife's filter behavior can vary by resource or
  installation.

## API research

- Start with public Classlife sources and keep routes, methods, parameters, examples, and consulted links in `devdocs`.
- Distinguish published facts, inferences, and information pending confirmation in an authorized environment.
- Do not invent endpoints or silently normalize documentation typos; record discrepancies and encapsulate them where necessary.
- Before implementing an endpoint, confirm its HTTP method, authentication, required fields, response codes, and error format.
- For research purposes (not to be confused with integration testing purposes), use the environment file `.env-research.local`. 
Get the values `SAFE_STUDENT_ID` and `SAFE_TEACHER_ID` from there. Those IDs refer to the only student and teacher IDs in that environment that may be edited with PUT/PATCH. 
This authorization does not extend to other records or environments.
- Classlife `metas` are installation-specific extensions. Treat them as opaque mappings and assume no keys, types, requiredness, semantics, or limits for any `metas.<key>` entry.
- Do not copy credentials, personal data, or identifying real responses into `devdocs`.
- Real API fixtures belong only in `devdocs/`, preferably from RESEARCH environment. Before retaining them, anonymize them and remove credentials, real identifiers, personal data, and sensitive values.

## Development workflow

1. Inspect repository state and existing changes first; do not overwrite other work.
2. Make small, reviewable changes.
3. Add or update tests for every new or corrected behavior.
4. Run formatting, linting, tests, and type checks before delivery.
5. Update documentation and the changelog when the API or observable behavior changes.

## Minimum quality

Black is the official formatter. Run it against `src/` and `tests/` targeting
Python 3.11:

```text
python -m black --target-version py311 src tests
```

Formatting does not replace tests, linting, or type checks. Configure the
project tools in `pyproject.toml` for PEP 517/518 builds, formatting, linting,
type checking, tests, coverage, and distribution metadata validation.

Unit tests belong under `tests/unit/`, must not depend on a real Classlife
account, and must run without requiring or loading an `.env` file. Isolate HTTP
with mocks or a test server.

Integration tests belong under `tests/integration/`, require an explicit
environment file, and may use only filenames containing `TEST`. Reject before
any call every filename or configuration indicating `PROD`. Integration tests
are opt-in, must not store credentials in the repository, and must fail clearly
when the required TEST file is absent. Use `scripts/run_tests.py`.

### Test runner

- Unit: `python scripts/run_tests.py unit`.
- Integration: `python scripts/run_tests.py integration --env-file .env-<brand>-test.local`.
- Select exactly one suite per run and load the environment only for integration.
- Unit tests use mocks and no network; integration tests are the only tests allowed to connect to Classlife.
- Reject missing files, names without `TEST`, and names containing `PROD` before pytest starts.
- Keep credential files and temporary runner artifacts ignored by Git.

## API and compatibility

- Centralize HTTP, authentication, timeouts, retries, and errors.
- Do not hide network or API errors; expose contextual custom exceptions without secrets.
- Keep base URL, timeout, and transport configurable where reasonable.
- Document asynchronous operations, pagination, limits, and date formats clearly.
- Follow semantic versioning until the public API is stable.

## Builds and PyPI

- Build releases from a clean checkout.
- Generate both an sdist and a wheel.
- Validate artifacts with `twine check` and inspect their contents.
- Do not publish automatically from a local task or unreviewed change.
- Use TestPyPI for a release candidate and PyPI only after confirming version, changelog, and artifacts.
- Never reuse a published version; increment it according to the change.
- Keep generated artifacts outside version control, normally in `dist/`.

## Security

- Read credentials from environment variables, keyring, or CI secret providers.
- Store local brand/environment secrets in `.env-<brand>-prod.local` and `.env-<brand>-test.local`; all are Git-ignored and must never appear with real values in commits, logs, or artifacts.
- Classlife uses the common base `https://api.classlife.io/api/v1/`. `CLASSLIFE_BASE_URL` is non-secret configuration; the minimum secrets are `CLASSLIFE_API_KEY` and `CLASSLIFE_CLIENT_ID`.
- Resources build routes relative to `DEFAULT_BASE_URL`; never copy internal hosts from the documentation provided by Classlife, since some of them refer to localhost unintentionally.
- PyPI credentials are separate from Classlife credentials: use secure publication configuration, normally `TWINE_USERNAME=__token__` and a token in `TWINE_PASSWORD`.
- Never print tokens or authentication headers.
- Review dependencies and permissions before incorporating external code.
- If a credential appears in logs or files, stop, remove it, and recommend revocation.

## Definition of done

A change is complete when:

- implementation and public API are documented;
- relevant tests pass;
- formatting, linting, and type checks pass or exceptions are justified;
- the build produces installable artifacts accepted by `twine check`;
- no secrets or generated files are in the commit; and
- state and limitations are summarized for the next contributor or agent.
