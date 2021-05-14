# WorkOS Python Library

![PyPI](https://img.shields.io/pypi/v/workos)
[![Build Status](https://workos.semaphoreci.com/badges/workos-python/branches/master.svg?style=shields&key=9e4cb5bb-86a4-4938-9ec2-fc9f9fc512be)](https://workos.semaphoreci.com/projects/workos-python)

The WorkOS library for Python provides convenient access to the WorkOS API from applications written in Python, [hosted on PyPi](https://pypi.org/project/workos/)

## Documentation

See the [API Reference](https://workos.com/docs/reference/client-libraries) for Python usage examples.

## Installation

To install from PyPi, run the following:

```
pip install workos
```

To install from source, clone the repo and run the following:

```
python setup.py install
```

## Configuration

The package will need to be configured with your [api key](https://dashboard.workos.com/api-keys) at a minimum and [client id](https://dashboard.workos.com/sso/configuration) if you plan on using SSO:

```python
import workos

workos.api_key = "sk_1234"
workos.client_id = "client_1234"
```

## More Information

- [Single Sign-On Guide](https://workos.com/docs/sso/guide)
- [Directory Sync Guide](https://workos.com/docs/directory-sync/guide)
- [Admin Portal Guide](https://workos.com/docs/admin-portal/guide)
- [Magic Link Guide](https://workos.com/docs/magic-link/guide)
