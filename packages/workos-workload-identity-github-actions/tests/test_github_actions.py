# @oagen-ignore-file

"""Conformance cases WIF-GHA-01 and WIF-GHA-02, against a local mock endpoint."""

from __future__ import annotations

import errno
import http.server
import os
import socket
import threading
from dataclasses import dataclass, field
from typing import Dict, Iterator, List

import pytest

import workos_workload_identity_github_actions as gha
from workos_workload_identity_github_actions import (
    GitHubActionsProviderError,
    github_actions,
)

AUDIENCE = "https://api.workos.com"
REQUEST_TOKEN = "gha-request-token"


def unreachable(reason: str, host: str) -> str:
    """The whole error text for a request that got no HTTP response."""
    return (
        f"The GitHub Actions OIDC token endpoint at {host} could not be reached: "
        f"{reason}. This provider works only in a GitHub Actions job, which sets "
        "the endpoint in ACTIONS_ID_TOKEN_REQUEST_URL."
    )


@dataclass
class Recorded:
    method: str
    path: str
    headers: Dict[str, str]


@dataclass
class MockServer:
    """A loopback HTTP server that records requests and returns a canned reply."""

    status: int = 200
    body: bytes = b""
    reply_headers: Dict[str, str] = field(default_factory=lambda: {})
    requests: List[Recorded] = field(default_factory=lambda: [])

    def __post_init__(self) -> None:
        mock = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                mock.requests.append(
                    Recorded(
                        "GET",
                        self.path,
                        {k.lower(): v for k, v in self.headers.items()},
                    )
                )
                self.send_response(mock.status)
                for name, value in mock.reply_headers.items():
                    self.send_header(name, value)
                self.send_header("Content-Length", str(len(mock.body)))
                self.end_headers()
                self.wfile.write(mock.body)

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
def mock() -> Iterator[MockServer]:
    server = MockServer(body=b'{"value": "gha-jwt"}')
    yield server
    server.close()


@pytest.fixture
def second_mock() -> Iterator[MockServer]:
    server = MockServer(body=b'{"value": "redirected-jwt"}')
    yield server
    server.close()


@pytest.fixture
def actions_env(mock: MockServer, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "ACTIONS_ID_TOKEN_REQUEST_URL", f"{mock.url}/token?api-version=2.0"
    )
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", REQUEST_TOKEN)


@pytest.mark.usefixtures("actions_env")
def test_WIF_GHA_01_requests_token_with_audience_and_bearer(mock: MockServer) -> None:
    provider = github_actions(AUDIENCE)

    assert provider() == "gha-jwt"

    assert len(mock.requests) == 1
    request = mock.requests[0]
    assert request.method == "GET"
    path, _, query = request.path.partition("?")
    assert path == "/token"
    # The existing query string is kept and the encoded audience is added to it.
    assert query.split("&") == [
        "api-version=2.0",
        "audience=https%3A%2F%2Fapi.workos.com",
    ]
    assert request.headers["authorization"] == f"Bearer {REQUEST_TOKEN}"
    assert request.headers["accept"] == "application/json"


