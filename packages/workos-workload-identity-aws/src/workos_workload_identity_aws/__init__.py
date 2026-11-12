# @oagen-ignore-file

"""AWS identity token provider for WorkOS workload identity federation.

``aws_sts(audience, region)`` returns a callable that asks AWS STS
(``GetWebIdentityToken``) for a JWT representing the calling AWS identity. Pass
it to ``workos.WorkloadIdentityCredentials(identity_token_provider=...)``.

The provider keeps no cache and does no retries; the WorkOS SDK retries the
call as part of the token exchange.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

import boto3
import botocore.session
from botocore.exceptions import BotoCoreError, ClientError

if TYPE_CHECKING:
    from types_boto3_sts.client import STSClient

__all__ = ["AwsStsProviderError", "aws_sts"]

_SIGNING_ALGORITHM = "RS256"
_GLOBAL_ENDPOINT_HOSTS = ("sts.amazonaws.com",)


class AwsStsProviderError(Exception):
    """AWS STS did not return a web identity token."""


def _create_sts_client(region: Optional[str]) -> "STSClient":
    """Build an STS client on the regional endpoint for ``region``.

    Credentials come from the AWS SDK's default chain. The region is the
    argument, else whatever boto3 resolves (``AWS_DEFAULT_REGION`` or the
    shared config file).
    """
    core_session = botocore.session.get_session()
    # GetWebIdentityToken is not served by the global endpoint. Force the
    # regional one even when AWS_STS_REGIONAL_ENDPOINTS=legacy is set.
    core_session.set_config_variable("sts_regional_endpoints", "regional")
    session = boto3.Session(botocore_session=core_session)
    resolved = region or session.region_name
    if not resolved:
        raise AwsStsProviderError(
            "No AWS region is configured. Pass region to aws_sts() or set "
            "AWS_DEFAULT_REGION; sts:GetWebIdentityToken needs a regional STS "
            "endpoint."
        )
    # The stubs type every service's client; only the STS one is installed.
    client: STSClient = session.client("sts", region_name=resolved)  # pyright: ignore[reportUnknownMemberType]
    endpoint = client.meta.endpoint_url
    if any(endpoint.endswith(f"//{host}") for host in _GLOBAL_ENDPOINT_HOSTS):
        raise AwsStsProviderError(
            f"AWS region {resolved!r} resolves to the global STS endpoint; "
            "sts:GetWebIdentityToken needs a regional STS endpoint."
        )
    return client


def aws_sts(audience: str, region: Optional[str] = None) -> Callable[[], str]:
    """Return a provider of AWS STS web identity tokens for ``audience``.

    The calling identity needs the ``sts:GetWebIdentityToken`` permission, and
    outbound identity federation must be enabled for the account. The
    conventional audience is ``https://api.workos.com``.

    Raises ``AwsStsProviderError`` here, not on first use, when no region can
    be resolved.
    """
    if not audience:
        raise ValueError("audience is required")
    # Built once; the provider reuses it on every call.
    client = _create_sts_client(region)

    def provider() -> str:
        try:
            response = client.get_web_identity_token(
                Audience=[audience], SigningAlgorithm=_SIGNING_ALGORITHM
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code") or "UnknownError"
            raise AwsStsProviderError(
                f"sts:GetWebIdentityToken failed with {code}."
            ) from None
        except BotoCoreError as exc:
            raise AwsStsProviderError(
                f"sts:GetWebIdentityToken failed with {type(exc).__name__}."
            ) from None
        token = response.get("WebIdentityToken")
        if not token:
            raise AwsStsProviderError("sts:GetWebIdentityToken returned no token.")
        return token

    return provider
