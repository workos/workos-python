#!/usr/bin/env bash
#
# Usage:
#   ./scripts/test.sh              # Run tests on all Python versions
#   ./scripts/test.sh 3.12         # Run tests on Python 3.12 only
#   ./scripts/test.sh 3.11 3.12    # Run tests on Python 3.11 and 3.12
#   ./scripts/test.sh --coverage   # Run tests with coverage on all versions
#   ./scripts/test.sh --ci         # Run full CI checks (lint, type, tests)
#   ./scripts/test.sh --fresh      # Recreate virtual environments
#
# Additional pytest arguments can be passed after --, e.g.:
#   ./scripts/test.sh 3.12 -- -k "test_sso" -v

set -e

# Check if uv is available
if ! command -v uv &>/dev/null; then
  echo "Error: uv is not installed or not in PATH"
  echo "Install uv: https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
fi

# Parse arguments
PYTHON_VERSIONS=()
NOX_ARGS=()
PYTEST_ARGS=()
SESSION="tests"
FRESH=false
PARSING_PYTEST_ARGS=false

for arg in "$@"; do
  if [[ "$PARSING_PYTEST_ARGS" == true ]]; then
    PYTEST_ARGS+=("$arg")
  elif [[ "$arg" == "--" ]]; then
    PARSING_PYTEST_ARGS=true
  elif [[ "$arg" == "--coverage" ]]; then
    SESSION="coverage"
  elif [[ "$arg" == "--ci" ]]; then
    SESSION="ci"
  elif [[ "$arg" == "--fresh" ]]; then
    FRESH=true
  elif [[ "$arg" =~ ^3\.[0-9]+$ ]]; then
    PYTHON_VERSIONS+=("$arg")
  else
    NOX_ARGS+=("$arg")
  fi
done

# Build the nox command
CMD=(uv run nox -s)

if [[ ${#PYTHON_VERSIONS[@]} -gt 0 ]]; then
  # Run specific Python versions
  SESSIONS=""
  for ver in "${PYTHON_VERSIONS[@]}"; do
    if [[ -n "$SESSIONS" ]]; then
      SESSIONS="$SESSIONS,"
    fi
    SESSIONS="${SESSIONS}${SESSION}-${ver}"
  done
  CMD+=("$SESSIONS")
else
  # Run all versions
  CMD+=("$SESSION")
fi

# Add fresh flag if requested
if [[ "$FRESH" == true ]]; then
  CMD+=(--reuse-venv=never)
fi

# Add any additional nox args
if [[ ${#NOX_ARGS[@]} -gt 0 ]]; then
  CMD+=("${NOX_ARGS[@]}")
fi

# Add pytest args if provided
if [[ ${#PYTEST_ARGS[@]} -gt 0 ]]; then
  CMD+=(-- "${PYTEST_ARGS[@]}")
fi

echo "Running: ${CMD[*]}"
exec "${CMD[@]}"
