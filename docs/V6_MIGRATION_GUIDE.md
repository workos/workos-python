# WorkOS Python SDK v6 Migration Guide

This guide describes the upgrade pattern for the v6 release in this branch.

The important theme is that v6 is primarily a client architecture migration, not a full product-surface reset. Most of the familiar product namespaces remain available, but the SDK now sits on a generated client with new models, new pagination types, normalized errors, built-in retries, and much stronger sync/async parity.

## Table of Contents

- [WorkOS Python SDK v6 Migration Guide](#workos-python-sdk-v6-migration-guide)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [What Stays Familiar](#what-stays-familiar)
  - [Breaking Changes](#breaking-changes)
    - [Python 3.10+ is now required](#python-310-is-now-required)
    - [Old client module paths were removed](#old-client-module-paths-were-removed)
    - [Client construction is less strict](#client-construction-is-less-strict)
    - [`portal` became `admin_portal`](#portal-became-admin_portal)
    - [`fga` is removed](#fga-is-removed)
    - [Models are no longer Pydantic models](#models-are-no-longer-pydantic-models)
    - [Model imports moved out of `workos.types`](#model-imports-moved-out-of-workostypes)
    - [Paginated responses now use `SyncPage` / `AsyncPage`](#paginated-responses-now-use-syncpage--asyncpage)
    - [Exception classes were renamed and normalized](#exception-classes-were-renamed-and-normalized)
    - [Requests now retry by default](#requests-now-retry-by-default)
  - [New Additions and Benefits](#new-additions-and-benefits)
  - [API Parity Notes](#api-parity-notes)
  - [Suggested Upgrade Order](#suggested-upgrade-order)
  - [Migration Checklist](#migration-checklist)

## Executive Summary

The shortest possible summary is:

1. Keep `WorkOSClient` / `AsyncWorkOSClient` imports (these names are unchanged from v5).
2. Remove any imports from the old `workos.client` or `workos.async_client` modules (use `from workos import WorkOSClient` instead).
3. Keep most existing product namespace calls as-is.
4. Rename `client.portal` to `client.admin_portal`.
5. Remove any use of `client.fga`.
6. Update model imports and serialization code away from `workos.types.*` and Pydantic.
7. Review exception handling and retry assumptions.

## What Stays Familiar

v6 keeps a high degree of product-surface continuity.

These namespaces still exist on the client:

- `api_keys`
- `audit_logs`
- `authorization`
- `connect`
- `directory_sync`
- `events`
- `organization_domains`
- `organizations`
- `passwordless`
- `pipes`
- `sso`
- `user_management`
- `webhooks`
- `widgets`
- `vault`

Several high-value convenience helpers also remain available:

- `client.mfa` still works as an alias for `client.multi_factor_auth`
- `client.user_management.load_sealed_session(...)`
- `client.user_management.authenticate_with_password(...)`
- `client.user_management.get_authorization_url_with_pkce(...)`
- `client.sso.get_authorization_url_with_pkce(...)`

That means many integrations can upgrade with mostly import, model, and error-handling changes rather than a wholesale rewrite of API calls.

## Breaking Changes

### Python 3.10+ is now required

v5 supported Python 3.8+.

v6 requires Python 3.10+.

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

**Migration:** Upgrade local dev, CI, and production runtimes before taking the SDK upgrade.

### Old client module paths were removed

The client class names `WorkOSClient` and `AsyncWorkOSClient` are unchanged from v5. However, the old module paths `workos.client` and `workos.async_client` are gone.

**v5**

```python
from workos.client import WorkOSClient          # old module path
from workos.async_client import AsyncWorkOSClient  # old module path
```

**v6**

```python
from workos import WorkOSClient, AsyncWorkOSClient  # top-level import
```

**Migration:** If you were importing from `workos.client` or `workos.async_client`, update to the top-level import. If you were already using `from workos import WorkOSClient`, no change is needed.

### Client construction is less strict

v5 required both an API key and a client ID at construction time.

v6 requires at least one of them.

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

**Migration:** Keep passing both values if that matches your app today. If you have server-only usage, you can now construct a client with only `api_key`. If you have client-ID-driven flows, make sure a `client_id` is still available wherever those flows run.

### `portal` became `admin_portal`

This is one of the few product-namespace renames that users are likely to hit directly.

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

**Migration:** Rename `client.portal` to `client.admin_portal`. While doing that, also update `organization_id=` to `organization=` for `generate_link(...)`.

### `fga` is removed

The old `client.fga` surface is no longer present in v6.

**Migration:** Any remaining FGA usage needs to stay on v5 for now or be migrated separately before adopting v6.

### Models are no longer Pydantic models

v5 models exposed Pydantic APIs like `model_validate()` and `model_dump()`.

v6 models are generated dataclass-style objects with `from_dict()` and `to_dict()`.

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

**Migration:** Replace Pydantic-specific helpers and stop depending on Pydantic behaviors such as validators, `model_dump()`, or `model_validate()`.

### Model imports moved out of `workos.types`

The broad `workos.types.*` tree is gone.

Use resource-local `models` packages instead, plus `workos.common.models` for shared enums and common DTOs.

**v5**

```python
from workos.types.organizations.organization import Organization
from workos.types.portal.portal_link_intent import PortalLinkIntent
```

**v6**

```python
from workos.organizations.models import Organization
from workos.common.models import GenerateLinkDtoIntent
```

**Migration:** Move imports to `workos.<resource>.models` wherever possible. If you are importing a shared enum or common helper type, look in `workos.common.models`.

### Paginated responses now use `SyncPage` / `AsyncPage`

List endpoints now return page objects with cursor metadata and built-in iteration helpers.

**v6**

```python
page = client.organizations.list()

for organization in page:
    print(organization.id)

assert page.before is None or isinstance(page.before, str)
assert page.after is None or isinstance(page.after, str)
```

**Migration:** If your code expected a custom handwritten list wrapper, update it to work with `SyncPage` or `AsyncPage`.

### Exception classes were renamed and normalized

The old exception classes used `*Exception` names. v6 uses `*Error` names and exposes a more consistent set of fields.

Representative mapping:

- `BadRequestException` -> `BadRequestError`
- `AuthenticationException` -> `AuthenticationError`
- `AuthorizationException` -> `AuthorizationError`
- `NotFoundException` -> `NotFoundError`
- `ConflictException` -> `ConflictError`
- `ServerException` -> `ServerError`

v6 also adds clearer runtime exceptions such as:

- `ConfigurationError`
- `UnprocessableEntityError`
- `RateLimitExceededError`
- `WorkOSConnectionError`
- `WorkOSTimeoutError`

Exception instances now consistently expose fields such as:

- `status_code`
- `message`
- `request_id`
- `code`
- `param`
- `raw_body`
- `request_url`
- `request_method`

**Migration:** Update imports, rename caught exception classes, and review any code that inspects exception attributes.

### Requests now retry by default

The generated client retries certain failures by default, including common 5xx and rate-limit responses.

If your v5 integration assumed immediate failure, this is a behavior change.

**v6**

```python
client = WorkOSClient(api_key="sk_test_123", max_retries=0)
```

Per-request overrides are also available through `RequestOptions`.

```python
from workos import WorkOSClient

client = WorkOSClient(api_key="sk_test_123")

client.organizations.list(
    request_options={
        "timeout": 5,
        "max_retries": 0,
    }
)
```

**Migration:** Set `max_retries=0` if you need fail-fast behavior during rollout or in latency-sensitive paths.

## New Additions and Benefits

The v6 branch is not only a migration cost. It also improves the SDK in ways that are visible to users:

- Higher API parity with the WorkOS API because the client surface is generated from the spec rather than maintained endpoint-by-endpoint by hand.
- Stronger sync/async parity. In v5, several areas were unavailable or incomplete in the async client. In v6, async support is much broader and more consistent.
- A normalized request stack built on `httpx`, with retries, timeout handling, connection handling, and automatic POST idempotency keys.
- Consistent generated model behavior across products with `from_dict()` / `to_dict()`.
- Dedicated pagination primitives with cursor metadata and automatic iteration.
- New or newly first-class surfaces such as `radar`, plus hand-maintained helper utilities like `actions` and `pkce`.
- Broader generated tests, including model round-trip coverage.

## API Parity Notes

For most existing integrations, the parity story is better than the old draft guide implied.

What is largely unchanged:

- The major product namespaces most users call today are still present.
- Many convenience helpers remain in place.
- The SDK still offers both sync and async clients.
- Core request flows still target the same HTTP API paths and data model.

What changed for parity in a positive direction:

- The async client is no longer missing large parts of the product surface such as Admin Portal, MFA, Webhooks, Widgets, Vault, and Passwordless.
- Generated resources and models make it easier to keep the SDK aligned with the public API over time.

What still requires migration work:

- old `workos.client` / `workos.async_client` module paths
- `portal` to `admin_portal`
- removal of `fga`
- model import and serialization changes
- exception name changes

## Suggested Upgrade Order

1. Upgrade Python to 3.10+.
2. Update any `from workos.client import WorkOSClient` to `from workos import WorkOSClient`.
3. Rename `client.portal` usages to `client.admin_portal`.
4. Find and remove any `client.fga` usage.
5. Replace `workos.types.*` imports with `workos.<resource>.models` or `workos.common.models`.
6. Replace `model_validate()` / `model_dump()` with `from_dict()` / `to_dict()`.
7. Update exception imports and any code matching on exception names or attributes.
8. Review retry-sensitive call sites and set `max_retries=0` where appropriate.
9. Run sync and async test suites and look for import errors, attribute errors, and serialization mismatches.

## Migration Checklist

- Python runtime is 3.10+
- `workos.client` and `workos.async_client` module imports are updated to `from workos import WorkOSClient, AsyncWorkOSClient`
- `client.portal` usages are renamed to `client.admin_portal`
- `client.fga` usages are removed or isolated from the v6 upgrade
- `workos.types.*` imports are gone
- Pydantic-only model helpers are gone
- Exception imports use v6 `*Error` names
- Retry behavior has been reviewed explicitly
- Sync and async integration tests pass
