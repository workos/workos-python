# PR Feedback - Audit Logs Create Event Response

## Context

You received feedback on your PR regarding the `audit_logs.py` file (lines 92-101) with two main points:

1. **"Can we return this response object back to the user?"**
2. **"I think we should also add some test cases when the schema validation fails."**

## Current State Analysis

### Current Implementation
- The `create_event` method currently returns `None` (line 83 and Protocol definition line 23)
- The `_http_client.request()` call (lines 94-100) **does** return a `ResponseJson` but it's being discarded
- Test assertions confirm that `create_event` returns `None` (test_audit_logs.py lines 87, 107, 133)

### Comparison with Other Endpoints
Looking at similar endpoints in the codebase:

**Endpoints that RETURN data:**
- `create_export()` (lines 102-127): Returns `AuditLogExport` with `model_validate(response)`
- `get_export()` (lines 129-135): Returns `AuditLogExport` with `model_validate(response)`
- `create_user()` in `user_management.py`: Returns `User` with `model_validate(response)`
- `create_organization()` in `organizations.py`: Returns `Organization` with `model_validate(response)`

**Pattern identified:**
- POST/PUT endpoints that create/update resources capture the response and validate it against a Pydantic model
- DELETE endpoints return `None`
- `create_event` should follow the POST pattern and return the response

### Current Response Structure
Based on test mocks (line 71, 97, 116 in test_audit_logs.py):
```json
{"success": true}
```

This is a simple success indicator, unlike other endpoints that return full resource objects.

## What Needs to Change

### 1. Create a Response Type for Audit Log Event Creation

**File:** `workos/types/audit_logs/audit_log_event_response.py` (NEW FILE)

Create a Pydantic model to represent the response:

```python
from workos.types.workos_model import WorkOSModel


class AuditLogEventResponse(WorkOSModel):
    """Response from creating an audit log event."""
    
    success: bool
```

**Rationale:** 
- Follows the pattern used by other endpoints (`AuditLogExport`, `User`, `Organization`)
- Provides type safety and validation
- Matches the mock response structure `{"success": True}`

### 2. Update Type Exports

**File:** `workos/types/audit_logs/__init__.py`

Add the new response type to exports:

```python
from workos.types.audit_logs.audit_log_event_response import AuditLogEventResponse

__all__ = [
    # ... existing exports ...
    "AuditLogEventResponse",
]
```

### 3. Update the Protocol Definition

**File:** `workos/audit_logs.py` (Lines 17-33)

Change the return type from `None` to `AuditLogEventResponse`:

```python
def create_event(
    self,
    *,
    organization_id: str,
    event: AuditLogEvent,
    idempotency_key: Optional[str] = None,
) -> AuditLogEventResponse:  # Changed from None
    """Create an Audit Logs event.

    Kwargs:
        organization_id (str): Organization's unique identifier.
        event (AuditLogEvent): An AuditLogEvent object.
        idempotency_key (str): Idempotency key. (Optional)
    Returns:
        AuditLogEventResponse: Response indicating success
    """
    ...
```

### 4. Update the Implementation

**File:** `workos/audit_logs.py` (Lines 77-100)

Capture and return the response with validation:

```python
def create_event(
    self,
    *,
    organization_id: str,
    event: AuditLogEvent,
    idempotency_key: Optional[str] = None,
) -> AuditLogEventResponse:  # Changed from None
    json = {"organization_id": organization_id, "event": event}

    headers = {}
    # Auto-generate UUID v4 if not provided
    if idempotency_key is None:
        idempotency_key = f"workos-python-{uuid.uuid4()}"

    headers["idempotency-key"] = idempotency_key

    # Enable retries for audit log event creation with default retryConfig
    response = self._http_client.request(  # Capture the response
        EVENTS_PATH,
        method=REQUEST_METHOD_POST,
        json=json,
        headers=headers,
        retry_config=RetryConfig(),
    )

    return AuditLogEventResponse.model_validate(response)  # Validate and return
```

**Changes:**
- Line 94: Capture the response in a variable
- Line 101: Add validation and return statement

### 5. Update Import Statements

**File:** `workos/audit_logs.py` (Top of file)

Add import for the new response type:

```python
from workos.types.audit_logs import AuditLogExport
from workos.types.audit_logs.audit_log_event import AuditLogEvent
from workos.types.audit_logs.audit_log_event_response import AuditLogEventResponse  # NEW
```

### 6. Update Existing Tests

**File:** `tests/test_audit_logs.py`

Update all three existing test methods to check for the response object:

**Test 1: `test_succeeds` (lines 43-87)**
```python
# Change line 87 from:
assert response is None

# To:
assert response is not None
assert response.success is True
assert isinstance(response, AuditLogEventResponse)
```

**Test 2: `test_sends_idempotency_key` (lines 89-107)**
```python
# Change line 107 from:
assert response is None

# To:
assert response is not None
assert response.success is True
```

**Test 3: `test_auto_generates_idempotency_key` (lines 109-133)**
```python
# Change line 133 from:
assert response is None

# To:
assert response is not None
assert response.success is True
```

### 7. Add New Test Cases for Schema Validation Failures

**File:** `tests/test_audit_logs.py`

Add new test methods to the `TestCreateEvent` class:

