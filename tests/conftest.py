from typing import Any, Callable, Mapping, Optional, Union
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from tests.utils.list_resource import list_data_to_dicts, list_response_of
import workos
from workos.resources.list import WorkOsListResource
from workos.utils.http_client import AsyncHTTPClient, HTTPClient, SyncHTTPClient


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
def mock_http_client_with_response(monkeypatch):
    def inner(
        http_client: HTTPClient,
        response_dict: Optional[dict] = None,
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
def capture_and_mock_http_client_request(monkeypatch):
    def inner(
        http_client: HTTPClient,
        response_dict: Optional[dict] = None,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
    ):
        request_kwargs = {}

        def capture_and_mock(*args, **kwargs):
            request_kwargs.update(kwargs)

            return httpx.Response(
                status_code=status_code,
                headers=headers,
                json=response_dict,
            )

        mock_class = (
            AsyncMock if isinstance(http_client, AsyncHTTPClient) else MagicMock
        )
        mock = mock_class(side_effect=capture_and_mock)

        monkeypatch.setattr(http_client._client, "request", mock)

        return request_kwargs

    return inner


@pytest.fixture
def mock_pagination_request_for_http_client(monkeypatch):
    # Mocking pagination correctly requires us to index into a list of data
    # and correctly set the before and after metadata in the response.
    def inner(
        http_client: HTTPClient,
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


@pytest.fixture
def test_sync_auto_pagination(
    mock_pagination_request_for_http_client,
):
    def inner(
        http_client: HTTPClient,
        list_function: Callable[[], WorkOsListResource],
        expected_all_page_data: dict,
        list_function_params: Optional[Mapping[str, Any]] = None,
    ):
        mock_pagination_request_for_http_client(
            http_client=http_client,
            data_list=expected_all_page_data,
            status_code=200,
        )

        results = list_function(**list_function_params or {})
        all_results = []

        for result in results:
            all_results.append(result)

        assert len(list(all_results)) == len(expected_all_page_data)
        assert (list_data_to_dicts(all_results)) == expected_all_page_data

    return inner
