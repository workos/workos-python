from workos import WorkOSClient
from workos.pkce import PKCE
from workos.public_client import create_public_client


class TestPublicClient:
    def test_create_returns_workos_instance(self):
        client = create_public_client(client_id="client_test_123")
        try:
            assert isinstance(client, WorkOSClient)
        finally:
            client.close()

    def test_pkce_accessible(self):
        client = create_public_client(client_id="client_test_123")
        try:
            assert isinstance(client.pkce, PKCE)
            pair = client.pkce.generate()
            assert len(pair.code_verifier) == 43
        finally:
            client.close()

    def test_authorization_url_works(self):
        client = create_public_client(client_id="client_test_123")
        try:
            url = client.user_management.get_authorization_url(
                response_type="code",
                redirect_uri="https://example.com/callback",
                client_id="client_test_123",
            )
            assert "user_management/authorize" in url
        finally:
            client.close()

    def test_authorization_url_with_pkce_works(self):
        client = create_public_client(client_id="client_test_123")
        try:
            result = client.user_management.get_authorization_url_with_pkce(
                redirect_uri="https://example.com/callback",
            )
            assert "url" in result
            assert "state" in result
            assert "code_verifier" in result
            assert "code_challenge" in result["url"]
        finally:
            client.close()

    def test_no_api_key_configured(self):
        client = create_public_client(client_id="client_test_123")
        try:
            assert client._api_key is None
            assert client.client_id == "client_test_123"
        finally:
            client.close()
