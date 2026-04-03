import json

import pytest
from workos import WorkOS, AsyncWorkOS
from tests.generated_helpers import load_fixture

from workos.passwordless import PasswordlessSession
from workos._errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitExceededError,
    ServerError,
)


class TestPasswordless:
    def test_create_session(self, workos, httpx_mock):
        httpx_mock.add_response(
            json=load_fixture("passwordless_session.json"),
        )
        result = workos.passwordless.create_session(
            email="user@example.com", type="MagicLink"
        )
        assert isinstance(result, PasswordlessSession)
        assert result.id == "passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        assert result.email == "user@example.com"
        assert result.link.startswith("https://auth.workos.com/passwordless/")
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path.endswith("/passwordless/sessions")
        body = json.loads(request.content)
        assert body["email"] == "user@example.com"
        assert body["type"] == "MagicLink"

    def test_create_session_with_optional_params(self, workos, httpx_mock):
        httpx_mock.add_response(
            json=load_fixture("passwordless_session.json"),
        )
        result = workos.passwordless.create_session(
            email="user@example.com",
            type="MagicLink",
            redirect_uri="https://example.com/callback",
            state="custom-state",
            expires_in=3600,
        )
        assert isinstance(result, PasswordlessSession)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["redirect_uri"] == "https://example.com/callback"
        assert body["state"] == "custom-state"
        assert body["expires_in"] == 3600

    def test_send_session(self, workos, httpx_mock):
        httpx_mock.add_response(status_code=204)
        result = workos.passwordless.send_session(
            "passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        assert result is True
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path.endswith(
            "/passwordless/sessions/passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C/send"
        )

    def test_create_session_unauthorized(self, workos, httpx_mock):
        httpx_mock.add_response(
            status_code=401,
            json={"message": "Unauthorized"},
        )
        with pytest.raises(AuthenticationError):
            workos.passwordless.create_session(
                email="user@example.com", type="MagicLink"
            )

    def test_create_session_not_found(self, httpx_mock):
        workos = WorkOS(api_key="sk_test_123", client_id="client_test", max_retries=0)
        try:
            httpx_mock.add_response(status_code=404, json={"message": "Not found"})
            with pytest.raises(NotFoundError):
                workos.passwordless.create_session(
                    email="user@example.com", type="MagicLink"
                )
        finally:
            workos.close()

    def test_create_session_rate_limited(self, httpx_mock):
        workos = WorkOS(api_key="sk_test_123", client_id="client_test", max_retries=0)
        try:
            httpx_mock.add_response(
                status_code=429,
                headers={"Retry-After": "0"},
                json={"message": "Slow down"},
            )
            with pytest.raises(RateLimitExceededError):
                workos.passwordless.create_session(
                    email="user@example.com", type="MagicLink"
                )
        finally:
            workos.close()

    def test_create_session_server_error(self, httpx_mock):
        workos = WorkOS(api_key="sk_test_123", client_id="client_test", max_retries=0)
        try:
            httpx_mock.add_response(status_code=500, json={"message": "Server error"})
            with pytest.raises(ServerError):
                workos.passwordless.create_session(
                    email="user@example.com", type="MagicLink"
                )
        finally:
            workos.close()


@pytest.mark.asyncio
class TestAsyncPasswordless:
    async def test_create_session(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("passwordless_session.json"))
        result = await async_workos.passwordless.create_session(
            email="user@example.com", type="MagicLink"
        )
        assert isinstance(result, PasswordlessSession)
        assert result.id == "passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        assert result.email == "user@example.com"
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path.endswith("/passwordless/sessions")

    async def test_create_session_with_optional_params(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("passwordless_session.json"))
        result = await async_workos.passwordless.create_session(
            email="user@example.com",
            type="MagicLink",
            redirect_uri="https://example.com/callback",
            state="custom-state",
            expires_in=3600,
        )
        assert isinstance(result, PasswordlessSession)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["redirect_uri"] == "https://example.com/callback"
        assert body["state"] == "custom-state"
        assert body["expires_in"] == 3600

    async def test_send_session(self, async_workos, httpx_mock):
        httpx_mock.add_response(status_code=204)
        result = await async_workos.passwordless.send_session(
            "passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        assert result is True
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path.endswith(
            "/passwordless/sessions/passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C/send"
        )

    async def test_create_session_unauthorized(self, async_workos, httpx_mock):
        httpx_mock.add_response(status_code=401, json={"message": "Unauthorized"})
        with pytest.raises(AuthenticationError):
            await async_workos.passwordless.create_session(
                email="user@example.com", type="MagicLink"
            )

    async def test_create_session_not_found(self, httpx_mock):
        workos = AsyncWorkOS(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        try:
            httpx_mock.add_response(status_code=404, json={"message": "Not found"})
            with pytest.raises(NotFoundError):
                await workos.passwordless.create_session(
                    email="user@example.com", type="MagicLink"
                )
        finally:
            await workos.close()

    async def test_create_session_rate_limited(self, httpx_mock):
        workos = AsyncWorkOS(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        try:
            httpx_mock.add_response(
                status_code=429,
                headers={"Retry-After": "0"},
                json={"message": "Slow down"},
            )
            with pytest.raises(RateLimitExceededError):
                await workos.passwordless.create_session(
                    email="user@example.com", type="MagicLink"
                )
        finally:
            await workos.close()

    async def test_create_session_server_error(self, httpx_mock):
        workos = AsyncWorkOS(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        try:
            httpx_mock.add_response(status_code=500, json={"message": "Server error"})
            with pytest.raises(ServerError):
                await workos.passwordless.create_session(
                    email="user@example.com", type="MagicLink"
                )
        finally:
            await workos.close()
