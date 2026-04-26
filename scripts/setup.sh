#!/usr/bin/env bash

if ! command -v uv &>/dev/null; then
  echo "Can't find uv, please install uv or ensure it's available in your PATH before attempting setup."
  exit 1
fi

uv sync --dev

# Install ruff globally so formatters (e.g. oagen) can find it in PATH
if ! command -v ruff &>/dev/null; then
  uv tool install ruff
fi
