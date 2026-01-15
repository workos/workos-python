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

    # Instantiate with dummy credentials (no API calls made)
    client = WorkOSClient(api_key="sk_test_smoke", client_id="client_smoke")
    assert client is not None
    print("✓ WorkOSClient imports and instantiates")


def test_async_client_import_and_instantiate() -> None:
    """Verify async client can be imported and instantiated."""
    from workos import AsyncWorkOSClient

    # Instantiate with dummy credentials (no API calls made)
    client = AsyncWorkOSClient(api_key="sk_test_smoke", client_id="client_smoke")
    assert client is not None
    print("✓ AsyncWorkOSClient imports and instantiates")


def test_sync_client_modules_accessible() -> None:
    """Verify all module properties are accessible on sync client."""
    from workos import WorkOSClient

    client = WorkOSClient(api_key="sk_test_smoke", client_id="client_smoke")

    modules = [
        "api_keys",
        "audit_logs",
        "directory_sync",
        "events",
        "fga",
        "mfa",
        "organizations",
        "organization_domains",
        "passwordless",
        "pipes",
        "portal",
        "sso",
        "user_management",
        "vault",
        "webhooks",
        "widgets",
    ]

    for module_name in modules:
        module = getattr(client, module_name, None)
        assert module is not None, f"Module {module_name} not accessible"
        print(f"  ✓ client.{module_name}")

    print(f"✓ All {len(modules)} sync client modules accessible")


def test_async_client_modules_accessible() -> None:
    """Verify all module properties are accessible on async client.

    Note: Some modules raise NotImplementedError as they're not yet
    supported in the async client. We verify the property exists and
    raises the expected error.
    """
    from workos import AsyncWorkOSClient

    client = AsyncWorkOSClient(api_key="sk_test_smoke", client_id="client_smoke")

    # Modules fully supported in async client
    supported_modules = [
        "api_keys",
        "directory_sync",
        "events",
        "organizations",
        "organization_domains",
        "pipes",
        "sso",
        "user_management",
    ]

    # Modules that exist but raise NotImplementedError
    not_implemented_modules = [
        "audit_logs",
        "fga",
        "mfa",
        "passwordless",
        "portal",
        "vault",
        "webhooks",
        "widgets",
    ]

    for module_name in supported_modules:
        module = getattr(client, module_name, None)
        assert module is not None, f"Module {module_name} not accessible"
        print(f"  ✓ async_client.{module_name}")

    for module_name in not_implemented_modules:
        try:
            getattr(client, module_name)
            raise AssertionError(
                f"Module {module_name} should raise NotImplementedError"
            )
        except NotImplementedError:
            print(f"  ✓ async_client.{module_name} (not yet implemented)")

    total = len(supported_modules) + len(not_implemented_modules)
    print(f"✓ All {total} async client modules verified")


def test_core_types_importable() -> None:
    """Verify core type models can be imported."""
    # SSO types
    from workos.types.sso import Connection, ConnectionDomain, Profile

    assert Connection is not None
    assert ConnectionDomain is not None
    assert Profile is not None

    # Organization types
    from workos.types.organizations import Organization

    assert Organization is not None

    # Directory Sync types
    from workos.types.directory_sync import Directory, DirectoryGroup, DirectoryUser

    assert Directory is not None
    assert DirectoryGroup is not None
    assert DirectoryUser is not None

    # User Management types
    from workos.types.user_management import (
        AuthenticationResponse,
        Invitation,
        OrganizationMembership,
        User,
    )

    assert AuthenticationResponse is not None
    assert Invitation is not None
    assert OrganizationMembership is not None
    assert User is not None

    # Events types
    from workos.types.events import Event

    assert Event is not None

    # FGA types
    from workos.types.fga import Warrant, CheckResponse

    assert Warrant is not None
    assert CheckResponse is not None

    print("✓ Core types importable")


def test_exceptions_importable() -> None:
    """Verify exception classes can be imported."""
    from workos.exceptions import (
        AuthenticationException,
        AuthorizationException,
        BadRequestException,
        ConflictException,
        NotFoundException,
        ServerException,
    )

    assert AuthenticationException is not None
    assert AuthorizationException is not None
    assert BadRequestException is not None
    assert ConflictException is not None
    assert NotFoundException is not None
    assert ServerException is not None

    print("✓ Exception classes importable")


def test_dependencies_available() -> None:
    """Verify core dependencies are installed and importable."""
    import httpx
    import pydantic
    import cryptography
    import jwt

    print("✓ Core dependencies available (httpx, pydantic, cryptography, jwt)")


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
        test_exceptions_importable,
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
