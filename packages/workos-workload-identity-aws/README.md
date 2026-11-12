# workos-workload-identity-aws

AWS identity token provider for [WorkOS](https://workos.com) workload identity federation. It lets a workload on AWS call the WorkOS API without a stored API key: a token from AWS STS (`GetWebIdentityToken`) is exchanged for a short-lived WorkOS access token.

This package depends on `boto3` and does not depend on `workos`.

## Install

```bash
pip install workos workos-workload-identity-aws
# or: pip install "workos[aws]"
```

## Use

The calling identity needs the `sts:GetWebIdentityToken` permission, and outbound identity federation must be enabled for the AWS account.

```python
from workos import WorkOSClient, WorkloadIdentityCredentials
from workos_workload_identity_aws import aws_sts

client = WorkOSClient(
    credentials=WorkloadIdentityCredentials(
        client_id="client_...",
        token_url="https://.../oauth2/token",
        environment_id="environment_...",
        identity_token_provider=aws_sts("https://api.workos.com", region="us-east-1"),
    )
)
```

`aws_sts(audience, region=None)` builds one STS client from the default AWS credential chain and returns a callable that requests an `RS256` token on every call. `region` is optional when boto3 can resolve one (`AWS_DEFAULT_REGION` or the shared config file); with no region, `aws_sts` raises. The request always goes to the regional STS endpoint. The audience must match the audience of the trust rule on your WorkOS application.
