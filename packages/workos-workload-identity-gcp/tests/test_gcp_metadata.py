# @oagen-ignore-file

"""Conformance cases WIF-GCP-01 and WIF-GCP-02, against a local mock server."""

from __future__ import annotations

import http.server
import threading
from dataclasses import dataclass, field
from typing import Dict, Iterator, List

import pytest

import workos_workload_identity_gcp as gcp
from workos_workload_identity_gcp import GcpMetadataProviderError, gcp_metadata

AUDIENCE = "https://api.workos.com"
IDENTITY_PATH = "/computeMetadata/v1/instance/service-accounts/default/identity"


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

    with pytest.raises(GcpMetadataProviderError):
        gcp_metadata(AUDIENCE)()


def test_the_request_does_not_go_through_an_environment_proxy(
    mock: MockServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Nothing listens on the proxy's port: the call works only if it is direct.
    for name in ("http_proxy", "HTTP_PROXY", "all_proxy", "ALL_PROXY"):
        monkeypatch.setenv(name, "http://127.0.0.1:9")
    for name in ("no_proxy", "NO_PROXY"):
        monkeypatch.delenv(name, raising=False)

    assert gcp_metadata(AUDIENCE)() == "gcp-jwt"

    assert len(mock.requests) == 1


def test_audience_is_percent_encoded(mock: MockServer) -> None:
    gcp_metadata("api://workos/prod env")()

    assert mock.requests[0].path == (
        f"{IDENTITY_PATH}?audience=api%3A%2F%2Fworkos%2Fprod%20env&format=full"
    )


def test_audience_is_required() -> None:
    with pytest.raises(ValueError):
        gcp_metadata("")
