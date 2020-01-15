#!/bin/bash
# Clean out the dist directory so only the current release gets uploaded
rm dist/*

# Build the distribution
python3 setup.py sdist bdist_wheel

# Upload the distribution to PyPi via twine
twine upload dist/*