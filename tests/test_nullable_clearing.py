import json

import pytest

from tests.generated_helpers import load_fixture


def _request_body(httpx_mock):
    request = httpx_mock.get_request()
    return json.loads(request.content)


class TestNullableClearing:
    """Verifies the oagen "explicit None clears a nullable field" behavior:

    - omitting a nullable argument leaves the field out of the request body
    - passing an explicit None sends JSON null (clearing the field)
    - passing a value sends that value
    """

    def test_omitted_nullable_field_is_not_sent(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("organization.json"))
        workos.organizations.update_organization(id="org_123", name="New Name")
        body = _request_body(httpx_mock)
        assert "external_id" not in body
        assert body["name"] == "New Name"

    def test_explicit_none_clears_nullable_field(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("organization.json"))
        workos.organizations.update_organization(id="org_123", external_id=None)
        body = _request_body(httpx_mock)
        assert "external_id" in body
        assert body["external_id"] is None

    def test_concrete_value_is_sent(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("organization.json"))
        workos.organizations.update_organization(id="org_123", external_id="ext-1")
        body = _request_body(httpx_mock)
        assert body["external_id"] == "ext-1"

    def test_user_explicit_none_clears_external_id(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("user.json"))
        workos.user_management.update_user(id="user_123", external_id=None)
        body = _request_body(httpx_mock)
        assert "external_id" in body
        assert body["external_id"] is None

    def test_user_omitted_external_id_is_not_sent(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("user.json"))
        workos.user_management.update_user(id="user_123", first_name="Ada")
        body = _request_body(httpx_mock)
        assert "external_id" not in body
        assert body["first_name"] == "Ada"


class TestAsyncNullableClearing:
    @pytest.mark.asyncio
    async def test_explicit_none_clears_nullable_field(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("organization.json"))
        await async_workos.organizations.update_organization(
            id="org_123", external_id=None
        )
        body = _request_body(httpx_mock)
        assert "external_id" in body
        assert body["external_id"] is None

    @pytest.mark.asyncio
    async def test_omitted_nullable_field_is_not_sent(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("organization.json"))
        await async_workos.organizations.update_organization(
            id="org_123", name="New Name"
        )
        body = _request_body(httpx_mock)
        assert "external_id" not in body
