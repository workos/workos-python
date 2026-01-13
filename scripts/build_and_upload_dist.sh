#!/bin/bash
# Clean out the dist directory so only the current release gets uploaded
rm dist/*

# Build the package using uv
uv build --sdist --wheel

# Upload the distribution to PyPi via uv
uv publish

