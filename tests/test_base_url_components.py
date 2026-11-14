# @oagen-ignore-file
"""Public-client URL routing through a proxy base with URL components."""

from urllib.parse import parse_qs, urlsplit

import httpx2
import pytest

from workos import AsyncWorkOSClient, WorkOSClient, RequestOptions


BASES = [
    "https://proxy.example.test/prefix",
    "https://proxy.example.test/prefix/",
    "https://proxy.example.test/prefix?route=a%2Fb&label=x+y",
    "https://proxy.example.test/prefix/#section",
    "https://proxy.example.test/prefix?route=a%2Fb&label=x+y#section",
]


@pytest.mark.parametrize("base", BASES)
@pytest.mark.parametrize("override", [False, True])
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_unit_resource_requests_preserve_base_url_components(
    base, override, mode
):
    seen = []

    def respond(request):
        seen.append(request.url)
        return httpx2.Response(200, json={"data": [], "list_metadata": {}})

    options: RequestOptions | None = {"base_url": base} if override else None
    transport = httpx2.MockTransport(respond)
    if mode == "sync":
        with httpx2.Client(transport=transport) as http:
            client = WorkOSClient(
                api_key="sk_test_dummy",
                client_id="client_test",
                base_url=None if override else base,
                http_client=http,
            )
            with client:
                page = client.organizations.list_organizations(
                    limit=2, request_options=options
                )
                assert page.data == []
    else:
        async with httpx2.AsyncClient(transport=transport) as http:
            async_client = AsyncWorkOSClient(
                api_key="sk_test_dummy",
                client_id="client_test",
                base_url=None if override else base,
                http_client=http,
            )
            async with async_client:
                async_page = await async_client.organizations.list_organizations(
                    limit=2, request_options=options
                )
                assert async_page.data == []

    assert len(seen) == 1
    assert seen[0].path == "/prefix/organizations"
    expected = parse_qs(urlsplit(base).query)
    expected["limit"] = ["2"]
    expected["order"] = ["desc"]
    assert parse_qs(seen[0].query.decode()) == expected


@pytest.mark.parametrize("base", BASES)
@pytest.mark.parametrize("resource", ["sso", "user_management"])
def test_unit_authorization_urls_preserve_base_url_components(base, resource):
    with WorkOSClient(
        api_key="sk_test_dummy", client_id="client_test", base_url=base
    ) as client:
        url = getattr(client, resource).get_authorization_url(
            redirect_uri="https://app.example.test/callback", state="a/b?c"
        )
    parts = urlsplit(url)
    assert (
        parts.path
        == f"/prefix/{'sso' if resource == 'sso' else 'user_management'}/authorize"
    )
    query = parse_qs(parts.query)
    for key, value in parse_qs(urlsplit(base).query).items():
        assert query[key] == value
    assert query["redirect_uri"] == ["https://app.example.test/callback"]
    assert query["state"] == ["a/b?c"]
    assert parts.fragment == urlsplit(base).fragment
