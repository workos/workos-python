# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup

```bash
uv sync --locked --dev # Install package in development mode with dev dependencies
```

### Code Quality

```bash
uv run ruff format .          # Format code
uv run ruff format --check .  # Check formatting without making changes
uv run ruff check .           # Lint code
uv run mypy                   # Type checking
```

### Testing

The SDK uses [nox](https://nox.thea.codes/) with [nox-uv](https://github.com/dantebben/nox-uv) for multi-version Python testing. This ensures compatibility across all supported Python versions (3.8-3.14).

**Quick testing with the test script:**

```bash
./scripts/test.sh              # Run tests on all Python versions
./scripts/test.sh 3.12         # Run tests on Python 3.12 only
./scripts/test.sh 3.11 3.12    # Run tests on Python 3.11 and 3.12
./scripts/test.sh --coverage   # Run tests with coverage on all versions
./scripts/test.sh --ci         # Run full CI checks (lint, type, tests)
./scripts/test.sh --fresh      # Recreate virtual environments
./scripts/test.sh 3.12 -- -k "test_sso" -v  # Pass pytest arguments
```

**Direct nox commands:**

```bash
uv run nox                       # Run tests on all Python versions
uv run nox -s tests-3.12         # Run tests on specific Python version
uv run nox -s coverage           # Run tests with coverage
uv run nox -s lint               # Run linting
uv run nox -s typecheck          # Run type checking
uv run nox -s ci                 # Run all CI checks
uv run nox -l                    # List all available sessions
```

**Single-version testing (faster for development):**

```bash
uv run pytest                    # Run all tests on current Python
uv run pytest tests/test_sso.py  # Run specific test file
uv run pytest -k "test_name"     # Run tests matching pattern
uv run pytest --cov=workos       # Run tests with coverage
```

### Build and Distribution

```bash
uv build --sdist --wheel               # Build distribution packages
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