```python
def test_handles_missing_success_field(
    self, mock_audit_log_event, mock_http_client_with_response
):
    """Test that schema validation fails when response is missing required fields."""
    organization_id = "org_123456789"
    
    # Mock response missing the 'success' field
    mock_http_client_with_response(
        self.http_client,
        {},  # Empty response
        200,
    )
    
    with pytest.raises(Exception) as excinfo:  # Pydantic will raise ValidationError
        self.audit_logs.create_event(
            organization_id=organization_id,
            event=mock_audit_log_event,
        )
    
    # Assert that validation error occurred
    assert "success" in str(excinfo.value).lower() or "validation" in str(excinfo.value).lower()

def test_handles_invalid_success_type(
    self, mock_audit_log_event, mock_http_client_with_response
):
    """Test that schema validation fails when response has incorrect field types."""
    organization_id = "org_123456789"
    
    # Mock response with wrong type for 'success' field
    mock_http_client_with_response(
        self.http_client,
        {"success": "yes"},  # String instead of boolean
        200,
    )
    
    with pytest.raises(Exception) as excinfo:  # Pydantic will raise ValidationError
        self.audit_logs.create_event(
            organization_id=organization_id,
            event=mock_audit_log_event,
        )
    
    # Assert that validation error occurred
    assert "success" in str(excinfo.value).lower() or "bool" in str(excinfo.value).lower()

def test_handles_malformed_json_response(
    self, mock_audit_log_event, mock_http_client_with_response
):
    """Test that schema validation fails when response is completely malformed."""
    organization_id = "org_123456789"
    
    # Mock response with unexpected structure
    mock_http_client_with_response(
        self.http_client,
        {"unexpected": "data", "structure": 123},
        200,
    )
    
    with pytest.raises(Exception) as excinfo:
        self.audit_logs.create_event(
            organization_id=organization_id,
            event=mock_audit_log_event,
        )
    
    # Assert that validation error occurred
    assert excinfo.value is not None
```

## Step-by-Step Implementation Plan

1. **Create the response model** (15 min)
   - Create `workos/types/audit_logs/audit_log_event_response.py`
   - Add the `AuditLogEventResponse` Pydantic model
   - Update `workos/types/audit_logs/__init__.py` to export it

2. **Update the audit_logs module** (10 min)
   - Add import for `AuditLogEventResponse` in `workos/audit_logs.py`
   - Update Protocol definition return type (line 23)
   - Update docstring (line 30-31)
   - Update implementation return type (line 83)
   - Capture response in variable (line 94)
   - Add validation and return statement (line 101)

3. **Update existing tests** (10 min)
   - Modify three test methods in `tests/test_audit_logs.py`
   - Change assertions from `assert response is None` to check for response object
   - Import `AuditLogEventResponse` in test file

4. **Add schema validation failure tests** (20 min)
   - Add three new test methods to `TestCreateEvent` class
   - Test missing required field
   - Test incorrect field type
   - Test malformed response

5. **Run tests and verify** (10 min)
   - Run `pytest tests/test_audit_logs.py -v`
   - Ensure all tests pass
   - Fix any issues

6. **Run linter** (5 min)
   - Run `mypy` and `flake8` on modified files
   - Fix any type or style issues

## Files to Modify

### New Files
- `workos/types/audit_logs/audit_log_event_response.py`

### Modified Files
- `workos/types/audit_logs/__init__.py`
- `workos/audit_logs.py`
- `tests/test_audit_logs.py`

## Breaking Changes

**Yes, this is a breaking change** because:
- The return type changes from `None` to `AuditLogEventResponse`
- Users who may have code like `result = create_event(...)` will now get an object instead of `None`
- However, since most users likely don't assign the result (they ignore it), impact should be minimal

**Migration for users:**
```python
# Before:
workos.audit_logs.create_event(organization_id=org_id, event=event)
# Returns None, no value to check

# After:
response = workos.audit_logs.create_event(organization_id=org_id, event=event)
# Returns AuditLogEventResponse, can check response.success
```

## Testing Strategy

1. **Unit tests** for the new response model
2. **Integration tests** for successful response handling
3. **Error tests** for schema validation failures (the new tests requested)
4. **Existing tests** updated to check for response object

## Alternative Approaches Considered

### Alternative 1: Return raw dict without validation
**Pros:**
- Simpler implementation
- No need to create a new model
- Backwards compatible if we make return type `Optional[dict]`

**Cons:**
- No type safety
- Inconsistent with other endpoints
- Can't add schema validation failure tests

**Decision:** Not recommended - inconsistent with codebase patterns

### Alternative 2: Make return type `Optional[AuditLogEventResponse]`
**Pros:**
- More backwards compatible
- Can return `None` for older code paths

**Cons:**
- Adds complexity
- Not needed - the API always returns a response
- Still a breaking change for type checkers

**Decision:** Not recommended - unnecessary complexity

## Recommended Approach

Follow the pattern established by other endpoints in the codebase:
1. Create a Pydantic model for the response
2. Validate the response using `model_validate()`
3. Return the validated model
4. Update tests to verify the response
5. Add schema validation failure tests

This approach is **consistent**, **type-safe**, and **maintainable**.

## Estimated Time
- Total implementation time: ~70 minutes
- Testing and verification: Included in each step
- Documentation: N/A (docstrings updated inline)

## Risk Assessment

**Low Risk** because:
- Following established patterns in the codebase
- Changes are isolated to audit_logs module
- Comprehensive test coverage
- No database or external dependencies

**Mitigation:**
- Thorough testing before merge
- Update SDK changelog to note breaking change
- Consider semantic versioning (minor version bump if breaking)

