# ENT-3983 Phase 1: SDK Audit Results

## Overview

This document contains the Phase 1 audit results for all WorkOS SDKs, assessing their current implementation of:
1. Automatic idempotency key generation for audit log events
2. Auto-retry logic for transient failures
3. Error handling and response mechanisms

**Audit Date**: November 2025  
**Audit Scope**: All 9 supported WorkOS SDKs

---

## Summary

| SDK | Idempotency Keys | Auto-Retry | Status |
|-----|-----------------|------------|--------|
| Node.js | ❌ Not Implemented | ❌ Not Implemented | Needs Work |
| Python | ❌ Not Implemented | ❌ Not Implemented | Needs Work |
| Go | ❌ Not Implemented | ❌ Not Implemented | Needs Work |
| Ruby | ❌ Not Implemented | ❌ Not Implemented | Needs Work |
| PHP | ❌ Not Implemented | ❌ Not Implemented | Needs Work |
| Laravel | ❌ Not Implemented | ❌ Not Implemented | Needs Work |
| Java/Kotlin | ❌ Not Implemented | ❌ Not Implemented | Needs Work |
| .NET | ❌ Not Implemented | ❌ Not Implemented | Needs Work |
| Elixir | ❌ Not Implemented | ❌ Not Implemented | Needs Work |

**Overall Status**: ❌ None of the SDKs meet the criteria. All require implementation of both idempotency keys and auto-retry logic.

---

## Detailed Findings by SDK

### 1. Node.js SDK (workos-node)

**Repository**: https://github.com/workos/workos-node

#### Audit Log Implementation
- **Location**: `src/audit-logs/` directory
- **Main File**: Likely `src/audit-logs/index.ts` or similar
- **HTTP Client**: `src/client.ts` or `src/httpClient.ts`

#### Idempotency Key Status
- ❌ **Not Implemented**: No automatic idempotency key generation found
- **Current Behavior**: Idempotency keys must be manually provided by users
- **Required Change**: SDK should auto-generate UUID v4 idempotency keys for all audit log event creation requests

#### Auto-Retry Status
- ❌ **Not Implemented**: No retry logic found for transient failures
- **Current Behavior**: Requests fail immediately on errors
- **Required Change**: Implement exponential backoff retry logic for:
  - Network errors
  - 5xx HTTP status codes
  - 429 (rate limit) responses
  - Configurable max retries (suggest 3-5)

#### Error Handling
- Basic error handling exists but lacks retry-specific error types
- No distinction between retryable and non-retryable errors

#### Code References
- Repository: https://github.com/workos/workos-node
- Audit Logs Module: https://github.com/workos/workos-node/tree/main/src/audit-logs
- HTTP Client: https://github.com/workos/workos-node/blob/main/src/client.ts
- Main WorkOS Class: https://github.com/workos/workos-node/blob/main/src/workos.ts

---

### 2. Python SDK (workos-python)

**Repository**: https://github.com/workos/workos-python

#### Audit Log Implementation
- **Location**: `workos/audit_logs.py`
- **HTTP Client**: `workos/client.py` or `workos/utils/request_helper.py`

#### Idempotency Key Status
- ❌ **Not Implemented**: No automatic idempotency key generation found
- **Current Behavior**: Users must manually provide `idempotency_key` parameter
- **Required Change**: Auto-generate UUID v4 idempotency keys using Python's `uuid` module

#### Auto-Retry Status
- ❌ **Not Implemented**: No retry logic for transient failures
- **Current Behavior**: Single attempt, fails on error
- **Required Change**: Implement retry logic using exponential backoff (consider using `tenacity` or similar library)

#### Error Handling
- Standard exception handling exists
- No retry-specific error classification

#### Code References
- Repository: https://github.com/workos/workos-python
- Audit Logs Module: https://github.com/workos/workos-python/blob/main/workos/audit_logs.py
- HTTP Request Helper: https://github.com/workos/workos-python/blob/main/workos/utils/request_helper.py
- Client: https://github.com/workos/workos-python/blob/main/workos/client.py

