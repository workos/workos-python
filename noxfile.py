"""Nox configuration for multi-version Python testing.

This configuration uses nox-uv for fast, reproducible environment management
with uv's lockfile. Run `nox` to test against all supported Python versions,
or use `nox -s tests-3.12` to test a specific version.
"""

from __future__ import annotations

import nox
from nox_uv import session

# Use uv as the default venv backend for speed
nox.options.default_venv_backend = "uv"

# Reuse virtual environments by default for faster local iteration
nox.options.reuse_venv = "yes"

# All Python versions supported by the SDK (must match CI matrix)
PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]

# Default sessions to run
nox.options.sessions = ["tests"]


@session(python=PYTHON_VERSIONS, uv_groups=["test"])
def tests(s: nox.Session) -> None:
    """Run the test suite against all supported Python versions."""
    args = s.posargs or []
    s.run("pytest", *args)


@session(python=PYTHON_VERSIONS, uv_groups=["test"])
def coverage(s: nox.Session) -> None:
    """Run tests with coverage reporting."""
    s.run("pytest", "--cov=workos", "--cov-report=term-missing", *s.posargs)


@session(uv_only_groups=["lint"])
def lint(s: nox.Session) -> None:
    """Run linting with ruff."""
    s.run("ruff", "check", ".")


@session(uv_only_groups=["lint"])
def format(s: nox.Session) -> None:
    """Check code formatting with ruff."""
    s.run("ruff", "format", "--check", ".")


@session(uv_only_groups=["lint"])
def format_fix(s: nox.Session) -> None:
    """Apply code formatting with ruff."""
    s.run("ruff", "format", ".")


@session(uv_groups=["type_check"])
def typecheck(s: nox.Session) -> None:
    """Run type checking with mypy."""
    s.run("mypy")


@session(uv_groups=["test", "lint", "type_check"])
def ci(s: nox.Session) -> None:
    """Run all CI checks (format, lint, typecheck, tests) for a single Python version.

    This is useful for quick local validation before pushing.
    """
    s.run("ruff", "format", "--check", ".")
    s.run("ruff", "check", ".")
    s.run("mypy")
    s.run("pytest")
