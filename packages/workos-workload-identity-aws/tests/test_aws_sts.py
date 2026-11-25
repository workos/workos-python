# @oagen-ignore-file

"""Conformance cases WIF-AWS-01 and WIF-AWS-02.

The STS client is the real boto3 client with a botocore ``Stubber`` attached,
so parameter names are validated against the service model and no request
leaves the process.

The tests of an unreachable endpoint have no stub. The client sends its
request, and the name lookup or the connection under it is faked, so nothing
leaves the machine.

The tests that count requests have no stub either: the stub answers before the
AWS SDK's retry logic runs. They point the client at a loopback server.
"""

from __future__ import annotations

import datetime
import errno
import http.server
import os
import socket
import ssl
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterator, List, Optional

import pytest
from botocore.stub import Stubber

import workos_workload_identity_aws as aws
from workos_workload_identity_aws import AwsStsProviderError, aws_sts

if TYPE_CHECKING:
    from types_boto3_sts.client import STSClient

AUDIENCE = "https://api.workos.com"
EXPECTED_PARAMS = {"Audience": [AUDIENCE], "SigningAlgorithm": "RS256"}
STS_HOST = "sts.us-east-1.amazonaws.com"


def unreachable(reason: str) -> str:
    """The whole error text for a request that got no HTTP response."""
    return f"The AWS STS endpoint at {STS_HOST} could not be reached: {reason}."


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


@pytest.fixture
def resolves_to(monkeypatch: pytest.MonkeyPatch) -> Callable[[int], List[object]]:
    """Point every host name at a loopback port, and list the names asked for."""
    # One attempt: botocore would sleep before each retry of a failed connection.
    monkeypatch.setenv("AWS_MAX_ATTEMPTS", "1")
    asked: List[object] = []

    def resolve_to(port: int) -> List[object]:
        def loopback(host: object, *args: object, **kwargs: object) -> List[object]:
            asked.append(host)
            address = ("127.0.0.1", port)
            return [
                (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", address)
            ]

        monkeypatch.setattr(socket, "getaddrinfo", loopback)
        return asked

    return resolve_to


def test_name_resolution_failure_names_the_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AWS_MAX_ATTEMPTS", "1")
    asked: List[object] = []

    def no_such_name(host: object, *args: object, **kwargs: object) -> None:
        asked.append(host)
        raise socket.gaierror(-2, "Name or service not known")

    monkeypatch.setattr(socket, "getaddrinfo", no_such_name)

    with pytest.raises(AwsStsProviderError) as excinfo:
        aws_sts(AUDIENCE, region="us-east-1")()

    assert str(excinfo.value) == unreachable("[Errno -2] Name or service not known")
    assert asked == [STS_HOST]


def test_connection_refused_names_the_reason(
    resolves_to: Callable[[int], List[object]],
) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as closed:
        closed.bind(("127.0.0.1", 0))
        port: int = closed.getsockname()[1]
    asked = resolves_to(port)

    with pytest.raises(AwsStsProviderError) as excinfo:
        aws_sts(AUDIENCE, region="us-east-1")()

    # The number differs by platform: 111 on Linux, 61 on macOS.
    refused = f"[Errno {errno.ECONNREFUSED}] {os.strerror(errno.ECONNREFUSED)}"
    assert refused.endswith("Connection refused")
    assert str(excinfo.value) == unreachable(refused)
    assert asked == [STS_HOST]


@pytest.mark.parametrize(
    ("failure", "reason"),
    [
        (TimeoutError("timed out"), "timed out"),
        (TimeoutError(), "timed out"),
        (OSError(), "unknown network error"),
    ],
    ids=["timeout", "timeout without text", "other failure without text"],
)
def test_connect_failure_always_names_a_reason(
    resolves_to: Callable[[int], List[object]],
    monkeypatch: pytest.MonkeyPatch,
    failure: OSError,
    reason: str,
) -> None:
    def fail(self: socket.socket, address: object) -> None:
        raise failure

    resolves_to(443)
    monkeypatch.setattr(socket.socket, "connect", fail)

    with pytest.raises(AwsStsProviderError) as excinfo:
        aws_sts(AUDIENCE, region="us-east-1")()

    assert str(excinfo.value) == unreachable(reason)
    # Not chained: nothing of the request is reachable from the error.
    assert excinfo.value.__cause__ is None


def test_timeout_waiting_for_the_response_names_the_reason(
    resolves_to: Callable[[int], List[object]], monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_answer(*args: object, **kwargs: object) -> None:
        raise TimeoutError("The read operation timed out")

    # A listener that never accepts: the connection opens through its backlog.
    # The TLS handshake that would wait ten seconds for an answer is cut short.
    monkeypatch.setattr(ssl.SSLContext, "wrap_socket", no_answer)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as silent:
        silent.bind(("127.0.0.1", 0))
        silent.listen(1)
        resolves_to(silent.getsockname()[1])

        with pytest.raises(AwsStsProviderError) as excinfo:
            aws_sts(AUDIENCE, region="us-east-1")()

    assert str(excinfo.value) == unreachable("The read operation timed out")


class CountingSts:
    """A loopback server that answers every request with one STS error, and counts them."""

    def __init__(self) -> None:
        self.status = 400
        self.code = "Throttling"
        self.requests = 0
        counting = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                self.rfile.read(int(self.headers.get("Content-Length", 0)))
                counting.requests += 1
                body = (
                    "<ErrorResponse><Error><Type>Sender</Type>"
                    f"<Code>{counting.code}</Code><Message>no</Message></Error>"
                    "<RequestId>request-1</RequestId></ErrorResponse>"
                ).encode()
                self.send_response(counting.status)
                self.send_header("Content-Type", "text/xml")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                return None

        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            kwargs={"poll_interval": 0.01},
            daemon=True,
        )
        self._thread.start()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self._server.server_address[1]}"

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join()


@pytest.fixture
def counting_sts(monkeypatch: pytest.MonkeyPatch) -> Iterator[CountingSts]:
    server = CountingSts()
    monkeypatch.setenv("AWS_ENDPOINT_URL_STS", server.url)
    yield server
    server.close()


@pytest.mark.parametrize(
    ("status", "code"),
    [(400, "Throttling"), (500, "InternalFailure"), (503, "ServiceUnavailable")],
)
def test_one_provider_call_is_one_sts_request(
    counting_sts: CountingSts,
    monkeypatch: pytest.MonkeyPatch,
    status: int,
    code: str,
) -> None:
    counting_sts.status = status
    counting_sts.code = code
    # The AWS SDK's own settings ask for retries. The provider's client does
    # not follow them: the WorkOS SDK retries the provider call itself.
    monkeypatch.setenv("AWS_MAX_ATTEMPTS", "5")
    monkeypatch.setenv("AWS_RETRY_MODE", "standard")
    provider = aws_sts(AUDIENCE, region="us-east-1")

    with pytest.raises(AwsStsProviderError) as excinfo:
        provider()

    assert str(excinfo.value) == f"sts:GetWebIdentityToken failed with {code}."
    assert counting_sts.requests == 1


def test_the_sts_client_waits_ten_seconds_at_most(sts: StubbedSts) -> None:
    aws_sts(AUDIENCE, region="us-east-1")

    # The type stubs do not declare the settings of a client's configuration.
    limits = vars(sts.clients[0].meta.config)
    # To connect, and for each wait for the response. The AWS SDK's default
    # is 60 seconds for both.
    assert limits["connect_timeout"] == 10
    assert limits["read_timeout"] == 10


def test_audience_is_required() -> None:
    with pytest.raises(ValueError):
        aws_sts("", region="us-east-1")
