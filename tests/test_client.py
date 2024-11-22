import os
import pytest
from workos import AsyncWorkOSClient, WorkOSClient


class TestClient:
    @pytest.fixture
    def default_client(self):
        return WorkOSClient(
            api_key="sk_test", client_id="client_b27needthisforssotemxo"
        )

    def test_client_without_api_key(self):
        with pytest.raises(ValueError) as error:
            WorkOSClient(client_id="client_b27needthisforssotemxo")

        assert (
            "WorkOS API key must be provided when instantiating the client or via the WORKOS_API_KEY environment variable."
            == str(error.value)
        )

    def test_client_without_client_id(self):
        with pytest.raises(ValueError) as error:
            WorkOSClient(api_key="sk_test")

        assert (
            "WorkOS client ID must be provided when instantiating the client or via the WORKOS_CLIENT_ID environment variable."
            == str(error.value)
        )

    def test_client_with_api_key_and_client_id_environment_variables(self):
        os.environ["WORKOS_API_KEY"] = "sk_test"
        os.environ["WORKOS_CLIENT_ID"] = "client_b27needthisforssotemxo"

        assert bool(WorkOSClient())

        os.environ.pop("WORKOS_API_KEY")
        os.environ.pop("WORKOS_CLIENT_ID")

    def test_initialize_sso(self, default_client):
        assert bool(default_client.sso)

    def test_initialize_audit_logs(self, default_client):
        assert bool(default_client.audit_logs)

    def test_initialize_directory_sync(self, default_client):
        assert bool(default_client.directory_sync)

    def test_initialize_events(self, default_client):
        assert bool(default_client.events)

    def test_initialize_mfa(self, default_client):
        assert bool(default_client.mfa)

    def test_initialize_organizations(self, default_client):
        assert bool(default_client.organizations)

    def test_initialize_passwordless(self, default_client):
        assert bool(default_client.passwordless)

    def test_initialize_portal(self, default_client):
        assert bool(default_client.portal)

    def test_initialize_user_management(self, default_client):
        assert bool(default_client.user_management)

    def test_initialize_widgets(self, default_client):
        assert bool(default_client.widgets)

    def test_enforce_trailing_slash_for_base_url(
        self,
    ):
        client = WorkOSClient(
            api_key="sk_test",
            client_id="client_b27needthisforssotemxo",
            base_url="https://api.workos.com",
        )
        assert client.base_url == "https://api.workos.com/"


class TestAsyncClient:
    @pytest.fixture
    def default_client(self):
        return AsyncWorkOSClient(
            api_key="sk_test", client_id="client_b27needthisforssotemxo"
        )

    def test_client_without_api_key(self):
        with pytest.raises(ValueError) as error:
            AsyncWorkOSClient(client_id="client_b27needthisforssotemxo")

        assert (
            "WorkOS API key must be provided when instantiating the client or via the WORKOS_API_KEY environment variable."
            == str(error.value)
        )

    def test_client_without_client_id(self):
        with pytest.raises(ValueError) as error:
            AsyncWorkOSClient(api_key="sk_test")

        assert (
            "WorkOS client ID must be provided when instantiating the client or via the WORKOS_CLIENT_ID environment variable."
            == str(error.value)
        )

    def test_client_with_api_key_and_client_id_environment_variables(self):
        os.environ["WORKOS_API_KEY"] = "sk_test"
        os.environ["WORKOS_CLIENT_ID"] = "client_b27needthisforssotemxo"

        assert bool(AsyncWorkOSClient())

        os.environ.pop("WORKOS_API_KEY")
        os.environ.pop("WORKOS_CLIENT_ID")

    def test_initialize_directory_sync(self, default_client):
        assert bool(default_client.directory_sync)

    def test_initialize_events(self, default_client):
        assert bool(default_client.events)

    def test_initialize_sso(self, default_client):
        assert bool(default_client.sso)
