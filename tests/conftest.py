from typing import Mapping, Optional, Union
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import requests

from tests.utils.list_resource import list_response_of
import workos
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient


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
    monkeypatch.setattr(workos, "api_key", "sk_test")


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

        monkeypatch.setattr(requests, "request", mock)

    return inner


@pytest.fixture
def mock_raw_request_method(monkeypatch):
    def inner(method, content, status_code, headers=None):
        def mock(*args, **kwargs):
            return MockRawResponse(content, status_code, headers=headers)

        monkeypatch.setattr(requests, "request", mock)

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

        monkeypatch.setattr(requests, "request", capture_and_mock)

        return (request_args, request_kwargs)

    return inner


@pytest.fixture
def mock_pagination_request(monkeypatch):
    # Mocking pagination correctly requires us to index into a list of data
    # and correctly set the before and after metadata in the response.
    def inner(method, data_list, status_code, headers=None):
        # For convenient index lookup, store the list of object IDs.
        data_ids = list(map(lambda x: x["id"], data_list))

        def mock(*args, **kwargs):
            params = kwargs.get("params") or {}
            request_after = params.get("after", None)
            limit = params.get("limit", 10)

            if request_after is None:
                # First page
                start = 0
            else:
                # A subsequent page, return the first item _after_ the index we locate
                start = data_ids.index(request_after) + 1
            data = data_list[start : start + limit]
            if len(data) < limit or len(data) == 0:
                # No more data, set after to None
                after = None
            else:
                # Set after to the last item in this page of results
                after = data[-1]["id"]

            return MockResponse(
                list_response_of(data=data, before=request_after, after=after),
                status_code,
                headers=headers,
            )

        monkeypatch.setattr(requests, "request", mock)

    return inner


@pytest.fixture
def mock_http_client_with_response(monkeypatch):
    def inner(
        http_client: Union[SyncHTTPClient, AsyncHTTPClient],
        response_dict: dict,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
    ):
        mock_class = (
            AsyncMock if isinstance(http_client, AsyncHTTPClient) else MagicMock
        )
        mock = mock_class(
            return_value=httpx.Response(
                status_code=status_code, headers=headers, json=response_dict
            ),
        )
        monkeypatch.setattr(http_client._client, "request", mock)

    return inner


@pytest.fixture
def mock_pagination_request_for_http_client(monkeypatch):
    # Mocking pagination correctly requires us to index into a list of data
    # and correctly set the before and after metadata in the response.
    def inner(
        http_client: Union[SyncHTTPClient, AsyncHTTPClient],
        data_list: list,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
    ):
        # For convenient index lookup, store the list of object IDs.
        data_ids = list(map(lambda x: x["id"], data_list))

        def mock_function(*args, **kwargs):
            params = kwargs.get("params") or {}
            request_after = params.get("after", None)
            limit = params.get("limit", 10)

            if request_after is None:
                # First page
                start = 0
            else:
                # A subsequent page, return the first item _after_ the index we locate
                start = data_ids.index(request_after) + 1
            data = data_list[start : start + limit]
            if len(data) < limit or len(data) == 0:
                # No more data, set after to None
                after = None
            else:
                # Set after to the last item in this page of results
                after = data[-1]["id"]

            return httpx.Response(
                status_code=status_code,
                headers=headers,
                json=list_response_of(data=data, before=request_after, after=after),
            )

        mock_class = (
            AsyncMock if isinstance(http_client, AsyncHTTPClient) else MagicMock
        )
        mock = mock_class(side_effect=mock_function)

        monkeypatch.setattr(http_client._client, "request", mock)

    return inner
