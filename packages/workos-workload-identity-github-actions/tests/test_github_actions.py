# @oagen-ignore-file

"""Conformance cases WIF-GHA-01 and WIF-GHA-02, against a local mock endpoint."""

from __future__ import annotations

import http.server
import threading
from dataclasses import dataclass, field
from typing import Dict, Iterator, List

import pytest

from workos_workload_identity_github_actions import (
    GitHubActionsProviderError,
    github_actions,
)

AUDIENCE = "https://api.workos.com"
REQUEST_TOKEN = "gha-request-token"


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

    assert REQUEST_TOKEN not in str(excinfo.value)


def test_non_http_url_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_URL", "file:///etc/hostname")
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError, match="http or https"):
        github_actions(AUDIENCE)()


def test_audience_is_required() -> None:
    with pytest.raises(ValueError):
        github_actions("")
