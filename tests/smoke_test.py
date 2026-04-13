#!/usr/bin/env python3
"""Smoke tests to verify the built package works correctly.

These tests run against the installed package (wheel or sdist) to verify:
- All imports work correctly
- Dependencies are properly bundled
- Type markers are present
- Both sync and async clients can be instantiated
- All module properties are accessible

Run with: uv run --isolated --no-project --with dist/*.whl tests/smoke_test.py
"""

# ruff: noqa: F401 - imports are intentionally unused; this file tests import functionality

import sys
from pathlib import Path


# Service accessors exposed on both WorkOSClient and AsyncWorkOSClient.
CLIENT_MODULES = [
    "actions",
    "admin_portal",
    "api_keys",
    "audit_logs",
    "authorization",
    "connect",
    "directory_sync",
    "events",
    "feature_flags",
    "mfa",
    "multi_factor_auth",
    "organization_domains",
    "organizations",
    "passwordless",
    "pipes",
    "pkce",
    "radar",
    "sso",
    "user_management",
    "vault",
    "webhooks",
    "widgets",
]


def test_basic_import() -> None:
    """Verify the package can be imported."""
    import workos

    assert workos is not None
    print("✓ Basic import works")


def test_version_accessible() -> None:
    """Verify version metadata is accessible."""
    from importlib.metadata import version

    pkg_version = version("workos")
    assert pkg_version is not None
    assert len(pkg_version) > 0
    print(f"✓ Version accessible: {pkg_version}")


def test_py_typed_marker() -> None:
    """Verify py.typed marker is included for type checking support."""
    import workos

    package_path = Path(workos.__file__).parent
    py_typed = package_path / "py.typed"
    assert py_typed.exists(), f"py.typed marker not found at {py_typed}"
    print(f"✓ py.typed marker present at {py_typed}")


def test_sync_client_import_and_instantiate() -> None:
    """Verify sync client can be imported and instantiated."""
    from workos import WorkOSClient

    client = WorkOSClient(api_key="sk_test_smoke", client_id="client_smoke")
    assert client is not None
    print("✓ WorkOSClient imports and instantiates")


def test_async_client_import_and_instantiate() -> None:
    """Verify async client can be imported and instantiated."""
    from workos import AsyncWorkOSClient

    client = AsyncWorkOSClient(api_key="sk_test_smoke", client_id="client_smoke")
    assert client is not None
    print("✓ AsyncWorkOSClient imports and instantiates")


def test_sync_client_modules_accessible() -> None:
    """Verify all service accessors are reachable on the sync client."""
    from workos import WorkOSClient

    client = WorkOSClient(api_key="sk_test_smoke", client_id="client_smoke")

    for module_name in CLIENT_MODULES:
        module = getattr(client, module_name, None)
        assert module is not None, f"Module {module_name} not accessible"
        print(f"  ✓ client.{module_name}")

    print(f"✓ All {len(CLIENT_MODULES)} sync client modules accessible")


def test_async_client_modules_accessible() -> None:
    """Verify all service accessors are reachable on the async client."""
    from workos import AsyncWorkOSClient

    client = AsyncWorkOSClient(api_key="sk_test_smoke", client_id="client_smoke")

    for module_name in CLIENT_MODULES:
        module = getattr(client, module_name, None)
        assert module is not None, f"Module {module_name} not accessible"
        print(f"  ✓ async_client.{module_name}")

    print(f"✓ All {len(CLIENT_MODULES)} async client modules accessible")


def test_core_types_importable() -> None:
    """Verify a representative sample of feature models can be imported."""
    from workos.sso.models import Connection, ConnectionDomain, Profile

    assert Connection is not None
    assert ConnectionDomain is not None
    assert Profile is not None

    from workos.organizations.models import Organization

    assert Organization is not None

    from workos.directory_sync.models import (
        Directory,
        DirectoryGroup,
        DirectoryUserWithGroups,
    )

    assert Directory is not None
    assert DirectoryGroup is not None
    assert DirectoryUserWithGroups is not None

    from workos.user_management.models import (
        AuthenticateResponse,
        Invitation,
        OrganizationMembership,
        User,
    )

    assert AuthenticateResponse is not None
    assert Invitation is not None
    assert OrganizationMembership is not None
    assert User is not None

    from workos.events.models import EventSchema

    assert EventSchema is not None

    from workos.feature_flags.models import FeatureFlag

    assert FeatureFlag is not None

    print("✓ Core types importable")


def test_errors_importable() -> None:
    """Verify error classes can be imported from the top-level package."""
    from workos import (
        AuthenticationError,
        AuthorizationError,
        BadRequestError,
        ConflictError,
        NotFoundError,
        RateLimitExceededError,
        ServerError,
        UnprocessableEntityError,
        WorkOSError,
    )

    assert issubclass(AuthenticationError, WorkOSError)
    assert issubclass(AuthorizationError, WorkOSError)
    assert issubclass(BadRequestError, WorkOSError)
    assert issubclass(ConflictError, WorkOSError)
    assert issubclass(NotFoundError, WorkOSError)
    assert issubclass(RateLimitExceededError, WorkOSError)
    assert issubclass(ServerError, WorkOSError)
    assert issubclass(UnprocessableEntityError, WorkOSError)

    print("✓ Error classes importable")


def test_pagination_importable() -> None:
    """Verify pagination primitives are exported at the top level."""
    from workos import AsyncPage, ListMetadata, RequestOptions, SyncPage

    assert AsyncPage is not None
    assert ListMetadata is not None
    assert RequestOptions is not None
    assert SyncPage is not None
    print("✓ Pagination and RequestOptions importable")


def test_dependencies_available() -> None:
    """Verify core runtime dependencies are installed and importable."""
    import cryptography
    import httpx
    import jwt

    print("✓ Core dependencies available (httpx, cryptography, pyjwt)")


def main() -> int:
    """Run all smoke tests."""
    print("=" * 60)
    print("WorkOS Python SDK - Smoke Tests")
    print("=" * 60)
    print()

    tests = [
        test_basic_import,
        test_version_accessible,
        test_py_typed_marker,
        test_sync_client_import_and_instantiate,
        test_async_client_import_and_instantiate,
        test_sync_client_modules_accessible,
        test_async_client_modules_accessible,
        test_core_types_importable,
        test_errors_importable,
        test_pagination_importable,
        test_dependencies_available,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        print()

    print("=" * 60)
    if failed == 0:
        print(f"All {len(tests)} smoke tests passed!")
        return 0
    else:
        print(f"FAILED: {failed}/{len(tests)} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
