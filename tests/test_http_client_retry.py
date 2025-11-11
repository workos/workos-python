from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import httpx

from workos.utils._base_http_client import RetryConfig
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.exceptions import ServerException, BadRequestException


class TestSyncRetryLogic:
    """Test retry logic for synchronous HTTP client."""

    @pytest.fixture
    def sync_http_client(self):
        """Create a SyncHTTPClient for testing."""
        return SyncHTTPClient(
            api_key="sk_test",
            base_url="https://api.workos.test/",
            client_id="client_test",
            version="test",
        )

    @pytest.fixture
    def retry_config(self):
        """Create a RetryConfig for testing."""
        return RetryConfig(
            max_retries=3,
            base_delay=0.1,  # Use shorter delays for faster tests
            max_delay=1.0,
            jitter=0.0,  # No jitter for predictable tests
        )

    @staticmethod
    def create_mock_request_with_retries(
        failure_count: int,
        failure_response=None,
        failure_exception=None,
        success_response=None,
    ):
        """
        Create a mock request function that fails N times before succeeding.

        Args:
            failure_count: Number of times to fail before success
            failure_response: Response to return on failure (status_code, json, headers)
            failure_exception: Exception to raise on failure (instead of response)
            success_response: Response to return on success (default: 200 with {"success": True})

        Returns:
            A tuple of (mock_function, call_count_tracker) where call_count_tracker
            is a list that tracks the number of calls
        """
        call_count = [0]  # Use list to allow modification in nested function

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= failure_count:
                if failure_exception:
                    raise failure_exception
                if failure_response:
                    return httpx.Response(**failure_response)

            if success_response:
                return httpx.Response(**success_response)
            return httpx.Response(status_code=200, json={"success": True})

        return mock_request, call_count

    def assert_request_with_retries(
        self,
        http_client,
        call_count,
        expected_call_count: int,
        expected_sleep_count: int,
        retry_config=None,
        expected_response=None,
    ):
        """
        Helper to execute a request with mocked sleep and assert the results.

        Args:
            http_client: The HTTP client to test with
            call_count: The call count tracker from create_mock_request_with_retries
            expected_call_count: Expected number of request attempts
            expected_sleep_count: Expected number of sleep calls
            retry_config: Optional retry configuration
            expected_response: Expected response dict (default: {"success": True})
        """
        if expected_response is None:
            expected_response = {"success": True}

        with patch("time.sleep") as mock_sleep:
            if retry_config:
                response = http_client.request("test/path", retry_config=retry_config)
            else:
                response = http_client.request("test/path")

            assert call_count[0] == expected_call_count
            assert response == expected_response
            assert mock_sleep.call_count == expected_sleep_count

    def test_retries_on_408_error(self, sync_http_client, retry_config, monkeypatch):
        """Test that 408 (Request Timeout) errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=3,
            failure_response={"status_code": 408, "json": {"error": "Request timeout"}},
        )

        monkeypatch.setattr(
            sync_http_client._client, "request", MagicMock(side_effect=mock_request)
        )

        self.assert_request_with_retries(
            sync_http_client, call_count, expected_call_count=4, expected_sleep_count=3, retry_config=retry_config
        )

    def test_retries_on_500_error(self, sync_http_client, retry_config, monkeypatch):
        """Test that 500 errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=3,
            failure_response={"status_code": 500, "json": {"error": "Server error"}},
        )

        monkeypatch.setattr(
            sync_http_client._client, "request", MagicMock(side_effect=mock_request)
        )

        self.assert_request_with_retries(
            sync_http_client, call_count, expected_call_count=4, expected_sleep_count=3, retry_config=retry_config
        )

    def test_retries_on_502_error(self, sync_http_client, retry_config, monkeypatch):
        """Test that 502 (Bad Gateway) errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=3,
            failure_response={"status_code": 502, "json": {"error": "Bad gateway"}},
        )

        monkeypatch.setattr(
            sync_http_client._client, "request", MagicMock(side_effect=mock_request)
        )

        self.assert_request_with_retries(
            sync_http_client, call_count, expected_call_count=4, expected_sleep_count=3, retry_config=retry_config
        )

    def test_retries_on_504_error(self, sync_http_client, retry_config, monkeypatch):
        """Test that 504 (Gateway Timeout) errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=3,
            failure_response={"status_code": 504, "json": {"error": "Gateway timeout"}},
        )

        monkeypatch.setattr(
            sync_http_client._client, "request", MagicMock(side_effect=mock_request)
        )

        self.assert_request_with_retries(
            sync_http_client, call_count, expected_call_count=4, expected_sleep_count=3, retry_config=retry_config
        )

    def test_no_retry_on_non_retryable_error(self, sync_http_client, retry_config, monkeypatch):
        """Test that a non retryable error errors do NOT trigger retry (not in RETRY_STATUS_CODES)."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=100,  # Always fail
            failure_response={
                "status_code": 503,
                "json": {"error": "Service unavailable"},
            },
        )

        monkeypatch.setattr(
            sync_http_client._client, "request", MagicMock(side_effect=mock_request)
        )

        with pytest.raises(ServerException):
            sync_http_client.request("test/path", retry_config=retry_config)

        # Should only be called once (no retries on 503)
        assert call_count[0] == 1

    def test_respects_max_retries(self, sync_http_client, retry_config, monkeypatch):
        """Test that max retries limit is respected."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=100,  # Always fail
            failure_response={"status_code": 500, "json": {"error": "Server error"}},
        )

        monkeypatch.setattr(
            sync_http_client._client, "request", MagicMock(side_effect=mock_request)
        )

        with patch("time.sleep"):
            with pytest.raises(ServerException):
                sync_http_client.request("test/path", retry_config=retry_config)

        # Should be called max_retries + 1 times (initial + 3 retries)
        assert call_count[0] == 4

    def test_retries_on_network_error(
        self, sync_http_client, retry_config, monkeypatch
    ):
        """Test that network errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=2, failure_exception=httpx.ConnectError("Connection failed")
        )

        monkeypatch.setattr(
            sync_http_client._client, "request", MagicMock(side_effect=mock_request)
        )

        with patch("time.sleep"):
            response = sync_http_client.request("test/path", retry_config=retry_config)

            assert call_count[0] == 3
            assert response == {"success": True}

    def test_retries_on_timeout_error(
        self, sync_http_client, retry_config, monkeypatch
    ):
        """Test that timeout errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=1,
            failure_exception=httpx.TimeoutException("Request timed out"),
        )

        monkeypatch.setattr(
            sync_http_client._client, "request", MagicMock(side_effect=mock_request)
        )

        with patch("time.sleep"):
            response = sync_http_client.request("test/path", retry_config=retry_config)

            assert call_count[0] == 2
            assert response == {"success": True}

    def test_no_retry_on_success(self, sync_http_client, monkeypatch):
        """Test that successful requests don't retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=0  # Success immediately
        )

        monkeypatch.setattr(
            sync_http_client._client, "request", MagicMock(side_effect=mock_request)
        )

        response = sync_http_client.request("test/path")

        assert call_count[0] == 1
        assert response == {"success": True}


class TestAsyncRetryLogic:
    """Test retry logic for asynchronous HTTP client."""

    @pytest.fixture
    def async_http_client(self):
        """Create an AsyncHTTPClient for testing."""
        return AsyncHTTPClient(
            api_key="sk_test",
            base_url="https://api.workos.test/",
            client_id="client_test",
            version="test",
        )

    @pytest.fixture
    def retry_config(self):
        """Create a RetryConfig for testing."""
        return RetryConfig(
            max_retries=3,
            base_delay=0.1,  # Use shorter delays for faster tests
            max_delay=1.0,
            jitter=0.0,  # No jitter for predictable tests
        )

    @staticmethod
    def create_mock_request_with_retries(
        failure_count: int,
        failure_response=None,
        failure_exception=None,
        success_response=None,
    ):
        """
        Create an async mock request function that fails N times before succeeding.

        Args:
            failure_count: Number of times to fail before success
            failure_response: Response to return on failure (status_code, json, headers)
            failure_exception: Exception to raise on failure (instead of response)
            success_response: Response to return on success (default: 200 with {"success": True})

        Returns:
            A tuple of (mock_function, call_count_tracker) where call_count_tracker
            is a list that tracks the number of calls
        """
        call_count = [0]  # Use list to allow modification in nested function

        async def mock_request(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= failure_count:
                if failure_exception:
                    raise failure_exception
                if failure_response:
                    return httpx.Response(**failure_response)

            if success_response:
                return httpx.Response(**success_response)
            return httpx.Response(status_code=200, json={"success": True})

        return mock_request, call_count

    async def assert_async_request_with_retries(
        self,
        http_client,
        call_count,
        expected_call_count: int,
        expected_sleep_count: int,
        retry_config=None,
        expected_response=None,
    ):
        """
        Helper to execute an async request with mocked sleep and assert the results.

        Args:
            http_client: The HTTP client to test with
            call_count: The call count tracker from create_mock_request_with_retries
            expected_call_count: Expected number of request attempts
            expected_sleep_count: Expected number of sleep calls
            retry_config: Optional retry configuration
            expected_response: Expected response dict (default: {"success": True})
        """
        if expected_response is None:
            expected_response = {"success": True}

        with patch("asyncio.sleep") as mock_sleep:
            if retry_config:
                response = await http_client.request("test/path", retry_config=retry_config)
            else:
                response = await http_client.request("test/path")

            assert call_count[0] == expected_call_count
            assert response == expected_response
            assert mock_sleep.call_count == expected_sleep_count

    @pytest.mark.asyncio
    async def test_retries_on_408_error(
        self, async_http_client, retry_config, monkeypatch
    ):
        """Test that 408 (Request Timeout) errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=3,
            failure_response={"status_code": 408, "json": {"error": "Request timeout"}},
        )

        monkeypatch.setattr(
            async_http_client._client, "request", AsyncMock(side_effect=mock_request)
        )

        await self.assert_async_request_with_retries(
            async_http_client, call_count, expected_call_count=4, expected_sleep_count=3, retry_config=retry_config
        )

    @pytest.mark.asyncio
    async def test_retries_on_500_error(
        self, async_http_client, retry_config, monkeypatch
    ):
        """Test that 500 errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=3,
            failure_response={"status_code": 500, "json": {"error": "Server error"}},
        )

        monkeypatch.setattr(
            async_http_client._client, "request", AsyncMock(side_effect=mock_request)
        )

        await self.assert_async_request_with_retries(
            async_http_client, call_count, expected_call_count=4, expected_sleep_count=3, retry_config=retry_config
        )

    @pytest.mark.asyncio
    async def test_retries_on_502_error(
        self, async_http_client, retry_config, monkeypatch
    ):
        """Test that 502 (Bad Gateway) errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=3,
            failure_response={"status_code": 502, "json": {"error": "Bad gateway"}},
        )

        monkeypatch.setattr(
            async_http_client._client, "request", AsyncMock(side_effect=mock_request)
        )

        await self.assert_async_request_with_retries(
            async_http_client, call_count, expected_call_count=4, expected_sleep_count=3, retry_config=retry_config
        )

    @pytest.mark.asyncio
    async def test_retries_on_504_error(
        self, async_http_client, retry_config, monkeypatch
    ):
        """Test that 504 (Gateway Timeout) errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=3,
            failure_response={"status_code": 504, "json": {"error": "Gateway timeout"}},
        )

        monkeypatch.setattr(
            async_http_client._client, "request", AsyncMock(side_effect=mock_request)
        )

        await self.assert_async_request_with_retries(
            async_http_client, call_count, expected_call_count=4, expected_sleep_count=3, retry_config=retry_config
        )

    @pytest.mark.asyncio
    async def test_no_retry_on_non_retryable_error(
        self, async_http_client, retry_config, monkeypatch
    ):
        """Test that a non retryable error errors do NOT trigger retry (not in RETRY_STATUS_CODES)."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=100,  # Always fail
            failure_response={
                "status_code": 503,
                "json": {"error": "Service unavailable"},
            },
        )

        monkeypatch.setattr(
            async_http_client._client, "request", AsyncMock(side_effect=mock_request)
        )

        with pytest.raises(ServerException):
            await async_http_client.request("test/path", retry_config=retry_config)

        # Should only be called once (no retries on 503)
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_respects_max_retries(
        self, async_http_client, retry_config, monkeypatch
    ):
        """Test that max retries limit is respected."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=100,  # Always fail
            failure_response={"status_code": 500, "json": {"error": "Server error"}},
        )

        monkeypatch.setattr(
            async_http_client._client, "request", AsyncMock(side_effect=mock_request)
        )

        with patch("asyncio.sleep"):
            with pytest.raises(ServerException):
                await async_http_client.request("test/path", retry_config=retry_config)

        # Should be called max_retries + 1 times (initial + 3 retries)
        assert call_count[0] == 4

    @pytest.mark.asyncio
    async def test_retries_on_network_error(
        self, async_http_client, retry_config, monkeypatch
    ):
        """Test that network errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=2, failure_exception=httpx.ConnectError("Connection failed")
        )

        monkeypatch.setattr(
            async_http_client._client, "request", AsyncMock(side_effect=mock_request)
        )

        with patch("asyncio.sleep"):
            response = await async_http_client.request(
                "test/path", retry_config=retry_config
            )

            assert call_count[0] == 3
            assert response == {"success": True}

    @pytest.mark.asyncio
    async def test_retries_on_timeout_error(
        self, async_http_client, retry_config, monkeypatch
    ):
        """Test that timeout errors trigger retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=1,
            failure_exception=httpx.TimeoutException("Request timed out"),
        )

        monkeypatch.setattr(
            async_http_client._client, "request", AsyncMock(side_effect=mock_request)
        )

        with patch("asyncio.sleep"):
            response = await async_http_client.request(
                "test/path", retry_config=retry_config
            )

            assert call_count[0] == 2
            assert response == {"success": True}

    @pytest.mark.asyncio
    async def test_no_retry_on_success(self, async_http_client, monkeypatch):
        """Test that successful requests don't retry."""
        mock_request, call_count = self.create_mock_request_with_retries(
            failure_count=0  # Success immediately
        )

        monkeypatch.setattr(
            async_http_client._client, "request", AsyncMock(side_effect=mock_request)
        )

        response = await async_http_client.request("test/path")

        assert call_count[0] == 1
        assert response == {"success": True}
