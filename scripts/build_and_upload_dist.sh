#!/bin/bash
# Build the distribution
python3 setup.py sdist bdist_wheel

# Upload the distribution to PyPi via twine
twine upload dist/*