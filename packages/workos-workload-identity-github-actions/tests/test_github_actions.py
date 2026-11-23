# @oagen-ignore-file

"""Conformance cases WIF-GHA-01 and WIF-GHA-02, against a local mock endpoint."""

from __future__ import annotations

import errno
import http.client
import http.server
import os
import socket
import threading
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Type

import pytest

import workos_workload_identity_github_actions as gha
from workos_workload_identity_github_actions import (
    GitHubActionsProviderError,
    github_actions,
)

AUDIENCE = "https://api.workos.com"
REQUEST_TOKEN = "gha-request-token"
IDENTITY_TOKEN = "gha-identity-jwt"
URL_ENV = "ACTIONS_ID_TOKEN_REQUEST_URL"
TOKEN_ENV = "ACTIONS_ID_TOKEN_REQUEST_TOKEN"

# The fixed texts of the errors for a value or a response that cannot be used.
NOT_VISIBLE_ASCII = (
    "{name} must not contain a space, a line break, another control character "
    "or a non-ASCII character."
)
INVALID_URL = f"{URL_ENV} is not a valid URL."
INVALID_RESPONSE = "GitHub Actions OIDC token response was not valid HTTP."
UNEXPECTED = (
    "GitHub Actions OIDC token request failed with an unexpected {kind}. "
    f"Check {URL_ENV} and {TOKEN_ENV}."
)


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


class RawServer:
    """A loopback server that answers every connection with the same bytes.

    The bytes need not be HTTP, which ``http.server`` cannot be made to send.
    """

    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self._stop = threading.Event()
        self._socket = socket.create_server(("127.0.0.1", 0))
        self._socket.settimeout(0.01)
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self._socket.getsockname()[1]}/token"

    def _serve(self) -> None:
        while not self._stop.is_set():
            try:
                connection, _ = self._socket.accept()
            except OSError:
                continue
            with connection:
                connection.settimeout(5)
                try:
                    received = b""
                    while b"\r\n\r\n" not in received:
                        received += connection.recv(65536) or b"\r\n\r\n"
                    connection.sendall(self._payload)
                    # Closed only once the client has closed, so the client
                    # reads the answer and not a reset connection.
                    connection.shutdown(socket.SHUT_WR)
                    while connection.recv(65536):
                        pass
                except OSError:
                    pass

    def close(self) -> None:
        self._stop.set()
        self._thread.join()
        self._socket.close()


def shown(error: BaseException, *secrets: str) -> List[str]:
    """Every place a secret shows up in an error or in an error attached to it."""
    found: List[str] = []
    seen: List[BaseException] = []
    current: Optional[BaseException] = error
    while current is not None and current not in seen:
        seen.append(current)
        places = {
            "str": str(current),
            "repr": repr(current),
            "args": repr(current.args),
            "attributes": repr(vars(current)),
        }
        found.extend(
            f"{type(current).__name__} {place}: {secret}"
            for place, text in places.items()
            for secret in secrets
            if secret in text
        )
        current = current.__cause__ or current.__context__
    return found


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

    assert shown(excinfo.value, REQUEST_TOKEN) == []


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


@pytest.mark.usefixtures("actions_env")
@pytest.mark.parametrize(
    "request_token",
    [
        f"{REQUEST_TOKEN}\n",
        f"{REQUEST_TOKEN}\r\n",
        f"{REQUEST_TOKEN}\r\nX-Added: 1",
        f" {REQUEST_TOKEN}",
        f"{REQUEST_TOKEN} {REQUEST_TOKEN}",
        f"{REQUEST_TOKEN}\t",
        f"{REQUEST_TOKEN}\x01",
        f"{REQUEST_TOKEN}\x7f",
        f"{REQUEST_TOKEN}\xe9",
        f"{REQUEST_TOKEN}\u20ac",
        f"{REQUEST_TOKEN}\udcff",
    ],
    ids=[
        "line break at the end",
        "carriage return and line break",
        "a second header line",
        "space at the start",
        "space inside",
        "tab",
        "control character",
        "delete character",
        "Latin-1 letter",
        "character outside Latin-1",
        "byte that is not UTF-8",
    ],
)
def test_request_token_outside_visible_ascii_is_refused_before_any_request(
    mock: MockServer, monkeypatch: pytest.MonkeyPatch, request_token: str
) -> None:
    monkeypatch.setenv(TOKEN_ENV, request_token)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        github_actions(AUDIENCE)()

    assert str(excinfo.value) == NOT_VISIBLE_ASCII.format(name=TOKEN_ENV)
    assert shown(excinfo.value, REQUEST_TOKEN) == []
    assert mock.requests == []