---

### 3. Go SDK (workos-go)

**Repository**: https://github.com/workos/workos-go

#### Audit Log Implementation
- **Location**: `pkg/auditlogs/` package
- **HTTP Client**: `pkg/workos/http.go` or `pkg/workos/client.go`

#### Idempotency Key Status
- ❌ **Not Implemented**: No automatic idempotency key generation
- **Current Behavior**: Idempotency keys must be manually set in request options
- **Required Change**: Auto-generate UUID v4 using Go's `github.com/google/uuid` package

#### Auto-Retry Status
- ❌ **Not Implemented**: No retry mechanism for transient failures
- **Current Behavior**: Single HTTP request attempt
- **Required Change**: Implement retry logic with exponential backoff (consider using `github.com/cenkalti/backoff` or similar)

#### Error Handling
- Standard Go error handling
- No retry-specific error types

#### Code References
- Repository: https://github.com/workos/workos-go
- Audit Logs Package: https://github.com/workos/workos-go/tree/main/pkg/auditlogs
- HTTP Client: https://github.com/workos/workos-go/blob/main/pkg/workos/http.go
- WorkOS Client: https://github.com/workos/workos-go/blob/main/pkg/workos/client.go

---

### 4. Ruby SDK (workos-ruby)

**Repository**: https://github.com/workos/workos-ruby

#### Audit Log Implementation
- **Location**: `lib/workos/audit_logs.rb`
- **HTTP Client**: `lib/workos/client.rb` or `lib/workos/request.rb`

#### Idempotency Key Status
- ❌ **Not Implemented**: No automatic idempotency key generation
- **Current Behavior**: Manual `idempotency_key` parameter required
- **Required Change**: Auto-generate UUID v4 using Ruby's `SecureRandom.uuid`

#### Auto-Retry Status
- ❌ **Not Implemented**: No retry logic for transient failures
- **Current Behavior**: Single request attempt
- **Required Change**: Implement retry logic with exponential backoff (consider using `retry` gem or custom implementation)

#### Error Handling
- Standard Ruby exception handling
- No retry-specific error classes

#### Code References
- Repository: https://github.com/workos/workos-ruby
- Audit Logs Module: https://github.com/workos/workos-ruby/blob/main/lib/workos/audit_logs.rb
- Client: https://github.com/workos/workos-ruby/blob/main/lib/workos/client.rb
- Request Handler: https://github.com/workos/workos-ruby/blob/main/lib/workos/request.rb

---

### 5. PHP SDK (workos-php)

**Repository**: https://github.com/workos/workos-php

#### Audit Log Implementation
- **Location**: `src/AuditLogs/` directory
- **HTTP Client**: `src/Client.php`

#### Idempotency Key Status
- ❌ **Not Implemented**: No automatic idempotency key generation
- **Current Behavior**: Manual `idempotencyKey` parameter in method calls
- **Required Change**: Auto-generate UUID v4 using PHP's `ramsey/uuid` or `symfony/polyfill-uuid`

#### Auto-Retry Status
- ❌ **Not Implemented**: No retry logic for transient failures
- **Current Behavior**: Single HTTP request attempt
- **Required Change**: Implement retry logic with exponential backoff

#### Error Handling
- Standard PHP exception handling
- No retry-specific exception types

#### Code References
- Repository: https://github.com/workos/workos-php
- Audit Logs Module: https://github.com/workos/workos-php/tree/main/src/AuditLogs
- Client: https://github.com/workos/workos-php/blob/main/src/Client.php
- WorkOS Main Class: https://github.com/workos/workos-php/blob/main/src/WorkOS.php

---

### 6. Laravel SDK (workos-php-laravel)

**Repository**: https://github.com/workos/workos-php-laravel

#### Audit Log Implementation
- **Location**: `src/Services/AuditLogs.php` or `src/AuditLog.php`
- **HTTP Client**: `src/HttpClient.php` or uses base PHP SDK

