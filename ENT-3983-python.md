# ENT-3983: Python SDK Implementation Plan

## Overview
Implement automatic idempotency key generation and retry logic with exponential backoff for audit log event creation in the WorkOS Python SDK.

## Current State

### File Structure
- **Audit Logs**: `workos/audit_logs.py` (lines 75-90)
  - `create_event()` accepts optional `idempotency_key` parameter
  - Only sets header if idempotency key is provided
  - No auto-generation logic

- **HTTP Client**: 
  - Base: `workos/utils/_base_http_client.py` 
  - Implementations: `workos/utils/http_client.py` (SyncHTTPClient + AsyncHTTPClient)
  - Uses `httpx` library for HTTP requests
  - No retry logic implemented

- **Error Handling**: `workos/exceptions.py`
  - Has `ServerException` for 5xx errors (line 82)
  - No distinction between retryable/non-retryable errors

- **Tests**: `tests/test_audit_logs.py`
  - Test exists for manually provided idempotency key (lines 89-107)
  - No tests for auto-generation or retry logic

## Implementation Tasks

### 1. Add Automatic Idempotency Key Generation

**File**: `workos/audit_logs.py`

**Changes in `create_event()` method (lines 75-90)**:
```python
import uuid

def create_event(
    self,
    *,
    organization_id: str,
    event: AuditLogEvent,
    idempotency_key: Optional[str] = None,
) -> None:
    json = {"organization_id": organization_id, "event": event}

    headers = {}
    # Auto-generate UUID v4 if not provided
    if idempotency_key is None:
        idempotency_key = str(uuid.uuid4())
    
    headers["idempotency-key"] = idempotency_key

    self._http_client.request(
        EVENTS_PATH, method=REQUEST_METHOD_POST, json=json, headers=headers
    )
```

**Key Points**:
- Import Python's built-in `uuid` module (no new dependency)
- Generate UUID v4 using `uuid.uuid4()` if `idempotency_key` is `None`
- Always set the header (simplifies logic)
- User-provided keys still take precedence (backward compatible)

### 2. Implement Retry Logic with Exponential Backoff

**Strategy**: Implement at the base HTTP client level to support both sync and async clients

#### 2a. Add Retry Configuration

**File**: `workos/_client_configuration.py` (or create new config class)

**Add configuration options**:
```python
@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 30.0  # seconds
    jitter: float = 0.25  # 25% jitter
```

**Update client initialization**:
- `workos/utils/_base_http_client.py` - Add `retry_config` parameter to `__init__`
- `workos/utils/http_client.py` - Pass through `retry_config` to base class

#### 2b. Implement Retry Logic

**File**: `workos/utils/_base_http_client.py`

**Add helper methods**:
```python
import time
import random
from typing import Tuple

def _is_retryable_error(self, response: httpx.Response) -> bool:
    """Determine if an error should be retried."""
    status_code = response.status_code
    
    # Retry on 5xx server errors
    if 500 <= status_code < 600:
        return True
    
    # Retry on 429 rate limit
    if status_code == 429:
        return True
    
    # Do NOT retry 4xx client errors (except 429)
    return False

def _get_retry_delay(self, attempt: int, response: httpx.Response) -> float:
    """Calculate delay with exponential backoff and jitter."""
    # Check for Retry-After header on 429 responses
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass  # Fall through to exponential backoff
    
    # Exponential backoff: base_delay * 2^attempt
    delay = self._retry_config.base_delay * (2 ** attempt)
    
    # Cap at max_delay
    delay = min(delay, self._retry_config.max_delay)
    
    # Add jitter: random variation of 0-25% of delay
    jitter_amount = delay * self._retry_config.jitter * random.random()
    return delay + jitter_amount

def _should_retry_exception(self, exc: Exception) -> bool:
    """Determine if an exception should trigger a retry."""
    # Retry on network errors (connection, timeout)
    if isinstance(exc, (httpx.ConnectError, httpx.TimeoutException)):
        return True
    return False
```

**Modify `_handle_response()` or create wrapper**:
- Wrap the actual request execution with retry logic
- Track attempt count
- Sleep between retries using calculated delay
- Re-raise non-retryable errors immediately

#### 2c. Update Both Sync and Async Clients

**File**: `workos/utils/http_client.py`

**SyncHTTPClient.request()** (lines 83-114):
- Wrap `self._client.request()` call with retry loop
- Catch both `httpx` exceptions and check response status codes
- Use `time.sleep()` for delays

