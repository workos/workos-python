# @oagen-ignore-file

import pytest
import pytest_asyncio

from workos import WorkOSClient, AsyncWorkOSClient


@pytest.fixture
def workos():
    """Create a WorkOS client for testing with guaranteed cleanup."""
    client = WorkOSClient(
        api_key="sk_test_Sz3IQjepeSWaI4cMS4ms4sMuU", client_id="client_test"
    )
    yield client
    client.close()


@pytest_asyncio.fixture
async def async_workos():
    """Create an AsyncWorkOS client for testing with guaranteed cleanup."""
    client = AsyncWorkOSClient(
        api_key="sk_test_Sz3IQjepeSWaI4cMS4ms4sMuU", client_id="client_test"
    )
    try:
        yield client
    finally:
        await client.close()
