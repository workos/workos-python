#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ "${1:-}" = "--live" ]; then
  exec uv run --group docs pdoc workos -p 4000 --docformat google
fi
if [ ! -d docs/_site ]; then
  ./scripts/docs.sh
fi
exec python3 -m http.server 4000 --directory docs/_site
