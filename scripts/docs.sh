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

version=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
cat > docs/_site/llms.txt <<EOF
# WorkOS Python SDK

> Official Python client for the WorkOS API. Provides synchronous and
> asynchronous clients for SSO, Directory Sync, User Management, Audit Logs,
> Organizations, Events, Webhooks, and more. Current version: ${version}.

The full API reference is available as markdown at [index.md](index.md).
HTML documentation is at [index.html](index.html).

## Docs

- [Full API reference (markdown)](index.md): every public class and function in the \`workos\` package
- [HTML API reference](index.html): browsable pdoc-rendered site
- [WorkOS product documentation](https://workos.com/docs): guides, concepts, and REST API reference
- [Python SDK guide](https://workos.com/docs/sdks/python): installation and getting started

## Source

- [GitHub repository](https://github.com/workos/workos-python)
- [PyPI package](https://pypi.org/project/workos/)
EOF
