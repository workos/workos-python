# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup
```bash
pip install -e .[dev]  # Install package in development mode with dev dependencies
```

### Code Quality
```bash
black .                 # Format code
black --check .         # Check formatting without making changes
flake8 .               # Lint code
mypy                   # Type checking
```

### Testing
```bash
python -m pytest                    # Run all tests
python -m pytest tests/test_sso.py  # Run specific test file
python -m pytest -k "test_name"     # Run tests matching pattern
python -m pytest --cov=workos       # Run tests with coverage
```

### Build and Distribution
```bash
python setup.py sdist bdist_wheel   # Build distribution packages
bash scripts/build_and_upload_dist.sh  # Build and upload to PyPI
```

## Architecture Overview

### Client Architecture
The SDK provides both synchronous and asynchronous clients:
- `WorkOSClient` (sync) and `AsyncWorkOSClient` (async) are the main entry points
- Both inherit from `BaseClient` which handles configuration and module initialization
- Each feature area (SSO, Directory Sync, etc.) has dedicated module classes
- HTTP clients (`SyncHTTPClient`/`AsyncHTTPClient`) handle the actual API communication

### Module Structure
Each WorkOS feature has its own module following this pattern:
- **Module class** (e.g., `SSO`) - main API interface
- **Types directory** (e.g., `workos/types/sso/`) - Pydantic models for API objects
- **Tests** (e.g., `tests/test_sso.py`) - comprehensive test coverage

### Type System
- All models inherit from `WorkOSModel` (extends Pydantic `BaseModel`)
- Strict typing with mypy enforcement (`strict = True` in mypy.ini)
- Support for both sync and async operations via `SyncOrAsync` typing

### Testing Framework
- Uses pytest with custom fixtures for mocking HTTP clients
- `@pytest.mark.sync_and_async()` decorator runs tests for both sync/async variants
- Comprehensive fixtures in `conftest.py` for HTTP mocking and pagination testing
- Test utilities in `tests/utils/` for common patterns

### HTTP Client Abstraction
- Base HTTP client (`_BaseHTTPClient`) with sync/async implementations
- Request helper utilities for consistent API interaction patterns
- Built-in pagination support with `WorkOSListResource` type
- Automatic retry and error handling

### Key Patterns
- **Dual client support**: Every module supports both sync and async operations
- **Type safety**: Extensive use of Pydantic models and strict mypy checking
- **Pagination**: Consistent cursor-based pagination across list endpoints
- **Error handling**: Custom exception classes in `workos/exceptions.py`
- **Configuration**: Environment variable support (`WORKOS_API_KEY`, `WORKOS_CLIENT_ID`)

When adding new features:
1. Create module class with both sync/async HTTP client support
2. Add Pydantic models in appropriate `types/` subdirectory
3. Implement comprehensive tests using the sync_and_async marker
4. Follow existing patterns for pagination, error handling, and type annotations