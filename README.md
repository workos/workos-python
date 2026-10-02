# WorkOS Python Library

![PyPI](https://img.shields.io/pypi/v/workos)
[![Build Status](https://workos.semaphoreci.com/badges/workos-python/branches/main.svg?style=shields&key=9e4cb5bb-86a4-4938-9ec2-fc9f9fc512be)](https://workos.semaphoreci.com/projects/workos-python)

The WorkOS library for Python provides convenient access to the WorkOS API from applications written in Python, [hosted on PyPI](https://pypi.org/project/workos/).

## Documentation

See the [API Reference](https://workos.com/docs/reference/client-libraries) for Python usage examples.

## Installation

Requires Python 3.10+.

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
org = client.organizations.create_organization(name="Acme Corp")
print(org.id)
```

### Async Client

Every HTTP API method has an identical async counterpart on `AsyncWorkOSClient`. (Pure-local utilities such as webhook signature verification, Actions helpers, and PKCE are synchronous on both clients.)

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
| `WORKOS_ISSUER` | Expected `iss` claim of session access tokens, comma-separated to accept several (not validated when unset; also settable via `jwt_issuer=`) |

## Available Resources

The client exposes the WorkOS API through typed namespace properties:

| Property | Description |
|----------|-------------|
| `client.sso` | Single Sign-On connections and authorization |
| `client.organizations` | Organization management |
| `client.organization_domains` | Organization domain verification |
| `client.organization_membership` | Organization membership management |
| `client.user_management` | Users, identities, auth methods, invitations |
| `client.directory_sync` | Directory connections and directory users/groups |
| `client.groups` | Organization group management |
| `client.admin_portal` | Admin Portal link generation |
| `client.audit_logs` | Audit log events, exports, and schemas |
| `client.authorization` | Fine-Grained Authorization (FGA) resources, roles, permissions, and checks |
| `client.events` | Events API |
| `client.webhooks` | Webhook endpoint management and event verification |
| `client.feature_flags` | Feature flag management (list, enable/disable, targeting) |
| `client.api_keys` | Organization API key management |
| `client.client_api` | Client API token generation |
| `client.connect` | OAuth application management |
| `client.widgets` | Widget session tokens |
| `client.multi_factor_auth` | MFA enrollment and verification (also available as `client.mfa`) |
| `client.pipes` | Data Integrations |
| `client.pipes_provider` | Organization data integration configuration |
| `client.radar` | Radar risk scoring |
| `client.passwordless` | Passwordless authentication sessions |
| `client.vault` | Encrypted data vault |
| `client.actions` | AuthKit Actions signature verification and response signing |
| `client.pkce` | PKCE code verifier/challenge helpers |

## Webhook Signature Verification

Use `client.webhooks.verify_event()` rather than hand-rolling the HMAC check — it implements the exact scheme WorkOS signs with, and returns the deserialized event:

```python
from django.http import HttpResponse

from workos import WorkOSClient

client = WorkOSClient(api_key="sk_1234", client_id="client_1234")

# In a Django view (Flask: request.get_data() / request.headers)
def workos_webhook(request):
    try:
        event = client.webhooks.verify_event(
            event_body=request.body,  # raw bytes, never a re-serialized dict
            event_signature=request.headers["WorkOS-Signature"],
            secret="wh_secret_1234",  # endpoint secret from the WorkOS dashboard
        )
    except ValueError:
        return HttpResponse(status=400)  # invalid signature or stale timestamp

    print(event.event, event.id)
    return HttpResponse(status=200)
```

`verify_header()` does the same check without deserializing, for payloads you want to handle yourself.

The `WorkOS-Signature` header is formatted `t=<unix-timestamp-ms>, v1=<hex-sha256>` — note the `, ` separator — and `v1` is the HMAC-SHA256 of `"{timestamp}.{raw body}"` keyed with the endpoint secret. Events older (or newer) than `tolerance` seconds are rejected; it defaults to 180. Verification is local and synchronous, so it works the same on `AsyncWorkOSClient`.

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
from workos import NotFoundError, RateLimitExceededError

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

## Retries

The client automatically retries requests up to 3 times (configurable via the `max_retries` request option) on 429 and 5xx responses, timeouts, and connection errors, using exponential backoff with jitter and honoring `Retry-After`. The SDK attaches an auto-generated `Idempotency-Key` (UUID v4) to every `POST` request and reuses the same key across its internal retries.

## HTTP Backends

The SDK sends requests through [`httpx2`](https://pypi.org/project/httpx2/) by default. Pass your own configured client as `http_client` to control proxies, TLS, connection limits, or transports:

```python
import httpx2
from workos import AsyncWorkOSClient, WorkOSClient

client = WorkOSClient(
    api_key="sk_...",
    http_client=httpx2.Client(proxy="http://proxy.internal:3128", verify="/etc/ssl/corp.pem"),
)

async_client = AsyncWorkOSClient(
    api_key="sk_...",
    http_client=httpx2.AsyncClient(limits=httpx2.Limits(max_connections=20)),
)
```

`httpx` 0.28 clients are accepted as well; the two libraries share an API. The SDK closes only clients it created. A client you pass in stays open after `client.close()`, so close it yourself when you are done with it.

### Custom backends

Any object implementing `workos.HTTPBackend` (or `workos.AsyncHTTPBackend` for the async client) can be passed as `http_client`. The SDK hands the backend a fully built URL, the final headers, an optional `bytes` body, and a timeout in seconds, and expects a `workos.HTTPResponse` back. Raise `workos.TransportTimeout`, `workos.TransportConnectError`, or `workos.TransportError` for network failures so the SDK's retry logic can handle them. The `headers` mapping on the response must be case-insensitive.

The following `aiohttp` adapter is an example, not a supported part of the SDK:

```python
import asyncio

import aiohttp
import yarl

from workos import (
    AsyncWorkOSClient,
    HTTPResponse,
    TransportConnectError,
    TransportError,
    TransportTimeout,
)


class AiohttpBackend:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def request(self, method, url, *, headers, content, timeout) -> HTTPResponse:
        try:
            async with self._session.request(
                method,
                yarl.URL(url, encoded=True),  # keep the SDK's percent-encoding intact
                headers=headers,
                data=content,
                timeout=aiohttp.ClientTimeout(total=timeout),
                allow_redirects=True,
            ) as resp:
                body = await resp.read()
                return HTTPResponse(resp.status, resp.headers, body, method, str(resp.url))
        except (asyncio.TimeoutError, aiohttp.ServerTimeoutError) as exc:  # before connection errors
            raise TransportTimeout(str(exc)) from exc
        except aiohttp.ClientConnectionError as exc:
            raise TransportConnectError(str(exc)) from exc
        except aiohttp.ClientError as exc:
            raise TransportError(str(exc)) from exc

    async def close(self) -> None:
        await self._session.close()


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        client = AsyncWorkOSClient(api_key="sk_...", http_client=AiohttpBackend(session))
        page = await client.organizations.list_organizations()
```

## Per-Request Options

Every API method accepts `request_options` for per-call overrides (local helpers such as webhook/Actions signature verification and PKCE utilities do not make HTTP calls and don't take `request_options`):

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

> [!NOTE]
> The WorkOS API currently honors `Idempotency-Key` only on the [Create Audit Log Event](https://workos.com/docs/reference/audit-logs/event) endpoint (`audit_logs.create_event`). Other endpoints accept the header but do not deduplicate requests, so a retried mutation elsewhere can still create a duplicate.

## Type Safety

This SDK ships with full type annotations (`py.typed` / PEP 561) and works with mypy, pyright, and IDE autocompletion out of the box. All API resource models are `@dataclass(slots=True)` classes with `from_dict()` / `to_dict()` for serialization.

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