@pytest.mark.parametrize(
    "url",
    [
        "{mock}/to ken?api-version=2.0",
        "{mock}/token?api-version=2.0\n",
        "{mock}/tok\nen?api-version=2.0",
        " {mock}/token?api-version=2.0",
        "{mock}/token\t?api-version=2.0",
        "{mock}/tok\xe9n?api-version=2.0",
        "http://oidc actions.invalid/token?api-version=2.0",
    ],
    ids=[
        "space in the path",
        "line break at the end",
        "line break inside",
        "space at the start",
        "tab",
        "non-ASCII letter",
        "space in the host",
    ],
)
def test_url_outside_visible_ascii_is_refused_before_any_request(
    mock: MockServer, monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    monkeypatch.setenv(URL_ENV, url.format(mock=mock.url))
    monkeypatch.setenv(TOKEN_ENV, REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        github_actions(AUDIENCE)()

    # urllib alone would drop the line breaks, the tab and the space at the
    # start and send the request, and would quote the path with a space in it.
    assert str(excinfo.value) == NOT_VISIBLE_ASCII.format(name=URL_ENV)
    assert shown(excinfo.value, REQUEST_TOKEN, "api-version") == []
    assert mock.requests == []


def test_url_with_a_port_that_is_not_a_number_is_not_a_valid_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    url = "http://127.0.0.1:url-port/url-path"
    monkeypatch.setenv(URL_ENV, url)
    monkeypatch.setenv(TOKEN_ENV, REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        github_actions(AUDIENCE)()

    assert str(excinfo.value) == INVALID_URL
    assert shown(excinfo.value, REQUEST_TOKEN, "url-port", "url-path") == []
    # What urllib raises for it, and what that quotes.
    with pytest.raises(http.client.InvalidURL, match="url-port"):
        urllib.request.urlopen(url, timeout=1)


def test_url_that_cannot_be_split_is_not_a_valid_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    url = "http://[::1/url-path"
    monkeypatch.setenv(URL_ENV, url)
    monkeypatch.setenv(TOKEN_ENV, REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        github_actions(AUDIENCE)()

    assert str(excinfo.value) == INVALID_URL
    assert shown(excinfo.value, REQUEST_TOKEN, "url-path") == []
    with pytest.raises(ValueError):
        urllib.parse.urlsplit(url)


TOKEN_BODY = f'{{"value":"{IDENTITY_TOKEN}"}}'.encode()


@pytest.mark.parametrize(
    ("payload", "underneath"),
    [
        (TOKEN_BODY + b"\r\n\r\n", http.client.BadStatusLine),
        (
            b"HTTP/1.1 200 OK\r\nContent-Length: 500\r\n\r\n" + TOKEN_BODY,
            http.client.IncompleteRead,
        ),
        (
            b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n"
            + TOKEN_BODY
            + b"\r\n",
            http.client.IncompleteRead,
        ),
        (b"HTTP/1.1 200 " + b"x" * 70000 + b"\r\n\r\n", http.client.LineTooLong),
        (
            b"HTTP/1.1 200 OK\r\n" + b"X-Filler: 1\r\n" * 150 + b"\r\n",
            http.client.HTTPException,
        ),
        (b"HTTP/9.9 200 OK\r\n\r\n", http.client.UnknownProtocol),
    ],
    ids=[
        "body where the status line belongs",
        "body shorter than its Content-Length",
        "body that is not chunked under a chunked header",
        "status line too long",
        "too many headers",
        "unknown HTTP version",
    ],
)
def test_response_that_is_not_valid_http_is_not_quoted(
    monkeypatch: pytest.MonkeyPatch, payload: bytes, underneath: Type[Exception]
) -> None:
    server = RawServer(payload)
    monkeypatch.setenv(URL_ENV, server.url)
    monkeypatch.setenv(TOKEN_ENV, REQUEST_TOKEN)
    try:
        with pytest.raises(GitHubActionsProviderError) as excinfo:
            github_actions(AUDIENCE)()
        # What urllib raises for the same answer. It holds the bytes received.
        with pytest.raises(underneath):
            with urllib.request.urlopen(server.url, timeout=5) as response:
                response.read()
    finally:
        server.close()

    assert str(excinfo.value) == INVALID_RESPONSE
    assert shown(excinfo.value, REQUEST_TOKEN, IDENTITY_TOKEN) == []


@pytest.mark.parametrize(
    ("ending", "kind"),
    [("\n", "ValueError"), ("\u20ac", "UnicodeEncodeError")],
    ids=["line break", "character outside Latin-1"],
)
def test_request_token_stays_out_of_the_error_without_the_character_check(
    mock: MockServer, monkeypatch: pytest.MonkeyPatch, ending: str, kind: str
) -> None:
    def no_check(name: str, value: str) -> None:
        return None

    # With the check out of the way, http.client refuses the header itself,
    # with an error that quotes the header value.
    monkeypatch.setattr(gha, "_require_visible_ascii", no_check)
    monkeypatch.setenv(URL_ENV, f"{mock.url}/token")
    monkeypatch.setenv(TOKEN_ENV, REQUEST_TOKEN + ending)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        github_actions(AUDIENCE)()

    assert str(excinfo.value) == UNEXPECTED.format(kind=kind)
    assert shown(excinfo.value, REQUEST_TOKEN) == []
    assert mock.requests == []


def test_host_name_that_cannot_be_encoded_is_a_provider_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A host name with an empty label. Encoding it for the name lookup fails
    # before anything is looked up.
    monkeypatch.setenv(URL_ENV, "http://url-host..invalid:8080/url-path")
    monkeypatch.setenv(TOKEN_ENV, REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError) as excinfo:
        github_actions(AUDIENCE)()

    # The class is UnicodeError before Python 3.13 and a subclass of it since.
    assert str(excinfo.value) in (
        UNEXPECTED.format(kind="UnicodeError"),
        UNEXPECTED.format(kind="UnicodeEncodeError"),
    )
    assert shown(excinfo.value, REQUEST_TOKEN, "url-host", "url-path") == []


def test_json_nested_too_deep_to_parse_has_no_token_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = b"[" * 100000
    head = f"HTTP/1.1 200 OK\r\nContent-Length: {len(body)}\r\n\r\n".encode()
    server = RawServer(head + body)
    monkeypatch.setenv(URL_ENV, server.url)
    monkeypatch.setenv(TOKEN_ENV, REQUEST_TOKEN)
    try:
        with pytest.raises(GitHubActionsProviderError, match="no token value"):
            github_actions(AUDIENCE)()
    finally:
        server.close()


def test_non_http_url_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_URL", "file:///etc/hostname")
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", REQUEST_TOKEN)

    with pytest.raises(GitHubActionsProviderError, match="http or https"):
        github_actions(AUDIENCE)()


def test_audience_is_required() -> None:
    with pytest.raises(ValueError):
        github_actions("")
