from typing import (
    Any,
    Awaitable,
    Callable,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from tests.utils.client_configuration import ClientConfiguration
from tests.utils.list_resource import list_data_to_dicts, list_response_of
from tests.utils.syncify import syncify
from tests.types.test_auto_pagination_function import TestAutoPaginationFunction
from workos.types.list_resource import WorkOSListResource
from workos.utils._base_http_client import DEFAULT_REQUEST_TIMEOUT
from workos.utils.http_client import AsyncHTTPClient, HTTPClient, SyncHTTPClient
from workos.utils.request_helper import DEFAULT_LIST_RESPONSE_LIMIT

from jwt import PyJWKClient
from unittest.mock import Mock, patch
from functools import wraps

def _get_test_client_setup(
    http_client_class_name: str,
) -> Tuple[Literal["async", "sync"], ClientConfiguration, HTTPClient]:
    base_url = "https://api.workos.test/"
    client_id = "client_b27needthisforssotemxo"

    setup_name = None
    if http_client_class_name == "AsyncHTTPClient":
        http_client = AsyncHTTPClient(
            api_key="sk_test",
            base_url=base_url,
            client_id=client_id,
            version="test",
        )
        setup_name = "async"
    elif http_client_class_name == "SyncHTTPClient":
        http_client = SyncHTTPClient(
            api_key="sk_test",
            base_url=base_url,
            client_id=client_id,
            version="test",
        )
        setup_name = "sync"
    else:
        raise ValueError(
            f"Invalid HTTP client for test module setup: {http_client_class_name}"
        )

    client_configuration = ClientConfiguration(
        base_url=base_url, client_id=client_id, request_timeout=DEFAULT_REQUEST_TIMEOUT
    )

    return setup_name, client_configuration, http_client


def pytest_configure(config) -> None:
    config.addinivalue_line(
        "markers",
        "sync_and_async(): mark test to run both sync and async module versions",
    )


def pytest_generate_tests(metafunc: pytest.Metafunc):
    for marker in metafunc.definition.iter_markers(name="sync_and_async"):
        if marker.name == "sync_and_async":
            if len(marker.args) == 0:
                raise ValueError(
                    "sync_and_async marker requires argument representing list of modules."
                )

            # Take in args as a list of module classes. For example:
            # @pytest.mark.sync_and_async(Events, AsyncEvents) -> [Events, AsyncEvents]
            module_classes = marker.args
            ids = []
            arg_values = []

            for module_class in module_classes:
                if module_class is None:
                    raise ValueError(
                        f"Invalid module class for sync_and_async marker: {module_class}"
                    )

                # Pull the HTTP client type from the module class annotations and use that
                # to pass in the proper test HTTP client
                http_client_name = module_class.__annotations__["_http_client"].__name__
                setup_name, client_configuration, http_client = _get_test_client_setup(
                    http_client_name
                )

                class_kwargs: Mapping[str, Any] = {"http_client": http_client}
                if module_class.__init__.__annotations__.get(
                    "client_configuration", None
                ):
                    class_kwargs["client_configuration"] = client_configuration

                module_instance = module_class(**class_kwargs)

                ids.append(setup_name)  # sync or async will be the test ID
                arg_names = ["module_instance"]
                arg_values.append([module_instance])

            metafunc.parametrize(
                argnames=arg_names, argvalues=arg_values, ids=ids, scope="class"
            )


@pytest.fixture
def sync_http_client_for_test():
    _, _, http_client = _get_test_client_setup("SyncHTTPClient")
    return http_client


@pytest.fixture
def sync_client_configuration_and_http_client_for_test():
    _, client_configuration, http_client = _get_test_client_setup("SyncHTTPClient")
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
def test_auto_pagination(
    capture_and_mock_pagination_request_for_http_client,
) -> TestAutoPaginationFunction:
    def _iterate_results_sync(
        list_function: Callable[[], WorkOSListResource],
        list_function_params: Optional[Mapping[str, Any]] = None,
    ) -> Sequence[Any]:
        results = list_function(**list_function_params or {})
        all_results = []

        for result in results:
            all_results.append(result)

        return all_results

    async def _iterate_results_async(
        list_function: Callable[[], Awaitable[WorkOSListResource]],
        list_function_params: Optional[Mapping[str, Any]] = None,
    ) -> Sequence[Any]:
        results = await list_function(**list_function_params or {})
        all_results = []

        async for result in results:
            all_results.append(result)

        return all_results

    def inner(
        http_client: HTTPClient,
        list_function: Union[
            Callable[[], WorkOSListResource],
            Callable[[], Awaitable[WorkOSListResource]],
        ],
        expected_all_page_data: dict,
        list_function_params: Optional[Mapping[str, Any]] = None,
        url_path_keys: Optional[Sequence[str]] = None,
    ) -> None:
        request_kwargs = capture_and_mock_pagination_request_for_http_client(
            http_client=http_client,
            data_list=expected_all_page_data,
            status_code=200,
        )

        all_results = []
        if isinstance(http_client, AsyncHTTPClient):
            all_results = syncify(
                _iterate_results_async(
                    cast(Callable[[], Awaitable[WorkOSListResource]], list_function),
                    list_function_params,
                )
            )
        else:
            all_results = _iterate_results_sync(
                cast(Callable[[], WorkOSListResource], list_function),
                list_function_params,
            )

        assert len(list(all_results)) == len(expected_all_page_data)
        assert (list_data_to_dicts(all_results)) == expected_all_page_data
        assert request_kwargs["method"] == "get"

        # Validate parameters
        assert "after" in request_kwargs["params"]
        assert request_kwargs["params"]["limit"] == DEFAULT_LIST_RESPONSE_LIMIT
        assert request_kwargs["params"]["order"] == "desc"

        params = list_function_params or {}
        for param in params:
            if url_path_keys is not None and param not in url_path_keys:
                assert request_kwargs["params"][param] == params[param]

    return inner

def with_jwks_mock(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create mock JWKS client
        mock_jwks = Mock(spec=PyJWKClient)
        mock_signing_key = Mock()
        mock_signing_key.key = kwargs['TEST_CONSTANTS']["PUBLIC_KEY"]
        mock_jwks.get_signing_key_from_jwt.return_value = mock_signing_key

        # Apply the mock
        with patch('workos.session.PyJWKClient', return_value=mock_jwks):
            return func(*args, **kwargs)
    return wrapper