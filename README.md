# WorkOS Python Library

![PyPI](https://img.shields.io/pypi/v/workos)

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

## Workload Identity

A workload running in GitHub Actions, GCP or AWS can call the WorkOS API without a stored API key. The SDK exchanges a JWT issued by the platform for a short-lived WorkOS access token, caches it in memory, and refreshes it before it expires.

Build a `WorkloadIdentityCredentials` and pass it as `credentials` instead of `api_key`:

```python
from workos import WorkOSClient, WorkloadIdentityCredentials
from workos_workload_identity_github_actions import github_actions

client = WorkOSClient(
    credentials=WorkloadIdentityCredentials(
        client_id="client_1234",  # the M2M application's client ID
        token_url="https://.../oauth2/token",  # the token exchange endpoint
        environment_id="environment_1234",
        identity_token_provider=github_actions("https://api.workos.com"),
    )
)

page = client.organizations.list_organizations()
```

`AsyncWorkOSClient` takes the same `credentials` argument. Workload identity is used only when you pass `credentials`: no environment variable switches it on, `WORKOS_API_KEY` is ignored when credentials are passed, and a failed exchange is an error, never a fallback to an API key. Passing both `api_key` and `credentials` raises `ValueError`.

| Argument | Environment variable | Description |
|----------|----------------------|-------------|
| `identity_token_provider` | | A callable that returns the workload's JWT (required) |
| `client_id` | `WORKOS_CLIENT_ID` | The M2M application's client ID (required) |
| `token_url` | `WORKOS_WIF_TOKEN_URL` | The token exchange endpoint (required; there is no default) |
| `environment_id` | `WORKOS_ENVIRONMENT_ID` | The environment ID, sent with every API request (required) |
| `resource` | | The resource to request a token for (defaults to `https://api.workos.com`) |
| `scope` | `WORKOS_WIF_SCOPE` | The scope to request (omitted when unset) |

An explicit argument wins over its environment variable.

### Platform Providers

Each platform's provider is a separate distribution, so the SDK itself gains no dependencies. Install the one you need; installing a provider does not select it.

```bash
pip install "workos[github-actions]"  # workos-workload-identity-github-actions
pip install "workos[gcp]"             # workos-workload-identity-gcp
pip install "workos[aws]"             # workos-workload-identity-aws (depends on boto3)
```

Every provider takes the audience the identity token is requested for. It must match the audience of the trust rule on your WorkOS application; the conventional value is `https://api.workos.com`.

**GitHub Actions.** The job needs `permissions: id-token: write`.

```python
from workos_workload_identity_github_actions import github_actions

provider = github_actions("https://api.workos.com")
```

**GCP.** Uses the default service account's identity token from the metadata server (Compute Engine, GKE, Cloud Run, Cloud Functions).

```python
from workos_workload_identity_gcp import gcp_metadata

provider = gcp_metadata("https://api.workos.com")
```

**AWS.** Calls STS `GetWebIdentityToken` with the default AWS credential chain. The calling identity needs the `sts:GetWebIdentityToken` permission. `region` is optional when boto3 can resolve one.

```python
from workos_workload_identity_aws import aws_sts

provider = aws_sts("https://api.workos.com", region="us-east-1")
```

### Custom Providers

A provider is any callable that returns the JWT as a string. The SDK ships two, and you can pass your own function:

```python
from workos import WorkloadIdentityCredentials, token_env, token_file

# A file, read again on every exchange (for example a projected Kubernetes token)
provider = token_file("/var/run/secrets/tokens/workos")

# An environment variable, read on every exchange
provider = token_env("MY_IDENTITY_TOKEN")

# Your own callable
def provider() -> str:
    return fetch_identity_token_somehow()

# client_id, token_url and environment_id come from the environment here
credentials = WorkloadIdentityCredentials(identity_token_provider=provider)
```

With `AsyncWorkOSClient`, a plain function runs in a worker thread so it cannot block the event loop, and an `async def` provider is awaited.

### Workload Identity Errors

A failed exchange raises `WorkloadIdentityError`. Its `code` is the OAuth error code from the token endpoint (such as `invalid_grant`) or one of `exchange_failed`, `invalid_response`, `provider_failed` and `invalid_configuration`; `hint` says what to check; `description` carries the server's detail when there is any. Neither token ever appears in an error.

```python
from workos import WorkloadIdentityError

try:
    client.organizations.list_organizations()
except WorkloadIdentityError as e:
    print(e.code, e.hint)
```

The exchange is retried on connection failures, 429 and 5xx responses. If the API answers a request with a 401, the SDK discards that token, exchanges again, and retries the request once.

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
| `client.actions` | AuthKit Actions request verification, typed deserialization, and response signing |
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

## AuthKit Actions

[Actions](https://workos.com/docs/authkit/actions) call your endpoint during sign-in or sign-up and wait for a signed verdict. `client.actions.verify_action()` checks the `WorkOS-Signature` header and returns a typed context, and `client.actions.sign_response()` builds the signed reply:

```python
from django.http import HttpResponse, JsonResponse

from workos import WorkOSClient
from workos.actions import ActionType, AuthenticationActionContext

client = WorkOSClient(api_key="sk_1234", client_id="client_1234")
ACTIONS_SECRET = "actions_secret_1234"  # from the Actions page in the WorkOS dashboard

def workos_action(request):
    try:
        action = client.actions.verify_action(
            payload=request.body,  # raw bytes, never a re-serialized dict
            sig_header=request.headers["WorkOS-Signature"],
            secret=ACTIONS_SECRET,
        )
    except ValueError:
        return HttpResponse(status=400)  # invalid signature or stale timestamp

    action_type: ActionType
    if isinstance(action, AuthenticationActionContext):
        action_type = "authentication"
        allowed = action.user.email_verified
    else:  # UserRegistrationActionContext
        action_type = "user_registration"
        allowed = action.user_data.email.endswith("@example.com")

    return JsonResponse(
        client.actions.sign_response(
            action_type=action_type,
            verdict="Allow" if allowed else "Deny",
            error_message=None if allowed else "Not allowed",
            secret=ACTIONS_SECRET,
        )
    )
```

`AuthenticationActionContext` carries the `user`, and the `organization` and `organization_membership` when the sign-in targets one. `UserRegistrationActionContext` carries the submitted `user_data` and the `invitation` being accepted, if any. Both have the `id` of the action execution, the `authentication_method`, and the request's `ip_address`, `user_agent`, `device_fingerprint` and `client_id` where WorkOS has them.

`construct_action()` does the same verification but returns the raw payload as a `dict`, and `verify_header()` only checks the signature. Actions requests older (or newer) than `tolerance` seconds are rejected; it defaults to 30.

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

> **Upgrading to v11?** Iterating a page directly no longer auto-paginates.
> In v11, `for x in page` and `async for x in page` yield only the current
> page's items and make no further requests; `auto_paging_iter()` iterates
> forward across all pages. To migrate, replace `for x in page` with
> `for x in page.auto_paging_iter()` (and `async for x in page` with
> `async for x in page.auto_paging_iter()`).

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

## Feature Flags Runtime Client

The runtime client keeps an environment's feature flag configuration in memory and evaluates flags locally, with no network request per evaluation. It polls the configuration in the background (every 30 seconds by default) with the client's API key, base URL and retry settings. Create one long-lived instance per process and share it across requests. It is for trusted server-side code only.

```python
from workos import WorkOSClient

workos = WorkOSClient(api_key="sk_...")
flags = workos.create_feature_flags_runtime_client()
flags.start()  # polls on a daemon thread
flags.wait_until_ready(timeout=5)  # raises TimeoutError if no configuration arrives

flags.is_enabled("new-checkout", {"user": "user_123", "organization": "org_123"})
flags.is_enabled("new-checkout", {"workspace": "ws_1"}, default=True)
flags.get_all_flags({"organization": "org_123"})  # {"new-checkout": True, ...}

flags.close()  # on shutdown; or use `with workos.create_feature_flags_runtime_client() as flags:`
```

With `AsyncWorkOSClient`, polling runs in an asyncio task: `await flags.start()`, `await flags.wait_until_ready(timeout=5)` and `await flags.close()` (or `async with`). Evaluation stays synchronous.

**Evaluation.** The context maps a target type to the exact, case-sensitive ID being evaluated. `user` and `organization` are target types like any [custom target](https://workos.com/docs/feature-flags/custom-targets) type, and an ID of `None` is skipped. A disabled flag serves its off value. For an enabled flag, the first rule whose conditions all match wins, so a rule serving `False` can exclude a user before a later rule includes their organization; otherwise the flag's default value applies. A missing flag, an unready client, or a flag without a boolean answer returns `default` (`False` unless you pass one), and `get_all_flags` omits flags without an answer. Evaluation never raises: invalid context entries are ignored with a logged warning and the rest is evaluated.

**Failures.** A failed poll keeps the last good configuration and retries with exponential backoff. Transient failures (429, 500, 502, 503, 504, timeouts, connection errors) are also retried within one refresh, up to the client's `max_retries` and within `request_timeout`. A 429's `Retry-After` is honored up to 60 seconds, both by those retries and before the next poll. The async client enforces `request_timeout` exactly. The sync client streams the response and gives every network wait only the time left, so a refresh takes at most `request_timeout` plus one read of a response body that stalls; a custom `HTTPBackend` that is not an httpx client receives the remaining time as its per-request timeout instead. A 401, from a poll or from `refresh()`, stops polling for good: create a new client with a valid API key. Failures are logged to the `workos.feature_flags.runtime` logger (pass `logger=` to use your own) and reported to error listeners. `flags.status` shows readiness, the last error, refresh counts and timestamps, `polling_stopped`, `flag_count` and `cache_age()`.

**Notifications.** `on_change` (or `add_change_listener`) fires after a refresh installs a different configuration, including the first load, with the previous and current snapshots and the changed slugs. `on_error` fires for failed background polls and `on_status` after every refresh. Listeners run one at a time; their exceptions are logged and never affect polling. Async clients also accept coroutine listeners.

**Bootstrap.** Persist the configuration and pass it back to make a new client ready before its first poll:

```python
from workos import FeatureFlagsConfiguration

flags = workos.create_feature_flags_runtime_client(
    bootstrap=FeatureFlagsConfiguration.from_json(cached_json),  # raises on unreadable JSON
    on_change=lambda event: save_cache(event.current.to_json()),
)
```

**Inspection and manual refresh.** `flags.get_flag(slug)` returns a flag's configuration as received, with its rules in order. `flags.refresh()` fetches the configuration immediately, raising on failure, and works without `start()`, e.g. in scripts or serverless functions.

**Processes.** With the SDK's default HTTP client, the sync client polls through an HTTP client of its own and closes it in `close()`; with an HTTP client you supplied, close the runtime client before closing that client. Except on macOS, a runtime client created before a fork (for example in an app gunicorn loads with `--preload`, or that uWSGI loads before forking its workers) can be started in each worker, and a sync client that was already polling resumes on new connections the first time it is used there. That includes a fork that skips Python's fork hooks, as uWSGI's does unless you pass `--py-call-uwsgi-fork-hooks`, since the runtime client checks for a new process each time it is used. If the parent already sent requests through an HTTP client you supplied, or through the `AsyncWorkOSClient`, whether from the runtime client, any other SDK call, or another WorkOS client given the same HTTP client, the runtime client does not poll in the worker: `start()` and `refresh()` raise, it keeps serving its last configuration, and if it was polling it logs a warning the first time it is used. The SDK can't see requests your own code sends through an HTTP client you supplied, so don't use it before forking either. On macOS, once a process has created an HTTP client (every `WorkOSClient` has one), a child it forks can crash when it opens a network connection, so a runtime client created before the fork never polls in a worker there: `start()` logs a warning instead of raising, evaluation serves the bootstrap or last configuration (otherwise your defaults), `refresh()` raises, and so does `wait_until_ready()` without a configuration. Create the `WorkOSClient` and the runtime client after forking instead, for example in gunicorn's `post_fork` hook, or run without `--preload` locally. Background threads must be enabled, so run uWSGI with `--enable-threads`.

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
