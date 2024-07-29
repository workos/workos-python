import pytest

from workos import async_client, client
from workos.exceptions import ConfigurationException


class TestClient(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        client._audit_logs = None
        client._directory_sync = None
        client._events = None
        client._mfa = None
        client._organizations = None
        client._passwordless = None
        client._portal = None
        client._sso = None
        client._user_management = None

    def test_initialize_sso(self, set_api_key_and_client_id):
        assert bool(client.sso)

    def test_initialize_audit_logs(self, set_api_key):
        assert bool(client.audit_logs)

    def test_initialize_directory_sync(self, set_api_key):
        assert bool(client.directory_sync)

    def test_initialize_events(self, set_api_key):
        assert bool(client.events)

    def test_initialize_mfa(self, set_api_key):
        assert bool(client.mfa)

    def test_initialize_organizations(self, set_api_key):
        assert bool(client.organizations)

    def test_initialize_passwordless(self, set_api_key):
        assert bool(client.passwordless)

    def test_initialize_portal(self, set_api_key):
        assert bool(client.portal)

    def test_initialize_user_management(self, set_api_key, set_client_id):
        assert bool(client.user_management)

    def test_initialize_sso_missing_api_key(self, set_client_id):
        with pytest.raises(ConfigurationException) as ex:
            client.sso

        message = str(ex)

        assert "api_key" in message
        assert "client_id" not in message

    def test_initialize_sso_missing_client_id(self, set_api_key):
        with pytest.raises(ConfigurationException) as ex:
            client.sso

        message = str(ex)

        assert "client_id" in message
        assert "api_key" not in message

    def test_initialize_sso_missing_api_key_and_client_id(self):
        with pytest.raises(ConfigurationException) as ex:
            client.sso

        message = str(ex)

        assert all(
            setting in message
            for setting in (
                "api_key",
                "client_id",
            )
        )

    def test_initialize_directory_sync_missing_api_key(self):
        with pytest.raises(ConfigurationException) as ex:
            client.directory_sync

        message = str(ex)

        assert "api_key" in message

    def test_initialize_events_missing_api_key(self):
        with pytest.raises(ConfigurationException) as ex:
            client.events

        message = str(ex)

        assert "api_key" in message

    def test_initialize_mfa_missing_api_key(self):
        with pytest.raises(ConfigurationException) as ex:
            client.mfa

        message = str(ex)

        assert "api_key" in message

    def test_initialize_organizations_missing_api_key(self):
        with pytest.raises(ConfigurationException) as ex:
            client.organizations

        message = str(ex)

        assert "api_key" in message

    def test_initialize_passwordless_missing_api_key(self):
        with pytest.raises(ConfigurationException) as ex:
            client.passwordless

        message = str(ex)

        assert "api_key" in message

    def test_initialize_portal_missing_api_key(self):
        with pytest.raises(ConfigurationException) as ex:
            client.portal

        message = str(ex)

        assert "api_key" in message

    def test_initialize_user_management_missing_client_id(self, set_api_key):
        with pytest.raises(ConfigurationException) as ex:
            client.user_management

        message = str(ex)

        assert "client_id" in message

    def test_initialize_user_management_missing_api_key(self, set_client_id):
        with pytest.raises(ConfigurationException) as ex:
            client.user_management

        message = str(ex)

        assert "api_key" in message

    def test_initialize_user_management_missing_api_key_and_client_id(self):
        with pytest.raises(ConfigurationException) as ex:
            client.user_management

        message = str(ex)

        assert "api_key" in message
        assert "client_id" in message


class TestAsyncClient(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        async_client._audit_logs = None
        async_client._directory_sync = None
        async_client._events = None
        async_client._organizations = None
        async_client._passwordless = None
        async_client._portal = None
        async_client._sso = None
        async_client._user_management = None

    def test_initialize_directory_sync(self, set_api_key):
        assert bool(async_client.directory_sync)

    def test_initialize_directory_sync_missing_api_key(self):
        with pytest.raises(ConfigurationException) as ex:
            async_client.directory_sync

        message = str(ex)

        assert "api_key" in message

    def test_initialize_events(self, set_api_key):
        assert bool(async_client.events)

    def test_initialize_events_missing_api_key(self):
        with pytest.raises(ConfigurationException) as ex:
            async_client.events

        message = str(ex)

        assert "api_key" in message

    def test_initialize_sso(self, set_api_key_and_client_id):
        assert bool(async_client.sso)

    def test_initialize_sso_missing_api_key(self, set_client_id):
        with pytest.raises(ConfigurationException) as ex:
            async_client.sso

        message = str(ex)

        assert "api_key" in message
        assert "client_id" not in message

    def test_initialize_sso_missing_client_id(self, set_api_key):
        with pytest.raises(ConfigurationException) as ex:
            async_client.sso

        message = str(ex)

        assert "client_id" in message
        assert "api_key" not in message

    def test_initialize_sso_missing_api_key_and_client_id(self):
        with pytest.raises(ConfigurationException) as ex:
            async_client.sso

        message = str(ex)

        assert all(
            setting in message
            for setting in (
                "api_key",
                "client_id",
            )
        )
