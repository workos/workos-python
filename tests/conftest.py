import pytest
import requests

import workos


class MockResponse(object):
    def __init__(self, response_dict, status_code, headers=None):
        self.response_dict = response_dict
        self.status_code = status_code
        self.headers = {} if headers is None else headers

        if "content-type" not in self.headers:
            self.headers["content-type"] = "application/json"

    def json(self):
        return self.response_dict


class MockRawResponse(object):
    def __init__(self, content, status_code, headers=None):
        self.content = content
        self.status_code = status_code
        self.headers = {} if headers is None else headers


@pytest.fixture
def set_api_key(monkeypatch):
    monkeypatch.setattr(workos, "api_key", "sk_abdsomecharactersm284")


@pytest.fixture
def set_client_id(monkeypatch):
    monkeypatch.setattr(workos, "client_id", "client_b27needthisforssotemxo")


@pytest.fixture
def set_api_key_and_client_id(set_api_key, set_client_id):
    pass


@pytest.fixture
def mock_request_method(monkeypatch):
    def inner(method, response_dict, status_code, headers=None):
        def mock(*args, **kwargs):
            return MockResponse(response_dict, status_code, headers=headers)

        monkeypatch.setattr(requests, method, mock)

    return inner


@pytest.fixture
def mock_raw_request_method(monkeypatch):
    def inner(method, content, status_code, headers=None):
        def mock(*args, **kwargs):
            return MockRawResponse(content, status_code, headers=headers)

        monkeypatch.setattr(requests, method, mock)

    return inner


@pytest.fixture
def capture_and_mock_request(monkeypatch):
    def inner(method, response_dict, status_code, headers=None):
        request_args = []
        request_kwargs = {}

        def capture_and_mock(*args, **kwargs):
            request_args.extend(args)
            request_kwargs.update(kwargs)

            return MockResponse(response_dict, status_code, headers=headers)

        monkeypatch.setattr(requests, method, capture_and_mock)

        return (request_args, request_kwargs)

    return inner
