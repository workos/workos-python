# WorkOS Python SDK v6 Migration Guide

This guide covers the main breaking changes from v5 to v6 of the WorkOS Python SDK.

v6 moves the SDK onto the generated client surface, retires most of the old handwritten module layout, and standardizes models, pagination, errors, and request handling. Most upgrades are mechanical, but there are a few places where behavior changed enough that it is worth reviewing your integration carefully.

Read this as the migration guide for the generated-surface major release, not as a statement about the package version currently checked into this branch.

## Table of Contents

- [WorkOS Python SDK v6 Migration Guide](#workos-python-sdk-v6-migration-guide)
  - [Table of Contents](#table-of-contents)
  - [Quick Start](#quick-start)
  - [Breaking Changes](#breaking-changes)
    - [Python 3.10+ is now required](#python-310-is-now-required)
    - [`client_id` is only required for flows that use it](#client_id-is-only-required-for-flows-that-use-it)
    - [Legacy client modules were removed](#legacy-client-modules-were-removed)
    - [SDK models are no longer Pydantic models](#sdk-models-are-no-longer-pydantic-models)
    - [`client.connect` was split into explicit resources](#clientconnect-was-split-into-explicit-resources)
    - [`client.directory_sync` was split into directories, groups, and users](#clientdirectory_sync-was-split-into-directories-groups-and-users)
    - [`client.portal` became `client.admin_portal`](#clientportal-became-clientadmin_portal)
    - [Old `user_management` convenience helpers moved onto sub-resources](#old-user_management-convenience-helpers-moved-onto-sub-resources)
    - [AuthKit authentication helpers now use explicit request bodies](#authkit-authentication-helpers-now-use-explicit-request-bodies)
    - [Some `user_management` methods moved and were renamed](#some-user_management-methods-moved-and-were-renamed)
    - [Permission CRUD moved from `authorization` to `permissions`](#permission-crud-moved-from-authorization-to-permissions)
    - [The deprecated `client.fga` module was removed](#the-deprecated-clientfga-module-was-removed)
    - [Paginated responses are now `SyncPage` / `AsyncPage`](#paginated-responses-are-now-syncpage--asyncpage)
    - [Exception objects expose a more normalized error surface](#exception-objects-expose-a-more-normalized-error-surface)
    - [The SDK now retries certain failures by default](#the-sdk-now-retries-certain-failures-by-default)
  - [Suggested Upgrade Order](#suggested-upgrade-order)
  - [Final Checklist](#final-checklist)

## Quick Start

1. Upgrade to Python 3.10 or newer.
2. Update to the v6 release.
3. Replace legacy imports from `workos.client` and `workos.async_client`.
4. Update any uses of `connect`, `portal`, `directory_sync`, `fga`, `authorization` permission helpers, and old `user_management` convenience helpers.
5. Run your tests and look specifically for import errors, missing methods, and model serialization issues.

## Breaking Changes

### Python 3.10+ is now required

**5.x (old):**

```toml
[project]
requires-python = ">=3.8"
```

**6.x (new):**

```toml
[project]
requires-python = ">=3.10"
```

**Affected users:** Anyone still running Python 3.8 or 3.9 in production, CI, or local development
**Migration:** Upgrade your runtime and CI image to Python 3.10+ before upgrading the SDK

### `client_id` is only required for flows that use it

**5.x (old):**

```python
from workos import WorkOSClient

client = WorkOSClient(api_key="sk_test_123")
```

**6.x (new):**

```python
from workos import WorkOSClient

server_client = WorkOSClient(api_key="sk_test_123")
public_client = WorkOSClient(client_id="client_123")
```

**Affected users:** Anyone using SSO, AuthKit, session helpers, or other flows that depend on a client ID fallback from the SDK client
**Migration:** Keep using `api_key`-only construction for server-side API usage. For flows that need a client ID, pass it explicitly to the method or configure it via `WorkOSClient(client_id=...)` or `WORKOS_CLIENT_ID`. The generated client now requires at least one credential at construction time, not both.

### Legacy client modules were removed

**5.x (old):**

```python
from workos.client import SyncClient
from workos.async_client import AsyncClient

client = SyncClient(api_key="sk_test_123", client_id="client_123")
```

**6.x (new):**

```python
from workos import WorkOSClient, AsyncWorkOSClient

client = WorkOSClient(api_key="sk_test_123", client_id="client_123")
```

**Affected users:** Anyone importing `SyncClient`, `AsyncClient`, or other client classes from legacy client modules
**Migration:** Import clients from the top-level `workos` package instead of `workos.client` or `workos.async_client`

### SDK models are no longer Pydantic models

**5.x (old):**

```python
from workos.types.organizations import Organization

organization = Organization.model_validate(payload)
body = organization.model_dump()
```

**6.x (new):**

```python
from workos.organizations.models import Organization

organization = Organization.from_dict(payload)
body = organization.to_dict()
```

**Affected users:** Anyone calling `model_validate()`, `model_dump()`, or relying on other Pydantic model behavior
**Migration:** Switch to `from_dict()` / `to_dict()` and stop treating SDK models as Pydantic objects

### `client.connect` was split into explicit resources

**5.x (old):**

```python
applications = client.connect.list_applications()
secret = client.connect.create_client_secret("app_123")
```

**6.x (new):**

```python
applications = client.applications.list()
secret = client.application_client_secrets.create("app_123")
```

**Affected users:** Anyone using the old Connect namespace for application or client-secret management
**Migration:** Use `client.applications` for Connect apps and `client.application_client_secrets` for client secret operations

### `client.directory_sync` was split into directories, groups, and users

**5.x (old):**

```python
directories = client.directory_sync.list_directories()
users = client.directory_sync.list_users(directory_id="dir_123")
groups = client.directory_sync.list_groups(user_id="directory_user_123")
```

**6.x (new):**

```python
directories = client.directories.list()
users = client.directory_users.list(directory="dir_123")
groups = client.directory_groups.list(user="directory_user_123")
```

**Affected users:** Anyone using `client.directory_sync`
**Migration:** Replace `directory_sync` calls with `directories`, `directory_users`, and `directory_groups`

### `client.portal` became `client.admin_portal`

**5.x (old):**

```python
link = client.portal.generate_link(
    organization_id="org_123",
    intent="sso",
)
```

**6.x (new):**

```python
link = client.admin_portal.generate_link(
    organization="org_123",
    intent="sso",
)
```

**Affected users:** Anyone generating Admin Portal links through `client.portal`
**Migration:** Move to `client.admin_portal` and rename `organization_id` to `organization`

### Old `user_management` convenience helpers moved onto sub-resources

**5.x (old):**

```python
user = client.user_management.get_user("user_123")

url = client.user_management.get_authorization_url(
    provider="authkit",
    redirect_uri="https://example.com/callback",
)
```

**6.x (new):**

```python
user = client.user_management.users.get_user("user_123")

url = client.user_management.authentication.authorize(
    provider="authkit",
    redirect_uri="https://example.com/callback",
    response_type="code",
    client_id=client.client_id,
)
```

**Affected users:** Anyone calling helper methods directly on `client.user_management`
**Migration:** Use the generated sub-resources like `client.user_management.users` and `client.user_management.authentication`

### AuthKit authentication helpers now use explicit request bodies

**5.x (old):**

```python
auth = client.user_management.authenticate_with_password(
    email="a@b.com",
    password="pw",
)
```

**6.x (new):**

```python
from workos.user_management.authentication.models import (
    PasswordSessionAuthenticateRequest,
)

auth = client.user_management.authentication.authenticate(
    body=PasswordSessionAuthenticateRequest(
        client_id=client.client_id,
        client_secret="sk_test_123",
        grant_type="password",
        email="a@b.com",
        password="pw",
    )
)
```

**Affected users:** Anyone using `authenticate_with_password`, `authenticate_with_code`, `authenticate_with_magic_auth`, `authenticate_with_email_verification`, `authenticate_with_totp`, `authenticate_with_organization_selection`, or `authenticate_with_refresh_token`
**Migration:** Replace old helper methods with `client.user_management.authentication.authenticate(body=...)` using the generated request models or a plain dict

### Some `user_management` methods moved and were renamed

**5.x (old):**

```python
password_reset = client.user_management.create_password_reset("a@b.com")
verification = client.user_management.send_verification_email("user_123")
magic_auth = client.user_management.create_magic_auth(email="a@b.com")
```

**6.x (new):**

```python
password_reset = client.user_management.users.create_password_reset_token(
    email="a@b.com"
)
verification = client.user_management.users.send_verification_email("user_123")
magic_auth = client.user_management.magic_auth.send_magic_auth_code_and_return(
    email="a@b.com"
)
```

**Affected users:** Anyone relying on old flat `user_management` method names
**Migration:** Move calls onto the new sub-resources and update method names where the generated surface uses CRUD-style names

### Permission CRUD moved from `authorization` to `permissions`

**5.x (old):**

```python
permission = client.authorization.create_permission(
    slug="read:foo",
    name="Read Foo",
)
```

**6.x (new):**

```python
permission = client.permissions.create(
    slug="read:foo",
    name="Read Foo",
)
```

**Affected users:** Anyone managing permissions through `client.authorization`
**Migration:** Move permission list/create/get/update/delete calls onto `client.permissions`; keep role and resource operations on `client.authorization`

### The deprecated `client.fga` module was removed

**5.x (old):**

```python
resources = client.fga.list_resources(resource_type="project")
warrants = client.fga.list_warrants(resource_type="project")
check = client.fga.check(...)
```

**6.x (new):**

```python
resources = client.authorization.list_resources(resource_type_slug="project")
assignments = client.authorization.list_role_assignments(
    organization_membership_id="om_123"
)
check = client.authorization.check(
    organization_membership_id="om_123",
    permission_slug="project:read",
    resource_id="proj_123",
)
```

**Affected users:** Anyone using the deprecated `/fga/v1` SDK surface through `client.fga`
**Migration:** Migrate off `client.fga` onto the current Authorization and Permissions APIs. The mapping is not perfectly 1:1: use `client.authorization` for resource, role, and permission checks; use `client.permissions` for permission CRUD; and update call signatures to the generated parameter names like `resource_id`, `resource_external_id`, and `resource_type_slug`

### Paginated responses are now `SyncPage` / `AsyncPage`

**5.x (old):**

```python
from workos.types.list_resource import WorkOSListResource

page = client.organizations.list_organizations()
assert isinstance(page, WorkOSListResource)
```

**6.x (new):**

```python
from workos import SyncPage

page = client.organizations.list()
assert isinstance(page, SyncPage)
```

**Affected users:** Anyone importing or type-checking against `WorkOSListResource`
**Migration:** Replace `WorkOSListResource` with `SyncPage` or `AsyncPage`, and prefer `page.before` / `page.after` over reaching into the old list resource internals

### Exception objects expose a more normalized error surface

**5.x (old):**

```python
from workos import BaseRequestException

try:
    client.organizations.get_organization("org_bad")
except BaseRequestException as exc:
    print(exc.response.status_code)
    print(exc.response_json)
```

**6.x (new):**

```python
from workos import BaseRequestException

try:
    client.organizations.get("org_bad")
except BaseRequestException as exc:
    print(exc.status_code)
    print(exc.request_id)
    print(exc.raw_body)
```

**Affected users:** Anyone using try/except with SDK exceptions and inspecting the old raw response shape
**Migration:** Prefer normalized fields like `status_code`, `message`, `request_id`, `raw_body`, `request_url`, and `request_method`

### The SDK now retries certain failures by default

**5.x (old):**

```python
from workos import WorkOSClient

client = WorkOSClient(api_key="sk_test_123", client_id="client_123")
organization = client.organizations.get_organization("org_123")
```

**6.x (new):**

```python
from workos import WorkOSClient

client = WorkOSClient(
    api_key="sk_test_123",
    max_retries=0,
)
organization = client.organizations.get("org_123")
```

**Affected users:** Anyone with latency-sensitive code paths, custom retry infrastructure, or assumptions about immediate failure on 429/5xx/network issues
**Migration:** Leave retries enabled if you want the new default behavior, or set `max_retries=0` globally or per request to get closer to 5.x behavior

## Suggested Upgrade Order

1. Upgrade Python to 3.10+.
2. Review which flows need `client_id` and either pass it explicitly or configure it on the client / environment.
3. Fix imports from `workos.client` and `workos.async_client`.
4. Replace old namespaces: `connect`, `directory_sync`, `portal`, `fga`, and handwritten `user_management` helpers.
5. Move permission CRUD from `client.authorization` to `client.permissions`.
6. Update model serialization code away from Pydantic helpers.
7. Review retry behavior and set `max_retries=0` where you need strict fail-fast semantics.

## Final Checklist

- No imports from `workos.client`
- No imports from `workos.async_client`
- Client-ID-based flows explicitly pass `client_id` or configure it on the client / environment
- No remaining uses of `client.connect`
- No remaining uses of `client.directory_sync`
- No remaining uses of `client.portal`
- No remaining uses of `client.fga`
- No remaining uses of `client.authorization.create_permission`, `list_permissions`, `get_permission`, `update_permission`, or `delete_permission`
- No remaining uses of removed Pydantic helpers like `model_dump()` or `model_validate()`

Once those are cleaned up, integrations should be in good shape for v6.
