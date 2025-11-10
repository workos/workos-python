import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, Mock, patch
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

    def test_retries_on_500_error(self, sync_http_client, retry_config, monkeypatch):
        """Test that 500 errors trigger retry."""
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return httpx.Response(status_code=500, json={"error": "Server error"})
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        with patch("time.sleep") as mock_sleep:
            response = sync_http_client.request("test/path", retry_config=retry_config)
            
            assert call_count == 3
            assert response == {"success": True}
            # Verify sleep was called with exponential backoff
            assert mock_sleep.call_count == 2

    def test_retries_on_429_rate_limit(self, sync_http_client, retry_config, monkeypatch):
        """Test that 429 errors trigger retry."""
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return httpx.Response(
                    status_code=429,
                    headers={"Retry-After": "0.1"},
                    json={"error": "Rate limit exceeded"}
                )
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        with patch("time.sleep") as mock_sleep:
            response = sync_http_client.request("test/path", retry_config=retry_config)
            
            assert call_count == 2
            assert response == {"success": True}
            # Verify Retry-After header was respected
            mock_sleep.assert_called_once_with(0.1)

    def test_no_retry_on_400_error(self, sync_http_client, monkeypatch):
        """Test that 4xx errors (except 429) don't retry (no retry_config passed)."""
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return httpx.Response(
                status_code=400,
                json={"error": "Bad request", "message": "Invalid data"}
            )
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        with pytest.raises(BadRequestException):
            sync_http_client.request("test/path")
        
        # Should only be called once (no retries)
        assert call_count == 1

    def test_no_retry_on_401_error(self, sync_http_client, monkeypatch):
        """Test that 401 errors don't retry (no retry_config passed)."""
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return httpx.Response(
                status_code=401,
                json={"error": "Unauthorized", "message": "Invalid credentials"}
            )
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        with pytest.raises(Exception):
            sync_http_client.request("test/path")
        
        # Should only be called once (no retries)
        assert call_count == 1

    def test_respects_max_retries(self, sync_http_client, retry_config, monkeypatch):
        """Test that max retries limit is respected."""
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return httpx.Response(status_code=500, json={"error": "Server error"})
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        with patch("time.sleep"):
            with pytest.raises(ServerException):
                sync_http_client.request("test/path", retry_config=retry_config)
        
        # Should be called max_retries + 1 times (initial + 3 retries)
        assert call_count == 4

    def test_exponential_backoff_delays(self, sync_http_client, retry_config, monkeypatch):
        """Test that retry delays follow exponential backoff."""
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                return httpx.Response(status_code=500, json={"error": "Server error"})
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        with patch("time.sleep") as mock_sleep:
            sync_http_client.request("test/path", retry_config=retry_config)
            
            # Verify exponential backoff: 0.1s, 0.2s, 0.4s
            assert mock_sleep.call_count == 3
            calls = [call[0][0] for call in mock_sleep.call_args_list]
            # Check that delays are increasing (exponential backoff)
            assert calls[0] < calls[1] < calls[2]

    def test_retries_on_network_error(self, sync_http_client, retry_config, monkeypatch):
        """Test that network errors trigger retry."""
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.ConnectError("Connection failed")
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        with patch("time.sleep"):
            response = sync_http_client.request("test/path", retry_config=retry_config)
            
            assert call_count == 3
            assert response == {"success": True}

    def test_retries_on_timeout_error(self, sync_http_client, retry_config, monkeypatch):
        """Test that timeout errors trigger retry."""
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.TimeoutException("Request timed out")
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        with patch("time.sleep"):
            response = sync_http_client.request("test/path", retry_config=retry_config)
            
            assert call_count == 2
            assert response == {"success": True}

    def test_no_retry_on_success(self, sync_http_client, monkeypatch):
        """Test that successful requests don't retry."""
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        response = sync_http_client.request("test/path")
        
        assert call_count == 1
        assert response == {"success": True}

    def test_retry_with_custom_config(self):
        """Test that RetryConfig can be customized with different values."""
        custom_retry_config = RetryConfig(
            max_retries=5,
            base_delay=0.05,
            max_delay=2.0,
            jitter=0.1,
        )
        
        # Verify custom values are set correctly
        assert custom_retry_config.max_retries == 5
        assert custom_retry_config.base_delay == 0.05
        assert custom_retry_config.max_delay == 2.0
        assert custom_retry_config.jitter == 0.1
        
        # Verify defaults are as expected
        default_retry_config = RetryConfig()
        assert default_retry_config.max_retries == 3
        assert default_retry_config.base_delay == 1.0
        assert default_retry_config.max_delay == 30.0
        assert default_retry_config.jitter == 0.25

    def test_retry_respects_max_delay(self, sync_http_client, monkeypatch):
        """Test that retry delays don't exceed max_delay."""
        # Create custom retry config with very low max_delay
        custom_retry_config = RetryConfig(
            max_retries=5,
            base_delay=1.0,
            max_delay=0.5,  # Max delay is lower than what exponential backoff would produce
            jitter=0.0,
        )
        
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 4:
                return httpx.Response(status_code=500, json={"error": "Server error"})
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        with patch("time.sleep") as mock_sleep:
            sync_http_client.request("test/path", retry_config=custom_retry_config)
            
            # All delays should be capped at max_delay
            calls = [call[0][0] for call in mock_sleep.call_args_list]
            for delay in calls:
                assert delay <= 0.5

    def test_mixed_retryable_and_non_retryable_errors(self, sync_http_client, retry_config, monkeypatch):
        """Test behavior when encountering different error types."""
        call_count = 0
        
        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(status_code=500, json={"error": "Server error"})
            elif call_count == 2:
                # Non-retryable error should stop retries
                return httpx.Response(status_code=403, json={"error": "Forbidden"})
        
        monkeypatch.setattr(sync_http_client._client, "request", MagicMock(side_effect=mock_request))
        
        with patch("time.sleep"):
            with pytest.raises(Exception):
                sync_http_client.request("test/path", retry_config=retry_config)
        
        # Should stop after the 403 error (no more retries)
        assert call_count == 2

    def test_default_retry_config(self):
        """Test that client has no retry config by default (opt-in behavior)."""
        client = SyncHTTPClient(
            api_key="sk_test",
            base_url="https://api.workos.test/",
            client_id="client_test",
            version="test",
        )
        
        # Should be None by default (no retries unless explicitly enabled)
        assert client._retry_config is None


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

    @pytest.mark.asyncio
    async def test_retries_on_500_error(self, async_http_client, retry_config, monkeypatch):
        """Test that 500 errors trigger retry."""
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return httpx.Response(status_code=500, json={"error": "Server error"})
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(async_http_client._client, "request", AsyncMock(side_effect=mock_request))
        
        with patch("asyncio.sleep") as mock_sleep:
            response = await async_http_client.request("test/path", retry_config=retry_config)
            
            assert call_count == 3
            assert response == {"success": True}
            # Verify sleep was called with exponential backoff
            assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_retries_on_429_rate_limit(self, async_http_client, retry_config, monkeypatch):
        """Test that 429 errors trigger retry."""
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return httpx.Response(
                    status_code=429,
                    headers={"Retry-After": "0.1"},
                    json={"error": "Rate limit exceeded"}
                )
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(async_http_client._client, "request", AsyncMock(side_effect=mock_request))
        
        with patch("asyncio.sleep") as mock_sleep:
            response = await async_http_client.request("test/path", retry_config=retry_config)
            
            assert call_count == 2
            assert response == {"success": True}
            # Verify Retry-After header was respected
            mock_sleep.assert_called_once_with(0.1)

    @pytest.mark.asyncio
    async def test_no_retry_on_400_error(self, async_http_client, monkeypatch):
        """Test that 4xx errors (except 429) don't retry (no retry_config passed)."""
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return httpx.Response(
                status_code=400,
                json={"error": "Bad request", "message": "Invalid data"}
            )
        
        monkeypatch.setattr(async_http_client._client, "request", AsyncMock(side_effect=mock_request))
        
        with pytest.raises(BadRequestException):
            await async_http_client.request("test/path")
        
        # Should only be called once (no retries)
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_respects_max_retries(self, async_http_client, retry_config, monkeypatch):
        """Test that max retries limit is respected."""
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return httpx.Response(status_code=500, json={"error": "Server error"})
        
        monkeypatch.setattr(async_http_client._client, "request", AsyncMock(side_effect=mock_request))
        
        with patch("asyncio.sleep"):
            with pytest.raises(ServerException):
                await async_http_client.request("test/path", retry_config=retry_config)
        
        # Should be called max_retries + 1 times (initial + 3 retries)
        assert call_count == 4

    @pytest.mark.asyncio
    async def test_exponential_backoff_delays(self, async_http_client, retry_config, monkeypatch):
        """Test that retry delays follow exponential backoff."""
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                return httpx.Response(status_code=500, json={"error": "Server error"})
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(async_http_client._client, "request", AsyncMock(side_effect=mock_request))
        
        with patch("asyncio.sleep") as mock_sleep:
            await async_http_client.request("test/path", retry_config=retry_config)
            
            # Verify exponential backoff: 0.1s, 0.2s, 0.4s
            assert mock_sleep.call_count == 3
            calls = [call[0][0] for call in mock_sleep.call_args_list]
            # Check that delays are increasing (exponential backoff)
            assert calls[0] < calls[1] < calls[2]

    @pytest.mark.asyncio
    async def test_retries_on_network_error(self, async_http_client, retry_config, monkeypatch):
        """Test that network errors trigger retry."""
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.ConnectError("Connection failed")
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(async_http_client._client, "request", AsyncMock(side_effect=mock_request))
        
        with patch("asyncio.sleep"):
            response = await async_http_client.request("test/path", retry_config=retry_config)
            
            assert call_count == 3
            assert response == {"success": True}

    @pytest.mark.asyncio
    async def test_retries_on_timeout_error(self, async_http_client, retry_config, monkeypatch):
        """Test that timeout errors trigger retry."""
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.TimeoutException("Request timed out")
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(async_http_client._client, "request", AsyncMock(side_effect=mock_request))
        
        with patch("asyncio.sleep"):
            response = await async_http_client.request("test/path", retry_config=retry_config)
            
            assert call_count == 2
            assert response == {"success": True}

    @pytest.mark.asyncio
    async def test_no_retry_on_success(self, async_http_client, monkeypatch):
        """Test that successful requests don't retry (no retry_config needed)."""
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return httpx.Response(status_code=200, json={"success": True})
        
        monkeypatch.setattr(async_http_client._client, "request", AsyncMock(side_effect=mock_request))
        
        response = await async_http_client.request("test/path")
        
        assert call_count == 1
        assert response == {"success": True}

    def test_default_retry_config(self):
        """Test that client has no retry config by default (opt-in behavior)."""
        client = AsyncHTTPClient(
            api_key="sk_test",
            base_url="https://api.workos.test/",
            client_id="client_test",
            version="test",
        )
        
        # Should be None by default (no retries unless explicitly enabled)
        assert client._retry_config is None