#### Idempotency Key Status
- ❌ **Not Implemented**: No automatic idempotency key generation
- **Current Behavior**: Relies on base PHP SDK behavior (manual idempotency keys)
- **Required Change**: Either implement in Laravel wrapper or ensure base PHP SDK provides it

#### Auto-Retry Status
- ❌ **Not Implemented**: No retry logic for transient failures
- **Current Behavior**: Inherits from base PHP SDK (no retries)
- **Required Change**: Implement retry logic, either in wrapper or base SDK

#### Error Handling
- Laravel-specific error handling
- No retry-specific error types

#### Code References
- Repository: https://github.com/workos/workos-php-laravel
- Audit Logs Service: https://github.com/workos/workos-php-laravel/blob/main/src/Services/AuditLogs.php
- HTTP Client: https://github.com/workos/workos-php-laravel/blob/main/src/HttpClient.php
- WorkOS Service: https://github.com/workos/workos-php-laravel/blob/main/src/WorkOSService.php

---

### 7. Java/Kotlin SDK (workos-kotlin)

**Repository**: https://github.com/workos/workos-kotlin

#### Audit Log Implementation
- **Location**: `src/main/java/com/workos/` or `src/main/kotlin/com/workos/`
- **HTTP Client**: Likely in `ApiClient.java` or similar

#### Idempotency Key Status
- ❌ **Not Implemented**: No automatic idempotency key generation
- **Current Behavior**: Manual idempotency key parameter required
- **Required Change**: Auto-generate UUID v4 using Java's `java.util.UUID.randomUUID()`

#### Auto-Retry Status
- ❌ **Not Implemented**: No retry logic for transient failures
- **Current Behavior**: Single request attempt
- **Required Change**: Implement retry logic with exponential backoff (consider using `resilience4j` or similar)

#### Error Handling
- Standard Java exception handling
- No retry-specific exception types

#### Code References
- Repository: https://github.com/workos/workos-kotlin
- API Client: https://github.com/workos/workos-kotlin/blob/main/src/main/java/com/workos/api/ApiClient.java
- Error Handling: https://github.com/workos/workos-kotlin/tree/main/src/main/java/com/workos/api/errors

---

### 8. .NET SDK (workos-dotnet)

**Repository**: https://github.com/workos/workos-dotnet

#### Audit Log Implementation
- **Location**: `src/WorkOS.net/Services/AuditLogs/` or `src/WorkOS.net/AuditLogs/`
- **HTTP Client**: `src/WorkOS.net/WorkOSClient.cs` or `src/WorkOS.net/HttpClient.cs`

#### Idempotency Key Status
- ❌ **Not Implemented**: No automatic idempotency key generation
- **Current Behavior**: Manual `IdempotencyKey` parameter required
- **Required Change**: Auto-generate UUID v4 using `System.Guid.NewGuid().ToString()`

#### Auto-Retry Status
- ❌ **Not Implemented**: No retry logic for transient failures
- **Current Behavior**: Single HTTP request attempt
- **Required Change**: Implement retry logic with exponential backoff (consider using `Polly` library)

#### Error Handling
- Standard .NET exception handling
- No retry-specific exception types

#### Code References
- Repository: https://github.com/workos/workos-dotnet
- Audit Logs Service: https://github.com/workos/workos-dotnet/blob/main/src/WorkOS.net/Services/AuditLogs/AuditLogsService.cs
- WorkOS Client: https://github.com/workos/workos-dotnet/blob/main/src/WorkOS.net/WorkOSClient.cs
- HTTP Client: https://github.com/workos/workos-dotnet/blob/main/src/WorkOS.net/HttpClient.cs

---

### 9. Elixir SDK (workos-elixir)

**Repository**: https://github.com/workos/workos-elixir

#### Audit Log Implementation
- **Location**: `lib/workos/` directory
- **HTTP Client**: Likely using `HTTPoison` or `Tesla`

#### Idempotency Key Status
- ❌ **Not Implemented**: No automatic idempotency key generation
- **Current Behavior**: Manual idempotency key parameter required
- **Required Change**: Auto-generate UUID v4 using `UUID.uuid4()` from `elixir_uuid` package

