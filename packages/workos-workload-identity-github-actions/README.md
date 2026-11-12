# workos-workload-identity-github-actions

GitHub Actions identity token provider for [WorkOS](https://workos.com) workload identity federation. It lets a workflow call the WorkOS API without a stored API key: the job's OIDC token is exchanged for a short-lived WorkOS access token.

This package has no dependencies and does not depend on `workos`.

## Install

```bash
pip install workos workos-workload-identity-github-actions
# or: pip install "workos[github-actions]"
```

## Use

The job needs `permissions: id-token: write`.

```python
from workos import WorkOSClient, WorkloadIdentityCredentials
from workos_workload_identity_github_actions import github_actions

client = WorkOSClient(
    credentials=WorkloadIdentityCredentials(
        client_id="client_...",
        token_url="https://.../oauth2/token",
        environment_id="environment_...",
        identity_token_provider=github_actions("https://api.workos.com"),
    )
)
```

`github_actions(audience)` returns a callable that requests a token from `ACTIONS_ID_TOKEN_REQUEST_URL` on every call. The audience must match the audience of the trust rule on your WorkOS application.
