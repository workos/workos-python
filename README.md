# workos-python

Pyhon SDK to conveniently access the [WorkOS API](https://workos.com).

## Installation

To install from PyPi, run the following:
```
pip install workos
```

To install from source, clone the repo and run the following:
```
python setup.py install
```

## Getting Started

The package will need to be configured with your [api key](https://dashboard.workos.com/api-keys) at a minimum and [project id](https://dashboard.workos.com/sso/configuration) if you plan on utilizing SSO:
```python
import workos

workos.api_key = sk_abdsomecharactersm284
workos.project_id = project_b27needthisforssotemxo
```

For your convenience, a client is available as an entry point for accessing the WorkOS feature set:
```python
from workos import client

# URL to redirect a User to to initiate the WorkOS OAuth 2.0 workflow
client.sso.get_authorization_url(
    'customer-domain.com',
    'my-domain.com/auth/callback',
    state={
        'stuff': 'from_the_original_request',
        'more_things': 'ill_get_it_all_back_when_oauth_is_complete',
    }
)

# Get the WorkOSProfile for an authenticated User
client.get_profile(oauth_code)
```