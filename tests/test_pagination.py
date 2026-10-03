# @oagen-ignore-file

"""Pagination tests: auto_paging_iter, before cursor stripping, and HTTP integration."""

import pytest

from workos._pagination import SyncPage, AsyncPage, ListMetadata
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class FakeItem:
    id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FakeItem":
        return cls(id=data["id"])

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id}


class TestSyncPage:
    def test_has_more_with_after_cursor(self):
        page = SyncPage(
            data=[FakeItem(id="1")],
            list_metadata=ListMetadata(after="cursor_abc"),
        )
        assert page.has_more() is True
        assert page.after == "cursor_abc"

    def test_has_more_without_cursor(self):
        page = SyncPage(
            data=[FakeItem(id="1")],
            list_metadata=ListMetadata(),
        )
        assert page.has_more() is False

    def test_auto_paging_iter_single_page(self):
        page = SyncPage(
            data=[FakeItem(id="1"), FakeItem(id="2")],
            list_metadata=ListMetadata(),
        )
        items = list(page.auto_paging_iter())
        assert len(items) == 2
        assert items[0].id == "1"
        assert items[1].id == "2"

    def test_auto_paging_iter_multi_page(self):
        page2 = SyncPage(
            data=[FakeItem(id="3")],
            list_metadata=ListMetadata(),
        )
        page1 = SyncPage(
            data=[FakeItem(id="1"), FakeItem(id="2")],
            list_metadata=ListMetadata(after="cursor_abc"),
            _fetch_page=lambda after=None: page2,
        )
        items = list(page1.auto_paging_iter())
        assert len(items) == 3
        assert [i.id for i in items] == ["1", "2", "3"]


@pytest.mark.asyncio
class TestAsyncPage:
    async def test_has_more_with_after_cursor(self):
        page = AsyncPage(
            data=[FakeItem(id="1")],
            list_metadata=ListMetadata(after="cursor_abc"),
        )
        assert page.has_more() is True
        assert page.after == "cursor_abc"

    async def test_has_more_without_cursor(self):
        page = AsyncPage(
            data=[FakeItem(id="1")],
            list_metadata=ListMetadata(),
        )
        assert page.has_more() is False

    async def test_auto_paging_iter_single_page(self):
        page = AsyncPage(
            data=[FakeItem(id="1"), FakeItem(id="2")],
            list_metadata=ListMetadata(),
        )
        items = [item async for item in page.auto_paging_iter()]
        assert len(items) == 2
        assert items[0].id == "1"
        assert items[1].id == "2"

    async def test_auto_paging_iter_multi_page(self):
        page2 = AsyncPage(
            data=[FakeItem(id="3")],
            list_metadata=ListMetadata(),
        )

        async def _fetch(after=None):
            return page2

        page1 = AsyncPage(
            data=[FakeItem(id="1"), FakeItem(id="2")],
            list_metadata=ListMetadata(after="cursor_abc"),
            _fetch_page=_fetch,
        )
        items = [item async for item in page1.auto_paging_iter()]
        assert len(items) == 3
        assert [i.id for i in items] == ["1", "2", "3"]


ORG_BASE = {
    "object": "organization",
    "domains": [],
    "metadata": {},
    "external_id": None,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}


class TestPaginationHTTPIntegration:
    """Integration test verifying auto_paging_iter fetches multiple pages via httpx."""

    def test_auto_paging_iter_fetches_two_pages(self, workos, httpx_mock):
        page1_json = {
            "data": [{"id": "org_1", "name": "Org 1", **ORG_BASE}],
            "list_metadata": {"after": "cursor_page2"},
        }
        page2_json = {
            "data": [{"id": "org_2", "name": "Org 2", **ORG_BASE}],
            "list_metadata": {},
        }
        httpx_mock.add_response(json=page1_json)
        httpx_mock.add_response(json=page2_json)

        page = workos.organizations.list_organizations()
        items = list(page.auto_paging_iter())
        assert len(items) == 2
        assert items[0].id == "org_1"
        assert items[1].id == "org_2"

        requests = httpx_mock.get_requests()
        assert len(requests) == 2
        assert "after=cursor_page2" in str(requests[1].url)


class TestPageLocalIteration:
    """Iterating a page yields only that page's data and makes no extra request."""

    def test_iter_yields_current_page_only(self, workos, httpx_mock):
        httpx_mock.add_response(
            json={
                "data": [
                    {"id": "org_1", "name": "Org 1", **ORG_BASE},
                    {"id": "org_2", "name": "Org 2", **ORG_BASE},
                ],
                "list_metadata": {"after": "cursor_page2"},
            }
        )

        page = workos.organizations.list_organizations(
            request_options={"max_retries": 0}
        )
        items = list(page)

        assert [item.id for item in items] == ["org_1", "org_2"]
        assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_aiter_yields_current_page_only(self, async_workos, httpx_mock):
        httpx_mock.add_response(
            json={
                "data": [
                    {"id": "org_1", "name": "Org 1", **ORG_BASE},
                    {"id": "org_2", "name": "Org 2", **ORG_BASE},
                ],
                "list_metadata": {"after": "cursor_page2"},
            }
        )

        page = await async_workos.organizations.list_organizations(
            request_options={"max_retries": 0}
        )
        items = [item async for item in page]

        assert [item.id for item in items] == ["org_1", "org_2"]
        assert len(httpx_mock.get_requests()) == 1
