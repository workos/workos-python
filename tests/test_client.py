import pytest

from workos import client
from workos.exceptions import ConfigurationException


class TestClient(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        client._audit_trail = None
        client._directory_sync = None
        client._passwordless = None
        client._portal = None
        client._sso = None

    def test_initialize_sso(self, set_api_key_and_project_id):
        assert bool(client.sso)

    def test_initialize_audit_log(self, set_api_key_and_project_id):
        assert bool(client.audit_trail)

    def test_initialize_directory_sync(self, set_api_key):
        assert bool(client.directory_sync)

    def test_initialize_passwordless(self, set_api_key):
        assert bool(client.passwordless)

    def test_initialize_portal(self, set_api_key):
        assert bool(client.portal)

    def test_initialize_sso_missing_api_key(self, set_project_id):
        with pytest.raises(ConfigurationException) as ex:
            client.sso

        message = str(ex)

        assert "api_key" in message
        assert "project_id" not in message

    def test_initialize_sso_missing_project_id(self, set_api_key):
        with pytest.raises(ConfigurationException) as ex:
            client.sso

        message = str(ex)

        assert "project_id" in message
        assert "api_key" not in message

    def test_initialize_sso_missing_api_key_and_project_id(self):
        with pytest.raises(ConfigurationException) as ex:
            client.sso

        message = str(ex)

        assert all(setting in message for setting in ("api_key", "project_id",))

    def test_initialize_audit_trail_missing_api_key(self):
        with pytest.raises(ConfigurationException) as ex:
            client.audit_trail

        message = str(ex)

        assert "api_key" in message

    def test_initialize_directory_sync_missing_api_key(self):
        with pytest.raises(ConfigurationException) as ex:
            client.directory_sync

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
