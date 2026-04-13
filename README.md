# WorkOS Python Library

![PyPI](https://img.shields.io/pypi/v/workos)
[![Build Status](https://workos.semaphoreci.com/badges/workos-python/branches/main.svg?style=shields&key=9e4cb5bb-86a4-4938-9ec2-fc9f9fc512be)](https://workos.semaphoreci.com/projects/workos-python)

The WorkOS library for Python provides convenient access to the WorkOS API from applications written in Python, [hosted on PyPI](https://pypi.org/project/workos/).

## Documentation

See the [API Reference](https://workos.com/docs/reference/client-libraries) for Python usage examples.

## Installation

```bash
pip install workos
```

## Quick Start

```python
from workos import WorkOSClient

client = WorkOSClient(api_key="sk_1234", client_id="client_1234")

# List organizations
page = client.organizations.list_organizations()
for org in page.auto_paging_iter():
    print(org.name)

# Create an organization
org = client.organizations.create_organizations(name="Acme Corp")
print(org.id)
```

### Async Client

Every method has an identical async counterpart:

```python
from workos import AsyncWorkOSClient

async_client = AsyncWorkOSClient(api_key="sk_1234", client_id="client_1234")

page = await async_client.organizations.list_organizations()
async for org in page.auto_paging_iter():
    print(org.name)
```

### Environment Variables

The client reads credentials from the environment when not passed explicitly:

| Variable | Description |
|----------|-------------|
| `WORKOS_API_KEY` | WorkOS API key |
| `WORKOS_CLIENT_ID` | WorkOS client ID |
| `WORKOS_BASE_URL` | Override the API base URL (defaults to `https://api.workos.com/`) |
| `WORKOS_REQUEST_TIMEOUT` | HTTP timeout in seconds (defaults to `60`) |

## Available Resources

The client exposes the full WorkOS API through typed namespace properties:

| Property | Description |
|----------|-------------|
| `client.sso` | Single Sign-On connections and authorization |
| `client.organizations` | Organization management |
| `client.user_management` | Users, identities, auth methods, invitations |
| `client.directory_sync` | Directory connections and directory users/groups |
| `client.admin_portal` | Admin Portal link generation |
| `client.audit_logs` | Audit log events, exports, and schemas |
| `client.authorization` | Fine-Grained Authorization (FGA) resources, roles, permissions, and checks |
| `client.webhooks` | Webhook event verification |
| `client.feature_flags` | Feature flag evaluation |
| `client.api_keys` | Organization API key management |
| `client.connect` | OAuth application management |
| `client.widgets` | Widget session tokens |
| `client.multi_factor_auth` | MFA enrollment and verification (also available as `client.mfa`) |
| `client.pipes` | Data Integrations |
| `client.radar` | Radar risk scoring |
| `client.passwordless` | Passwordless authentication sessions |
| `client.vault` | Encrypted data vault |

## Pagination

Paginated endpoints return `SyncPage[T]` (or `AsyncPage[T]`) with built-in auto-pagination:

```python
# Iterate through all pages automatically
for user in client.user_management.list_users().auto_paging_iter():
    print(user.email)

# Or work with a single page
page = client.user_management.list_users(limit=10)
print(page.data)        # List of items on this page
print(page.has_more())  # Whether more pages exist
print(page.after)       # Cursor for the next page
```

## Error Handling

All API errors map to typed exception classes with rich context:

```python
from workos._errors import NotFoundError, RateLimitExceededError

try:
    client.organizations.get_organization("org_nonexistent")
except NotFoundError as e:
    print(f"Not found: {e.message}")
    print(f"Request ID: {e.request_id}")
except RateLimitExceededError as e:
    print(f"Retry after: {e.retry_after} seconds")
```

| Exception | Status Code |
|-----------|-------------|
| `BadRequestError` | 400 |
| `AuthenticationError` | 401 |
| `AuthorizationError` | 403 |
| `NotFoundError` | 404 |
| `ConflictError` | 409 |
| `UnprocessableEntityError` | 422 |
| `RateLimitExceededError` | 429 |
| `ServerError` | 5xx |

## Per-Request Options

Every method accepts `request_options` for per-call overrides:

```python
result = client.organizations.list_organizations(
    request_options={
        "timeout": 10,
        "max_retries": 5,
        "extra_headers": {"X-Custom": "value"},
        "idempotency_key": "my-key",
        "base_url": "https://staging.workos.com/",
    }
)
```

## Type Safety

This SDK ships with full type annotations (`py.typed` / PEP 561) and works with mypy, pyright, and IDE autocompletion out of the box. All models are `@dataclass(slots=True)` classes with `from_dict()` / `to_dict()` for serialization.

## SDK Versioning

WorkOS follows [Semantic Versioning](https://semver.org/). Breaking changes are only released in major versions. We strongly recommend reading changelogs before making major version upgrades.

## Beta Releases

WorkOS has features in Beta that can be accessed via Beta releases. We would love for you to try these and share feedback with us before these features reach general availability (GA). To install a Beta version, please follow the [installation steps](#installation) above using the Beta release version.

> **Note:** there can be breaking changes between Beta versions. We recommend pinning the package version to a specific version.

## More Information

- [Single Sign-On Guide](https://workos.com/docs/sso/guide)
- [User Management Guide](https://workos.com/docs/user-management)
- [AuthKit Guide](https://workos.com/docs/authkit)
- [Directory Sync Guide](https://workos.com/docs/directory-sync/guide)
- [Admin Portal Guide](https://workos.com/docs/admin-portal/guide)
- [Audit Logs Guide](https://workos.com/docs/audit-logs)
- [Authorization (FGA) Guide](https://workos.com/docs/fga)
- [Feature Flags Guide](https://workos.com/docs/feature-flags)
- [Webhooks Guide](https://workos.com/docs/webhooks)
- [Radar Guide](https://workos.com/docs/radar)
