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
def capture_and_mock_request(monkeypatch):
    def inner(method, response_dict, status_code):
        request_args = []
        request_kwargs = {}

        def capture_and_mock(*args, **kwargs):
            request_args.extend(args)
            request_kwargs.update(kwargs)

            return MockResponse(response_dict, status_code)

        monkeypatch.setattr(requests, method, capture_and_mock)

        return (request_args, request_kwargs)

    return inner
