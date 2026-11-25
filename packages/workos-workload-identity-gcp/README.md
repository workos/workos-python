# workos-workload-identity-gcp

GCP identity token provider for [WorkOS](https://workos.com) workload identity federation. It lets a workload on GCP (Compute Engine, GKE, Cloud Run, Cloud Functions) call the WorkOS API without a stored API key: the service account's identity token is exchanged for a short-lived WorkOS access token.

This package has no dependencies and does not depend on `workos`.

## Install

```bash
pip install workos workos-workload-identity-gcp
# or: pip install "workos[gcp]"
```

## Use

```python
from workos import WorkOSClient, WorkloadIdentityCredentials
from workos_workload_identity_gcp import gcp_metadata

client = WorkOSClient(
    credentials=WorkloadIdentityCredentials(
        client_id="client_...",
        token_url="https://.../oauth2/token",
        environment_id="environment_...",
        identity_token_provider=gcp_metadata("https://api.workos.com"),
    )
)
```

`gcp_metadata(audience)` returns a callable that requests an identity token for the default service account from the metadata server on every call. The audience must match the audience of the trust rule on your WorkOS application.