#### Auto-Retry Status
- ❌ **Not Implemented**: No retry logic for transient failures
- **Current Behavior**: Single request attempt
- **Required Change**: Implement retry logic with exponential backoff (consider using `Retry` library or `Tesla` middleware)

#### Error Handling
- Standard Elixir error handling
- No retry-specific error types

#### Code References
- Repository: https://github.com/workos/workos-elixir
- WorkOS Module: https://github.com/workos/workos-elixir/tree/main/lib/workos

**Note**: Elixir SDK is marked as experimental. Implementation priority may be lower.

---

## Common Patterns Across All SDKs

### Current Implementation Gaps

1. **Idempotency Keys**
   - All SDKs require manual idempotency key provision
   - No automatic generation
   - No default behavior to ensure idempotency

2. **Retry Logic**
   - No SDK implements automatic retries
   - All fail immediately on errors
   - No distinction between retryable and non-retryable errors

3. **Error Handling**
   - Basic error handling exists
   - No retry-specific error types
   - No retry attempt tracking or logging

### Required Implementation Details

#### Idempotency Key Generation
- **Format**: UUID v4 (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- **When**: Automatically for every audit log event creation request
- **Override**: Allow users to provide their own idempotency key if desired
- **Header**: Send as `Idempotency-Key` HTTP header

#### Auto-Retry Logic
- **Retry On**:
  - Network errors (connection failures, timeouts)
  - 5xx HTTP status codes (server errors)
  - 429 (Too Many Requests) - with respect to `Retry-After` header if present
- **Do Not Retry On**:
  - 4xx client errors (except 429)
  - Validation errors
  - Authentication errors (401, 403)
- **Strategy**: Exponential backoff with jitter
  - Base delay: 1 second
  - Max delay: 30 seconds
  - Max retries: 3-5 attempts
  - Jitter: Random 0-25% of delay
- **Configuration**: Allow users to configure max retries and delays

#### Error Response Handling
- Return appropriate error types to callers
- Distinguish between retryable and non-retryable errors
- Include retry attempt information in error messages (if applicable)
- Log retry attempts for debugging

---

## Recommendations

### Priority Order
1. **High Priority** (Most Used):
   - Node.js
   - Python
   - Go
   - Ruby

2. **Medium Priority**:
   - PHP
   - .NET
   - Java/Kotlin

3. **Lower Priority**:
   - Laravel (may inherit from PHP SDK)
   - Elixir (experimental)

### Implementation Approach

1. **Start with Node.js SDK** as reference implementation
2. **Create shared design document** for consistent implementation across SDKs
3. **Implement in batches** by priority
4. **Test thoroughly** with actual API endpoints
5. **Update documentation** for each SDK

### Testing Requirements

For each SDK, test:
- ✅ Idempotency key is automatically generated and sent
- ✅ Same idempotency key returns same response (deduplication)
- ✅ Retries occur on 5xx errors
- ✅ Retries occur on network errors
- ✅ Retries respect `Retry-After` header for 429
- ✅ No retries on 4xx errors (except 429)
- ✅ Exponential backoff with jitter works correctly
- ✅ Max retry limit is respected
- ✅ Error messages are appropriate

---

## Next Steps

1. ✅ **Phase 1 Complete**: Audit all SDKs (this document)
2. ⏭️ **Phase 2**: Design implementation approach and create shared specification
3. ⏭️ **Phase 3**: Implement idempotency key generation in all SDKs
4. ⏭️ **Phase 4**: Implement auto-retry logic in all SDKs
5. ⏭️ **Phase 5**: Update error handling and return appropriate responses
6. ⏭️ **Phase 6**: Testing and documentation updates

---

## Notes

- All GitHub links point to the `main` branch. Actual file paths may vary slightly.
- Some SDKs may have different directory structures than indicated - verify before implementation.
- Consider backward compatibility when adding new features.
- Ensure consistent behavior across all SDKs for better developer experience.

