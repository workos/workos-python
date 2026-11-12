# @oagen-ignore-file

"""Conformance cases WIF-AWS-01 and WIF-AWS-02.

The STS client is the real boto3 client with a botocore ``Stubber`` attached,
so parameter names are validated against the service model and no request
leaves the process.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Optional

import pytest
from botocore.stub import Stubber

import workos_workload_identity_aws as aws
from workos_workload_identity_aws import AwsStsProviderError, aws_sts

if TYPE_CHECKING:
    from types_boto3_sts.client import STSClient

AUDIENCE = "https://api.workos.com"
EXPECTED_PARAMS = {"Audience": [AUDIENCE], "SigningAlgorithm": "RS256"}


@pytest.fixture(autouse=True)
def isolated_aws_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """No region, profile or config from the machine running the tests."""
    for name in (
        "AWS_REGION",
        "AWS_DEFAULT_REGION",
        "AWS_PROFILE",
        "AWS_DEFAULT_PROFILE",
        "AWS_STS_REGIONAL_ENDPOINTS",
        "AWS_ENDPOINT_URL",
        "AWS_ENDPOINT_URL_STS",
    ):
        monkeypatch.delenv(name, raising=False)
    empty = tmp_path / "aws-empty"
    empty.write_text("")
    monkeypatch.setenv("AWS_CONFIG_FILE", str(empty))
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(empty))
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret-key")


class StubbedSts:
    """Wraps the provider's client builder so each built client is stubbed."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.clients: List["STSClient"] = []
        self.stubbers: List[Stubber] = []
        self._queue: List[Callable[[Stubber], None]] = []
        real_create = aws._create_sts_client  # pyright: ignore[reportPrivateUsage]

        def create(region: Optional[str]) -> "STSClient":
            client = real_create(region)
            stubber = Stubber(client)
            for add in self._queue:
                add(stubber)
            stubber.activate()
            self.clients.append(client)
            self.stubbers.append(stubber)
            return client

        monkeypatch.setattr(aws, "_create_sts_client", create)

    def returns(self, token: str) -> None:
        self._queue.append(
            lambda stubber: stubber.add_response(
                "get_web_identity_token",
                {
                    "WebIdentityToken": token,
                    "Expiration": datetime.datetime(
                        2030, 1, 1, tzinfo=datetime.timezone.utc
                    ),
                },
                EXPECTED_PARAMS,
            )
        )

    def fails(self, code: str, message: str, status: int) -> None:
        self._queue.append(
            lambda stubber: stubber.add_client_error(
                "get_web_identity_token",
                service_error_code=code,
                service_message=message,
                http_status_code=status,
                expected_params=EXPECTED_PARAMS,
            )
        )


@pytest.fixture
def sts(monkeypatch: pytest.MonkeyPatch) -> StubbedSts:
    return StubbedSts(monkeypatch)


def test_WIF_AWS_01_calls_get_web_identity_token_on_a_regional_endpoint(
    sts: StubbedSts,
) -> None:
    sts.returns("aws-jwt")

    provider = aws_sts(AUDIENCE, region="us-east-1")

    assert provider() == "aws-jwt"
    # The stubber rejects any call whose parameters differ from EXPECTED_PARAMS:
    # one call, audience https://api.workos.com, signing algorithm RS256.
    sts.stubbers[0].assert_no_pending_responses()
    assert len(sts.clients) == 1
    client = sts.clients[0]
    assert client.meta.region_name == "us-east-1"
    assert client.meta.endpoint_url == "https://sts.us-east-1.amazonaws.com"


def test_WIF_AWS_01_builds_the_client_once(sts: StubbedSts) -> None:
    sts.returns("aws-jwt-1")
    sts.returns("aws-jwt-2")

    provider = aws_sts(AUDIENCE, region="eu-west-1")

    assert [provider(), provider()] == ["aws-jwt-1", "aws-jwt-2"]
    assert len(sts.clients) == 1
    assert sts.clients[0].meta.endpoint_url == "https://sts.eu-west-1.amazonaws.com"


def test_WIF_AWS_01_stays_regional_under_the_legacy_endpoint_setting(
    sts: StubbedSts, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AWS_STS_REGIONAL_ENDPOINTS", "legacy")

    aws_sts(AUDIENCE, region="us-east-1")

    assert sts.clients[0].meta.endpoint_url == "https://sts.us-east-1.amazonaws.com"


def test_WIF_AWS_01_region_falls_back_to_what_the_aws_sdk_resolves(
    sts: StubbedSts, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AWS_DEFAULT_REGION", "ap-southeast-2")

    aws_sts(AUDIENCE)

    assert sts.clients[0].meta.region_name == "ap-southeast-2"
    assert (
        sts.clients[0].meta.endpoint_url == "https://sts.ap-southeast-2.amazonaws.com"
    )


def test_WIF_AWS_01_no_region_is_an_error_at_construction() -> None:
    with pytest.raises(AwsStsProviderError, match="region"):
        aws_sts(AUDIENCE)


def test_WIF_AWS_01_the_global_endpoint_is_rejected() -> None:
    with pytest.raises(AwsStsProviderError, match="regional"):
        aws_sts(AUDIENCE, region="aws-global")


def test_WIF_AWS_02_sts_error_names_the_call_and_the_code(sts: StubbedSts) -> None:
    sts.fails(
        "AccessDenied",
        "User: arn:aws:iam::123456789012:role/app is not authorized to perform: "
        "sts:GetWebIdentityToken",
        403,
    )
    provider = aws_sts(AUDIENCE, region="us-east-1")

    with pytest.raises(AwsStsProviderError) as excinfo:
        provider()

    message = str(excinfo.value)
    assert "sts:GetWebIdentityToken" in message
    assert "AccessDenied" in message
    assert "aws-jwt" not in message
    assert "aws-jwt" not in repr(excinfo.value)


def test_WIF_AWS_02_missing_token_in_the_response_is_an_error(sts: StubbedSts) -> None:
    sts.returns("")
    provider = aws_sts(AUDIENCE, region="us-east-1")

    with pytest.raises(AwsStsProviderError, match="sts:GetWebIdentityToken"):
        provider()


def test_audience_is_required() -> None:
    with pytest.raises(ValueError):
        aws_sts("", region="us-east-1")
