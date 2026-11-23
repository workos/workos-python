# @oagen-ignore-file

"""Conformance cases WIF-GCP-01 to WIF-GCP-03, against a local mock server."""

from __future__ import annotations

import errno
import http.client
import http.server
import os
import socket
import threading
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Type

import pytest

import workos_workload_identity_gcp as gcp
from workos_workload_identity_gcp import GcpMetadataProviderError, gcp_metadata

AUDIENCE = "https://api.workos.com"
IDENTITY_PATH = "/computeMetadata/v1/instance/service-accounts/default/identity"
IDENTITY_TOKEN = "SECRET-GCP-IDENTITY-TOKEN"
INVALID_RESPONSE = "GCP metadata identity response was not valid HTTP."
UNEXPECTED = "GCP metadata identity request failed with an unexpected {kind}."


def unreachable(reason: str) -> str:
    """The whole error text for a request that got no HTTP response."""
    return (
        f"The GCP metadata server could not be reached: {reason}. "
        "This provider works only on Google Cloud "
        "(Compute Engine, GKE, Cloud Run, Cloud Functions)."
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
        return f"http://127.0.0.1:{self._socket.getsockname()[1]}"

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
def mock(monkeypatch: pytest.MonkeyPatch) -> Iterator[MockServer]:
    """The metadata server. The provider's internal base URL points at it."""
    server = MockServer(body=b"gcp-jwt\n")
    monkeypatch.setattr(gcp, "_METADATA_BASE_URL", server.url)
    yield server
    server.close()


@pytest.fixture
def second_mock() -> Iterator[MockServer]:
    server = MockServer(body=b"redirected-jwt")
    yield server
    server.close()


def test_WIF_GCP_01_requests_identity_with_audience_and_metadata_header(
    mock: MockServer,
) -> None:
    provider = gcp_metadata(AUDIENCE)

    assert provider() == "gcp-jwt"

    assert len(mock.requests) == 1
    request = mock.requests[0]
    assert request.method == "GET"
    path, _, query = request.path.partition("?")
    assert path == IDENTITY_PATH
    assert query == "audience=https%3A%2F%2Fapi.workos.com&format=full"
    assert request.headers["metadata-flavor"] == "Google"


def test_WIF_GCP_01_default_base_url_is_the_metadata_server() -> None:
    assert gcp._METADATA_BASE_URL == "http://metadata.google.internal"  # pyright: ignore[reportPrivateUsage]


def test_WIF_GCP_02_non_200_is_an_error(mock: MockServer) -> None:
    mock.status = 404
    mock.body = b"not found"

    with pytest.raises(GcpMetadataProviderError, match="404"):
        gcp_metadata(AUDIENCE)()

    assert len(mock.requests) == 1


@pytest.mark.parametrize("body", [b"", b" \n\t "])
def test_WIF_GCP_02_empty_body_is_an_error(mock: MockServer, body: bytes) -> None:
    mock.body = body

    with pytest.raises(GcpMetadataProviderError, match="empty"):
        gcp_metadata(AUDIENCE)()


def test_WIF_GCP_02_redirect_is_not_followed(
    mock: MockServer, second_mock: MockServer
) -> None:
    mock.status = 302
    mock.reply_headers = {"Location": f"{second_mock.url}/elsewhere"}

    with pytest.raises(GcpMetadataProviderError, match="302"):
        gcp_metadata(AUDIENCE)()

    assert len(mock.requests) == 1
    assert second_mock.requests == []


def test_connection_failure_is_a_provider_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = MockServer()
    unused = server.url
    server.close()
    monkeypatch.setattr(gcp, "_METADATA_BASE_URL", unused)

    with pytest.raises(GcpMetadataProviderError) as raised:
        gcp_metadata(AUDIENCE)()

    # The number differs by platform: 111 on Linux, 61 on macOS.
    refused = f"[Errno {errno.ECONNREFUSED}] {os.strerror(errno.ECONNREFUSED)}"
    assert refused.endswith("Connection refused")
    assert str(raised.value) == unreachable(refused)


def test_name_resolution_failure_names_the_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    asked: List[object] = []

    def no_such_name(host: object, *args: object, **kwargs: object) -> None:
        asked.append(host)
        raise socket.gaierror(-2, "Name or service not known")

    monkeypatch.setattr(socket, "getaddrinfo", no_such_name)

    with pytest.raises(GcpMetadataProviderError) as raised:
        gcp_metadata(AUDIENCE)()

    assert str(raised.value) == unreachable("[Errno -2] Name or service not known")
    assert asked == ["metadata.google.internal"]


def test_timeout_waiting_for_the_response_names_the_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A listener that never accepts: the connection opens through its backlog
    # and no response ever comes.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as silent:
        silent.bind(("127.0.0.1", 0))
        silent.listen(1)
        monkeypatch.setattr(
            gcp, "_METADATA_BASE_URL", f"http://127.0.0.1:{silent.getsockname()[1]}"
        )
        monkeypatch.setattr(gcp, "_TIMEOUT_SECONDS", 0.2)

        with pytest.raises(GcpMetadataProviderError) as raised:
            gcp_metadata(AUDIENCE)()

    assert str(raised.value) == unreachable("timed out")


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

    with pytest.raises(GcpMetadataProviderError) as raised:
        gcp_metadata(AUDIENCE)()

    assert str(raised.value) == unreachable(reason)


def test_WIF_GCP_03_the_request_does_not_go_through_an_environment_proxy(
    mock: MockServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Nothing listens on the proxy's port: the call works only if it is direct.
    for name in ("http_proxy", "HTTP_PROXY", "all_proxy", "ALL_PROXY"):
        monkeypatch.setenv(name, "http://127.0.0.1:9")
    for name in ("no_proxy", "NO_PROXY"):
        monkeypatch.delenv(name, raising=False)

    assert gcp_metadata(AUDIENCE)() == "gcp-jwt"

    assert len(mock.requests) == 1


TOKEN_BODY = IDENTITY_TOKEN.encode()


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
        "token where the status line belongs",
        "token shorter than its Content-Length",
        "token that is not chunked under a chunked header",
        "status line too long",
        "too many headers",
        "unknown HTTP version",
    ],
)
def test_response_that_is_not_valid_http_is_not_quoted(
    monkeypatch: pytest.MonkeyPatch, payload: bytes, underneath: Type[Exception]
) -> None:
    server = RawServer(payload)
    monkeypatch.setattr(gcp, "_METADATA_BASE_URL", server.url)
    try:
        with pytest.raises(GcpMetadataProviderError) as excinfo:
            gcp_metadata(AUDIENCE)()
        # What urllib raises for the same answer. It holds the bytes received.
        with pytest.raises(underneath):
            with urllib.request.urlopen(server.url, timeout=5) as response:
                response.read()
    finally:
        server.close()

    assert str(excinfo.value) == INVALID_RESPONSE
    assert shown(excinfo.value, IDENTITY_TOKEN) == []


def test_an_unexpected_error_is_named_and_not_quoted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise ValueError(f"something that quotes {IDENTITY_TOKEN}")

    monkeypatch.setattr(urllib.request.OpenerDirector, "open", fail)

    with pytest.raises(GcpMetadataProviderError) as excinfo:
        gcp_metadata(AUDIENCE)()

    assert str(excinfo.value) == UNEXPECTED.format(kind="ValueError")
    assert shown(excinfo.value, IDENTITY_TOKEN) == []


def test_audience_is_percent_encoded(mock: MockServer) -> None:
    gcp_metadata("api://workos/prod env")()

    assert mock.requests[0].path == (
        f"{IDENTITY_PATH}?audience=api%3A%2F%2Fworkos%2Fprod%20env&format=full"
    )


def test_audience_is_required() -> None:
    with pytest.raises(ValueError):
        gcp_metadata("")