def test_WIF_GHA_01_adds_a_query_string_when_the_url_has_none(
    mock: MockServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_URL", f"{mock.url}/token")
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", REQUEST_TOKEN)

    assert github_actions("api://workos/prod env")() == "gha-jwt"

    assert mock.requests[0].path == "/token?audience=api%3A%2F%2Fworkos%2Fprod%20env"


@pytest.mark.usefixtures("actions_env")
def test_WIF_GHA_01_reads_the_environment_on_every_call(
    mock: MockServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    provider = github_actions(AUDIENCE)
    provider()
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "rotated-request-token")
    provider()

    assert [r.headers["authorization"] for r in mock.requests] == [
        f"Bearer {REQUEST_TOKEN}",
        "Bearer rotated-request-token",
    ]


@pytest.mark.usefixtures("actions_env")
@pytest.mark.parametrize(
    "missing", ["ACTIONS_ID_TOKEN_REQUEST_URL", "ACTIONS_ID_TOKEN_REQUEST_TOKEN"]
)
@pytest.mark.parametrize("how", ["unset", "empty"])
def test_WIF_GHA_02_missing_env_fails_with_the_permission_hint(
    mock: MockServer, monkeypatch: pytest.MonkeyPatch, missing: str, how: str
) -> None:
    if how == "unset":
        monkeypatch.delenv(missing)
    else:
        monkeypatch.setenv(missing, "")
    provider = github_actions(AUDIENCE)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        provider()

    assert "permissions: id-token: write" in str(excinfo.value)
    assert mock.requests == []


@pytest.mark.usefixtures("actions_env")
def test_non_200_fails_naming_the_status(mock: MockServer) -> None:
    mock.status = 404

    with pytest.raises(GitHubActionsProviderError, match="404") as excinfo:
        github_actions(AUDIENCE)()

    assert REQUEST_TOKEN not in str(excinfo.value)
    assert REQUEST_TOKEN not in repr(excinfo.value)


@pytest.mark.usefixtures("actions_env")
@pytest.mark.parametrize(
    "body", [b"", b"not json", b"[]", b"{}", b'{"value": ""}', b'{"value": 7}']
)
def test_missing_or_empty_value_fails(mock: MockServer, body: bytes) -> None:
    mock.body = body

    with pytest.raises(GitHubActionsProviderError, match="no token value"):
        github_actions(AUDIENCE)()


@pytest.mark.usefixtures("actions_env")
def test_redirect_is_not_followed(mock: MockServer, second_mock: MockServer) -> None:
    mock.status = 302
    mock.reply_headers = {"Location": f"{second_mock.url}/elsewhere"}

    with pytest.raises(GitHubActionsProviderError, match="302"):
        github_actions(AUDIENCE)()

    assert len(mock.requests) == 1
    assert second_mock.requests == []


def test_connection_failure_is_a_provider_error(
    mock: MockServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    unused = mock.url
    mock.close()
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_URL", f"{unused}/token")
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        github_actions(AUDIENCE)()

    # The number differs by platform: 111 on Linux, 61 on macOS.
    refused = f"[Errno {errno.ECONNREFUSED}] {os.strerror(errno.ECONNREFUSED)}"
    assert refused.endswith("Connection refused")
    assert str(excinfo.value) == unreachable(refused, unused.removeprefix("http://"))


def test_name_resolution_failure_names_the_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    asked: List[object] = []

    def no_such_name(host: object, *args: object, **kwargs: object) -> None:
        asked.append(host)
        raise socket.gaierror(-2, "Name or service not known")

    monkeypatch.setattr(socket, "getaddrinfo", no_such_name)
    monkeypatch.setenv(
        "ACTIONS_ID_TOKEN_REQUEST_URL",
        "https://oidc.actions.invalid/token?api-version=2.0",
    )
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        github_actions(AUDIENCE)()

    assert str(excinfo.value) == unreachable(
        "[Errno -2] Name or service not known", "oidc.actions.invalid"
    )
    assert asked == ["oidc.actions.invalid"]


def test_timeout_waiting_for_the_response_names_the_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A listener that never accepts: the connection opens through its backlog
    # and no response ever comes.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as silent:
        silent.bind(("127.0.0.1", 0))
        silent.listen(1)
        host = f"127.0.0.1:{silent.getsockname()[1]}"
        monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_URL", f"http://{host}/token")
        monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", REQUEST_TOKEN)
        monkeypatch.setattr(gha, "_TIMEOUT_SECONDS", 0.2)

        with pytest.raises(GitHubActionsProviderError) as excinfo:
            github_actions(AUDIENCE)()

    assert str(excinfo.value) == unreachable("timed out", host)


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
    monkeypatch: pytest.MonkeyPatch, failure: OSError, reason: str
) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise failure

    monkeypatch.setattr(socket, "create_connection", fail)
    monkeypatch.setenv(
        "ACTIONS_ID_TOKEN_REQUEST_URL", "http://oidc.actions.invalid:8080/token"
    )
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        github_actions(AUDIENCE)()

    assert str(excinfo.value) == unreachable(reason, "oidc.actions.invalid:8080")


def test_unreachable_endpoint_shows_only_the_host_and_port_of_its_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def refuse(*args: object, **kwargs: object) -> None:
        raise ConnectionRefusedError(errno.ECONNREFUSED, "Connection refused")

    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setenv(
        "ACTIONS_ID_TOKEN_REQUEST_URL",
        "http://url-user:url-password@oidc.actions.invalid:8080/url-path?url-query=1",
    )
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        github_actions(AUDIENCE)()

    assert str(excinfo.value) == unreachable(
        f"[Errno {errno.ECONNREFUSED}] Connection refused", "oidc.actions.invalid:8080"
    )
    # Not chained: nothing of the request is reachable from the error.
    assert excinfo.value.__cause__ is None
    for hidden in ("url-user", "url-password", "url-path", "url-query", REQUEST_TOKEN):
        assert hidden not in repr(excinfo.value)


def test_non_http_url_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_URL", "file:///etc/hostname")
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError, match="http or https"):
        github_actions(AUDIENCE)()


def test_audience_is_required() -> None:
    with pytest.raises(ValueError):
        github_actions("")