**AsyncHTTPClient.request()** (lines 180-211):
- Same retry logic but use `asyncio.sleep()` for delays
- Await the request call properly

**Pseudocode structure**:
```python
def request(self, ...):
    last_exception = None
    
    for attempt in range(self._retry_config.max_retries + 1):
        try:
            response = self._client.request(...)
            
            # Check if we should retry based on status code
            if attempt < self._retry_config.max_retries and self._is_retryable_error(response):
                delay = self._get_retry_delay(attempt, response)
                time.sleep(delay)  # or asyncio.sleep for async
                continue
            
            # No retry needed or max retries reached
            return self._handle_response(response)
            
        except Exception as exc:
            last_exception = exc
            if attempt < self._retry_config.max_retries and self._should_retry_exception(exc):
                delay = self._retry_config.base_delay * (2 ** attempt)
                time.sleep(delay)
                continue
            raise
    
    # Should not reach here, but raise last exception if we do
    raise last_exception
```

### 3. Error Handling Updates

**File**: `workos/exceptions.py`

**Optional Enhancement** (not strictly required):
- Add a method/property to exception classes to indicate if retryable
- Could add a `RateLimitException` class that extends `BaseRequestException` for 429 errors
- Include retry attempt information in error messages

**Minimal approach**:
- No changes needed; use status code checking in base client

### 4. Testing

**File**: `tests/test_audit_logs.py`

**Add test cases**:

```python
class TestCreateEvent(_TestSetup):
    def test_auto_generates_idempotency_key(self, capture_and_mock_http_client_request):
        """Test that idempotency key is auto-generated when not provided."""
        organization_id = "org_123"
        event = {...}  # mock event
        
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"success": True}, 200
        )
        
        self.audit_logs.create_event(
            organization_id=organization_id,
            event=event,
            # No idempotency_key provided
        )
        
        # Assert header exists and is a valid UUID v4
        assert "idempotency-key" in request_kwargs["headers"]
        idempotency_key = request_kwargs["headers"]["idempotency-key"]
        assert len(idempotency_key) == 36  # UUID format: 8-4-4-4-12
        assert idempotency_key.count("-") == 4
    
    def test_respects_user_provided_idempotency_key(self, capture_and_mock_http_client_request):
        """Test that user-provided idempotency key is used instead of auto-generated."""
        organization_id = "org_123"
        event = {...}  # mock event
        custom_key = "my-custom-key"
        
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"success": True}, 200
        )
        
        self.audit_logs.create_event(
            organization_id=organization_id,
            event=event,
            idempotency_key=custom_key,
        )
        
        assert request_kwargs["headers"]["idempotency-key"] == custom_key
```

**Create new test file**: `tests/test_http_client_retry.py`

```python
class TestRetryLogic:
    def test_retries_on_500_error(self):
        """Test that 500 errors trigger retry."""
        # Mock client to return 500 twice, then 200
        # Assert request was made 3 times
        
    def test_retries_on_429_rate_limit(self):
        """Test that 429 errors trigger retry."""
        # Mock client to return 429 with Retry-After header
        # Assert retry delay respects Retry-After
        
    def test_no_retry_on_400_error(self):
        """Test that 4xx errors (except 429) don't retry."""
        # Mock client to return 400
        # Assert request was made only once
        
    def test_respects_max_retries(self):
        """Test that max retries limit is respected."""
        # Mock client to always return 500
        # Assert request count = max_retries + 1
        
    def test_exponential_backoff_delays(self):
        """Test that retry delays follow exponential backoff."""
        # Mock time.sleep and track delays
        # Assert delays are: 1s, 2s, 4s (with jitter)
        
    def test_retries_on_network_error(self):
        """Test that network errors trigger retry."""
        # Mock client to raise httpx.ConnectError
        # Assert retries occur
```

### 5. Configuration & Backward Compatibility

**No breaking changes**:
- Idempotency key auto-generation only activates when `idempotency_key=None`
- Retry logic applies globally but with sensible defaults (3 retries)
- Consider making retry config optional or use default values

**Optional**: Add retry configuration to main client
```python
# In workos/client.py or workos/__init__.py
workos_client = WorkOS(
    api_key="...",
    max_retries=3,  # Optional: configure retry behavior
    retry_base_delay=1.0,
)
```

## Implementation Order

