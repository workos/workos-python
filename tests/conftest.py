import pytest
import requests

import workos

class MockResponse(object):
    def __init__(self, response_dict, status_code):
        self.response_dict = response_dict
        self.status_code = status_code

    def json(self):
        return self.response_dict

@pytest.fixture
def set_api_key(monkeypatch):
    monkeypatch.setattr(workos, 'api_key', 'sk_abdsomecharactersm284')

@pytest.fixture
def set_project_id(monkeypatch):
    monkeypatch.setattr(workos, 'project_id', 'project_b27needthisforssotemxo')

@pytest.fixture
def set_api_key_and_project_id(set_api_key, set_project_id):
    pass

@pytest.fixture
def mock_request_method(monkeypatch):
    def _mock_request_method(method, response_dict, status_code):
        def mock_response(*args, **kwargs):
            return MockResponse(response_dict, status_code)

        monkeypatch.setattr(requests, method, mock_response)

    return _mock_request_method