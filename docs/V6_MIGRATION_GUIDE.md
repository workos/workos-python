# WorkOS Python SDK v6 Migration Guide

This guide focuses on the code you are most likely to change when upgrading from v5 to v6 in this branch.

v6 is still recognizably the WorkOS Python SDK, but it moves onto a generated client and runtime. The highest-friction changes are import path updates, the `portal` to `admin_portal` rename, the removal of `fga`, the shift away from Pydantic model helpers, and the new error and retry behavior.

## TL;DR

1. Upgrade to Python 3.10+.
2. Replace any `workos.client` or `workos.async_client` imports with top-level imports from `workos`.
3. Rename `client.portal` to `client.admin_portal`.
4. Remove any `client.fga` usage before upgrading.
5. Replace Pydantic-specific model code such as `model_validate()` and `model_dump()`.
6. Review exception handling, pagination assumptions, and retry-sensitive call sites.

## HIGH Impact Changes

### Python 3.10+ is now required

**v5**

```toml
[project]
requires-python = ">=3.8"
```

**v6**

```toml
[project]
requires-python = ">=3.10"
```

**Affected users:** Any application, worker, CI job, or deploy target still pinned to Python 3.8 or 3.9.

**Migration:** Upgrade your runtime before taking the SDK upgrade.

### Old client module paths were removed

The client class names are unchanged, but the old module paths are gone.

**v5**

```python
from workos.client import WorkOSClient
from workos.async_client import AsyncWorkOSClient
```

**v6**

```python
from workos import WorkOSClient, AsyncWorkOSClient
```

**Affected users:** Anyone importing from `workos.client` or `workos.async_client`.

**Migration:** Move client imports to `from workos import WorkOSClient, AsyncWorkOSClient`.

### `portal` became `admin_portal`

This is the most visible service rename in v6. The `generate_link` argument also changed from `organization_id` to `organization`.

**v5**

```python
link = client.portal.generate_link(
    organization_id="org_123",
    intent="sso",
)
```

**v6**

```python
link = client.admin_portal.generate_link(
    organization="org_123",
    intent="sso",
)
```

**Affected users:** Anyone generating Admin Portal links.

**Migration:** Rename `client.portal` to `client.admin_portal` and update `organization_id=` to `organization=`.

### `fga` is removed

There is no `client.fga` accessor in v6.

**v5**

```python
fga = client.fga
```

**v6**

```python
# No v6 replacement is available in this branch.
```

**Affected users:** Any integration still using the FGA surface.

**Migration:** Keep that integration on v5 for now, or split the FGA migration from the v6 SDK upgrade.

### Models are no longer Pydantic models

Generated models now use `from_dict()` and `to_dict()` instead of Pydantic APIs.

**v5**

```python
from workos.types.audit_logs.audit_log_event import AuditLogEvent

event = AuditLogEvent.model_validate(payload)
body = event.model_dump()
```

**v6**

```python
from workos.audit_logs.models import AuditLogEvent

event = AuditLogEvent.from_dict(payload)
body = event.to_dict()
```

**Affected users:** Anyone calling `model_validate()`, `model_dump()`, or relying on Pydantic-specific behavior.

**Migration:** Replace Pydantic helpers with `from_dict()` and `to_dict()`, and remove any dependence on Pydantic validators or BaseModel APIs.

### Exception classes were renamed and normalized

The old `*Exception` naming is replaced with `*Error`, and the runtime now exposes more structured SDK-native errors.

**v5**

```python
from workos.exceptions import NotFoundException

try:
    client.organizations.get_organization("org_123")
except NotFoundException:
    ...
```

**v6**

```python
from workos import NotFoundError

try:
    client.organizations.get_organization("org_123")
except NotFoundError as exc:
    request_id = exc.request_id
    status_code = exc.status_code
```

Representative renames:

- `BadRequestException` -> `BadRequestError`
- `AuthenticationException` -> `AuthenticationError`
- `AuthorizationException` -> `AuthorizationError`
- `NotFoundException` -> `NotFoundError`
- `ConflictException` -> `ConflictError`
- `ServerException` -> `ServerError`

v6 also exposes runtime and auth-flow specific errors such as:

- `ConfigurationError`
- `UnprocessableEntityError`
- `RateLimitExceededError`
- `WorkOSConnectionError`
- `WorkOSTimeoutError`
- `EmailVerificationRequiredError`
- `MfaEnrollmentError`
- `MfaChallengeError`
- `OrganizationSelectionRequiredError`
- `SsoRequiredError`

**Affected users:** Anyone using `try`/`except` with SDK exceptions or inspecting exception attributes.

**Migration:** Rename caught exception classes, update imports, and review any code that depends on old exception names or attributes.

## MEDIUM Impact Changes

### Paginated list responses now use `SyncPage` and `AsyncPage`

List endpoints now return typed page wrappers with cursor metadata and built-in auto-pagination.

**v6**

```python
page = client.organizations.list_organizations()

for organization in page:
    print(organization.id)

assert page.before is None or isinstance(page.before, str)
assert page.after is None or isinstance(page.after, str)
```

**v6 async**

```python
page = await async_client.organizations.list_organizations()

items = [organization async for organization in page]
```

**Affected users:** Any code that expected a handwritten list wrapper or manually handled pagination state differently.

