import pytest
import requests

import workos


class MockResponse(object):
    def __init__(self, response_dict, status_code, headers=None):
        self.response_dict = response_dict
        self.status_code = status_code
        self.headers = {} if headers is None else headers

    def json(self):
        return self.response_dict


@pytest.fixture
def set_api_key(monkeypatch):
    monkeypatch.setattr(workos, "api_key", "sk_abdsomecharactersm284")


@pytest.fixture
def set_project_id(monkeypatch):
    monkeypatch.setattr(workos, "project_id", "project_b27needthisforssotemxo")


@pytest.fixture
def set_api_key_and_project_id(set_api_key, set_project_id):
    pass


@pytest.fixture
def mock_request_method(monkeypatch):
    def inner(method, response_dict, status_code, headers=None):
        def mock(*args, **kwargs):
            return MockResponse(response_dict, status_code, headers=headers)

        monkeypatch.setattr(requests, method, mock)

    return inner


@pytest.fixture
def capture_and_mock_requests(monkeypatch):
    def inner():
        captured_requests = []

        def capture(*args, **kwargs):
            captured_requests.append((args, kwargs))
            return MockResponse({}, 200)

        monkeypatch.setattr(requests, "get", capture)
        monkeypatch.setattr(requests, "post", capture)

        return captured_requests

    return inner
