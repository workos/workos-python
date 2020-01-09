import pytest

from workos import client
from workos.exceptions import ConfigurationException

class TestClient(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        client._sso = None

    def test_initialize_sso(self, set_api_key_and_project_id):
        assert bool(client.sso)

    def test_initialize_sso_missing_api_key(self, set_project_id):
        with pytest.raises(ConfigurationException):
            client.sso

    def test_initialize_sso_missing_project_id(self, set_api_key):
        with pytest.raises(ConfigurationException):
            client.sso
        
    