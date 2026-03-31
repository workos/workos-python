import pytest
from workos import WorkOS, AsyncWorkOS


@pytest.fixture
def workos():
    return WorkOS(
        api_key="sk_test",
        client_id="client_test",
    )


@pytest.fixture
def async_workos():
    return AsyncWorkOS(
        api_key="sk_test",
        client_id="client_test",
    )