1. ✅ **Phase 1**: Idempotency key auto-generation (Simple, isolated)
   - Modify `workos/audit_logs.py`
   - Add tests in `tests/test_audit_logs.py`

2. ✅ **Phase 2**: Retry logic infrastructure (Complex, affects all requests)
   - Add retry config to `_base_http_client.py`
   - Implement helper methods for retry decisions

3. ✅ **Phase 3**: Apply retry logic to sync client
   - Update `SyncHTTPClient.request()` in `http_client.py`
   - Add tests for sync retry behavior

4. ✅ **Phase 4**: Apply retry logic to async client
   - Update `AsyncHTTPClient.request()` in `http_client.py`
   - Add tests for async retry behavior

5. ✅ **Phase 5**: Integration testing & documentation
   - Test end-to-end with actual audit log creation
   - Update SDK documentation

## Files to Modify

| File | Purpose | Lines to Change |
|------|---------|-----------------|
| `workos/audit_logs.py` | Add UUID generation | ~75-90 (create_event method) |
| `workos/utils/_base_http_client.py` | Add retry logic base | Add ~50 lines (retry methods) |
| `workos/utils/http_client.py` | Implement retry in sync/async | ~83-114, ~180-211 (request methods) |
| `workos/exceptions.py` | (Optional) Add retryable classification | Minimal or none |
| `tests/test_audit_logs.py` | Test idempotency key auto-gen | Add 2 new test methods |
| `tests/test_http_client_retry.py` | Test retry logic | New file (~100-150 lines) |

## Dependencies

**No new dependencies required**:
- `uuid`: Python built-in (for idempotency keys)
- `time`: Python built-in (for delays)
- `random`: Python built-in (for jitter)
- `httpx`: Already in use (version >=0.28.1)

## Testing Checklist

- [ ] Auto-generated idempotency key is valid UUID v4
- [ ] User-provided idempotency key takes precedence
- [ ] Retries occur on 5xx errors
- [ ] Retries occur on 429 rate limit
- [ ] Retry-After header is respected for 429
- [ ] No retries on 4xx errors (except 429)
- [ ] Max retry limit is enforced
- [ ] Exponential backoff with jitter works correctly
- [ ] Network errors (connection, timeout) trigger retries
- [ ] Both sync and async clients have retry logic
- [ ] Backward compatibility maintained

## Retry Behavior Specification

### Retry Conditions
**DO Retry**:
- HTTP 5xx (500-599) status codes
- HTTP 429 (Too Many Requests)
- Network errors: `httpx.ConnectError`, `httpx.TimeoutException`

**DO NOT Retry**:
- HTTP 4xx (except 429): 400, 401, 403, 404, 409, etc.
- Authentication/authorization errors
- Validation errors

### Retry Strategy
- **Algorithm**: Exponential backoff with jitter
- **Base delay**: 1 second
- **Max delay**: 30 seconds
- **Jitter**: 0-25% random variation
- **Max retries**: 3 attempts (configurable)
- **Retry-After**: Honor header value for 429 responses

### Delay Calculation
```
Attempt 0 (initial): No delay
Attempt 1: 1s + jitter (0-0.25s) = 1-1.25s
Attempt 2: 2s + jitter (0-0.5s) = 2-2.5s
Attempt 3: 4s + jitter (0-1s) = 4-5s
```

## Notes for Implementation

1. **Thread Safety**: The retry logic uses `time.sleep()` (sync) and `asyncio.sleep()` (async), both safe for their contexts
2. **Logging**: Consider adding debug logs for retry attempts (not required for MVP)
3. **Metrics**: Could track retry counts for monitoring (future enhancement)
4. **Rate Limiting**: The jitter helps prevent thundering herd when multiple clients retry simultaneously
5. **Idempotency**: The auto-generated key ensures that retried requests don't create duplicate events

## Verification

After implementation, verify:
1. Run existing test suite - all pass (backward compatibility)
2. New tests pass for idempotency and retry logic
3. Manual test with actual API:
   - Create audit log event without providing idempotency key
   - Verify idempotency key is sent in request headers
   - Simulate network failure and observe retries
   - Verify 429 rate limit triggers retry with proper delay

## References

- Audit logs API endpoint: `POST /audit_logs/events`
- Idempotency header: `Idempotency-Key` (lowercase: `idempotency-key`)
- UUID v4 format: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`
- httpx documentation: https://www.python-httpx.org/

