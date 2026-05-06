#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
rm -rf docs/_site
uv run --group docs pdoc workos -o docs/_site --docformat google
if [ ! -f docs/_site/index.html ] && [ -f docs/_site/workos.html ]; then
  cp docs/_site/workos.html docs/_site/index.html
fi
uv run --group docs pydoc-markdown -p workos --render-toc > docs/_site/workos.md
cp docs/_site/workos.md docs/_site/index.md
