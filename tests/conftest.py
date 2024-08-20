from typing import Any, Callable, Mapping, Optional
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from tests.utils.client_configuration import ClientConfiguration
from tests.utils.list_resource import list_data_to_dicts, list_response_of
from workos.types.list_resource import WorkOSListResource
from workos.utils._base_http_client import DEFAULT_REQUEST_TIMEOUT
from workos.utils.http_client import AsyncHTTPClient, HTTPClient, SyncHTTPClient
from workos.utils.request_helper import DEFAULT_LIST_RESPONSE_LIMIT


_TEST_HTTP_CLIENTS = {
    "sync": SyncHTTPClient(
        api_key="sk_test",
        base_url="https://api.workos.test/",
        client_id="client_b27needthisforssotemxo",
        version="test",
    ),
    "async": AsyncHTTPClient(
        api_key="sk_test",
        base_url="https://api.workos.test/",
        client_id="client_b27needthisforssotemxo",
        version="test",
    ),
}


def pytest_configure(config) -> None:
    config.addinivalue_line(
        "markers", "sync_and_async(): mark test to run both sync and async versions"
    )


def pytest_generate_tests(metafunc: pytest.Metafunc):
    for marker in metafunc.definition.iter_markers(name="sync_and_async"):
        if marker.name == "sync_and_async":
            if len(marker.args) == 0:
                raise ValueError(
                    "sync_and_async marker requires module setups argument"
                )

            module_setup = marker.args[0]
            if "sync" not in module_setup or "async" not in module_setup:
                raise ValueError(
                    "sync_and_async marker requires sync and async module setups."
                )

            ids = []
            arg_values = []

            for setup_name, module_class in module_setup.items():
                if module_class is None:
                    raise ValueError(
                        f"Invalid module for test module setup: {module_class}"
                    )

                ids.append(setup_name)  # sync or async will be the test ID
                arg_names = ["http_client", "module_class"]
                arg_values.append([_TEST_HTTP_CLIENTS[setup_name], module_class])

            metafunc.parametrize(
                argnames=arg_names, argvalues=arg_values, ids=ids, scope="class"
            )


@pytest.fixture
def sync_http_client_for_test():
    return _TEST_HTTP_CLIENTS["sync"]


@pytest.fixture
def async_http_client_for_test():
    return _TEST_HTTP_CLIENTS["async"]


@pytest.fixture
def sync_client_configuration_and_http_client_for_test():
    base_url = "https://api.workos.test/"
    client_id = "client_b27needthisforssotemxo"

    client_configuration = ClientConfiguration(
        base_url=base_url, client_id=client_id, request_timeout=DEFAULT_REQUEST_TIMEOUT
    )

    http_client = SyncHTTPClient(
        api_key="sk_test",
        base_url=base_url,
        client_id=client_id,
        version="test",
    )

    return client_configuration, http_client


@pytest.fixture
def async_client_configuration_and_http_client_for_test():
    base_url = "https://api.workos.test/"
    client_id = "client_b27needthisforssotemxo"

    client_configuration = ClientConfiguration(
        base_url=base_url, client_id=client_id, request_timeout=DEFAULT_REQUEST_TIMEOUT
    )

    http_client = AsyncHTTPClient(
        api_key="sk_test",
        base_url=base_url,
        client_id=client_id,
        version="test",
    )

    return client_configuration, http_client


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
def capture_and_mock_pagination_request_for_http_client(monkeypatch):
    # Mocking pagination correctly requires us to index into a list of data
    # and correctly set the before and after metadata in the response.
    def inner(
        http_client: HTTPClient,
        data_list: list,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
    ):
        request_kwargs = {}

        # For convenient index lookup, store the list of object IDs.
        data_ids = list(map(lambda x: x["id"], data_list))

        def mock_function(*args, **kwargs):
            request_kwargs.update(kwargs)

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

        return request_kwargs

    return inner


@pytest.fixture
def test_sync_auto_pagination(capture_and_mock_pagination_request_for_http_client):
    def inner(
        http_client: SyncHTTPClient,
        list_function: Callable[[], WorkOSListResource],
        expected_all_page_data: dict,
        list_function_params: Optional[Mapping[str, Any]] = None,
    ):
        request_kwargs = capture_and_mock_pagination_request_for_http_client(
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
        assert request_kwargs["method"] == "get"

        # Validate parameters
        assert "after" in request_kwargs["params"]
        assert request_kwargs["params"]["limit"] == DEFAULT_LIST_RESPONSE_LIMIT
        assert request_kwargs["params"]["order"] == "desc"

        params = list_function_params or {}
        for param in params:
            assert request_kwargs["params"][param] == params[param]

    return inner