**Migration:** Update pagination code to work with `SyncPage` or `AsyncPage`, and use `page.data`, `page.before`, `page.after`, or iteration over the page as needed.

### Requests now retry by default

The generated runtime retries retryable failures by default, including `429` and common `5xx` responses.

**v6**

```python
from workos import WorkOSClient

client = WorkOSClient(api_key="sk_test_123", max_retries=0)
```

Per-request overrides are available through `request_options`.

```python
from workos import WorkOSClient

client = WorkOSClient(api_key="sk_test_123")

client.organizations.list_organizations(
    request_options={
        "timeout": 5,
        "max_retries": 0,
    }
)
```

**Affected users:** Latency-sensitive code paths, fail-fast integrations, and any callers that assumed immediate failure after a single request attempt.

**Migration:** Review retry-sensitive call sites and set `max_retries=0` at the client or request level where fail-fast behavior is required.

### Client construction is less strict, but some config failures may move to call sites

v6 accepts either an API key or a client ID at client construction time.

**v5**

```python
from workos import WorkOSClient

client = WorkOSClient(api_key="sk_test_123", client_id="client_123")
```

**v6**

```python
from workos import WorkOSClient

server_client = WorkOSClient(api_key="sk_test_123")
public_client = WorkOSClient(client_id="client_123")
hybrid_client = WorkOSClient(api_key="sk_test_123", client_id="client_123")
```

Operations that require a missing credential now raise `ConfigurationError` when called.

**Affected users:** Code that relied on constructor-time validation to prove both credentials were present for all later operations.

**Migration:** Keep passing both values if that matches your app today, and audit flows that require `api_key` or `client_id` so missing-config errors do not surprise you at request time.

## LOW Impact Changes

### Model import paths changed, but `workos.types.<resource>` compatibility barrels still exist

v6 prefers resource-local model imports such as `workos.organizations.models` and shared types in `workos.common.models`.

Package-level compatibility imports under `workos.types.<resource>` still exist in this branch. The bigger break is that old per-model module paths are no longer the preferred shape.

**v5**

```python
from workos.types.organizations.organization import Organization
from workos.types.portal.portal_link_intent import PortalLinkIntent
```

**v6**

```python
from workos.organizations.models import Organization
from workos.common.models import GenerateLinkIntent
```

Temporary compatibility still works for package-level imports:

```python
from workos.types.organizations import Organization
```

**Affected users:** Anyone importing individual model modules from the old `workos.types.*` tree.

**Migration:** Prefer `workos.<resource>.models` and `workos.common.models` for new code. If you need a lower-friction rollout, package-level `workos.types.<resource>` imports can bridge part of the migration in this branch.

## What's Preserved

- `WorkOSClient` and `AsyncWorkOSClient` remain the top-level client names.
- Most familiar service namespaces remain available, including `api_keys`, `audit_logs`, `authorization`, `connect`, `directory_sync`, `events`, `organization_domains`, `organizations`, `passwordless`, `pipes`, `sso`, `user_management`, `webhooks`, `widgets`, and `vault`.
- `client.mfa` still works as an alias for `client.multi_factor_auth`.
- High-value helpers remain available, including `client.user_management.load_sealed_session(...)`, `client.user_management.authenticate_with_password(...)`, `client.user_management.get_authorization_url_with_pkce(...)`, and `client.sso.get_authorization_url_with_pkce(...)`.
- Client configuration is still instance-scoped.
- Per-request options are supported and include `extra_headers`, `timeout`, `max_retries`, `base_url`, and `idempotency_key`.
- The runtime raises SDK-native errors instead of leaking raw `httpx` exceptions as the primary public contract.
- Retry handling honors `Retry-After` when present.
- POST requests automatically receive an idempotency key when one is not provided.
- Auto-pagination is wired and fetches subsequent pages.

## Suggested Upgrade Order

1. Upgrade Python to 3.10+ in local development, CI, and production.
2. Replace `workos.client` and `workos.async_client` imports with top-level imports from `workos`.
3. Rename `client.portal` usages to `client.admin_portal`.
4. Find and remove any `client.fga` usage.
5. Replace `model_validate()` and `model_dump()` with `from_dict()` and `to_dict()`.
6. Update exception imports and any code that catches or inspects SDK errors.
7. Audit pagination code that depends on the old list wrapper shape.
8. Review retry-sensitive call sites and set `max_retries=0` where required.
9. Migrate old model imports toward `workos.<resource>.models` and `workos.common.models`.
10. Run sync and async integration tests and look for import errors, attribute errors, serialization mismatches, and changed retry behavior.

## Searches To Run

```sh
rg 'workos\.client|workos\.async_client|client\.portal|client\.fga|model_dump|model_validate|Exception|workos\.types'
```

## Migration Checklist

- Python runtime is 3.10+.
- Client imports no longer use `workos.client` or `workos.async_client`.
- `client.portal` usages are renamed to `client.admin_portal`.
- `client.fga` usage is removed or isolated from the v6 upgrade.
- Pydantic-only model helpers are gone.
- Exception imports use v6 `*Error` names.
- Retry behavior has been reviewed explicitly.
- Pagination code has been updated where needed.
- Model imports are moving toward `workos.<resource>.models` and `workos.common.models`.
- Sync and async integration tests pass.
