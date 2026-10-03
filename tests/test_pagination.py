# @oagen-ignore-file

"""Pagination tests: auto_paging_iter, before cursor stripping, and HTTP integration."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import pytest

from workos._pagination import SyncPage, AsyncPage, ListMetadata


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


class TestPaginationHTTPIntegration:
    """Integration test verifying auto_paging_iter fetches multiple pages via httpx."""

    def test_auto_paging_iter_fetches_two_pages(self, workos, httpx_mock):
        org_base = {
            "object": "organization",
            "domains": [],
            "metadata": {},
            "external_id": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        page1_json = {
            "data": [{"id": "org_1", "name": "Org 1", **org_base}],
            "list_metadata": {"after": "cursor_page2"},
        }
        page2_json = {
            "data": [{"id": "org_2", "name": "Org 2", **org_base}],
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


def _user_json(user_id: str) -> Dict[str, Any]:
    return {
        "object": "user",
        "id": user_id,
        "first_name": None,
        "last_name": None,
        "profile_picture_url": None,
        "email": f"{user_id}@example.com",
        "email_verified": True,
        "external_id": None,
        "last_sign_in_at": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


def _user_page_json(
    ids: List[str],
    *,
    before: Optional[str] = None,
    after: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "data": [_user_json(i) for i in ids],
        "list_metadata": {"before": before, "after": after},
    }


def _query(request: Any) -> Dict[str, List[str]]:
    return parse_qs(urlparse(str(request.url)).query)


class TestAutoPagingDirection:
    """auto_paging_iter follows the direction of the initial request."""

    def test_forward_full_traversal(self, workos, httpx_mock):
        for i in range(10):
            ids = [f"u{n}" for n in range(i * 10 + 1, i * 10 + 11)]
            httpx_mock.add_response(
                json=_user_page_json(ids, after=f"u{(i + 1) * 10}" if i < 9 else None)
            )

        page = workos.user_management.list_users(limit=10)
        assert [u.id for u in page.auto_paging_iter()] == [
            f"u{n}" for n in range(1, 101)
        ]

        requests = httpx_mock.get_requests()
        assert len(requests) == 10
        assert _query(requests[0]) == {"limit": ["10"], "order": ["desc"]}
        for k in range(1, 10):
            assert _query(requests[k]) == {
                "limit": ["10"],
                "order": ["desc"],
                "after": [f"u{k * 10}"],
            }

    def test_backward_full_traversal(self, workos, httpx_mock):
        httpx_mock.add_response(
            json=_user_page_json(
                [f"u{n}" for n in range(11, 21)], before="u11", after="u21"
            )
        )
        httpx_mock.add_response(json=_user_page_json([f"u{n}" for n in range(1, 11)]))

        page = workos.user_management.list_users(before="u21", limit=10)
        assert [u.id for u in page.auto_paging_iter()] == [
            f"u{n}" for n in range(20, 0, -1)
        ]

        requests = httpx_mock.get_requests()
        assert len(requests) == 2
        assert _query(requests[0]) == {
            "limit": ["10"],
            "order": ["desc"],
            "before": ["u21"],
        }
        assert _query(requests[1]) == {
            "limit": ["10"],
            "order": ["desc"],
            "before": ["u11"],
        }

    def test_request_page_does_not_mutate_params(self, workos, httpx_mock):
        httpx_mock.add_response(json=_user_page_json(["u2"], before="u1", after="u3"))
        httpx_mock.add_response(json=_user_page_json(["u1"]))
        params: Dict[str, Any] = {"before": "u3", "limit": 1}

        page = workos.request_page(
            "get", ("user_management", "users"), model=FakeItem, params=params
        )
        assert [i.id for i in page.auto_paging_iter()] == ["u2", "u1"]

        assert params == {"before": "u3", "limit": 1}
        assert len(httpx_mock.get_requests()) == 2


@pytest.mark.asyncio
class TestAsyncAutoPagingDirection:
    """Async auto_paging_iter follows the direction of the initial request."""

    async def test_forward_full_traversal(self, async_workos, httpx_mock):
        for i in range(10):
            ids = [f"u{n}" for n in range(i * 10 + 1, i * 10 + 11)]
            httpx_mock.add_response(
                json=_user_page_json(ids, after=f"u{(i + 1) * 10}" if i < 9 else None)
            )

        page = await async_workos.user_management.list_users(limit=10)
        assert [u.id async for u in page.auto_paging_iter()] == [
            f"u{n}" for n in range(1, 101)
        ]

        requests = httpx_mock.get_requests()
        assert len(requests) == 10
        assert _query(requests[0]) == {"limit": ["10"], "order": ["desc"]}
        for k in range(1, 10):
            assert _query(requests[k]) == {
                "limit": ["10"],
                "order": ["desc"],
                "after": [f"u{k * 10}"],
            }

    async def test_backward_full_traversal(self, async_workos, httpx_mock):
        httpx_mock.add_response(
            json=_user_page_json(
                [f"u{n}" for n in range(11, 21)], before="u11", after="u21"
            )
        )
        httpx_mock.add_response(json=_user_page_json([f"u{n}" for n in range(1, 11)]))

        page = await async_workos.user_management.list_users(before="u21", limit=10)
        assert [u.id async for u in page.auto_paging_iter()] == [
            f"u{n}" for n in range(20, 0, -1)
        ]

        requests = httpx_mock.get_requests()
        assert len(requests) == 2
        assert _query(requests[0]) == {
            "limit": ["10"],
            "order": ["desc"],
            "before": ["u21"],
        }
        assert _query(requests[1]) == {
            "limit": ["10"],
            "order": ["desc"],
            "before": ["u11"],
        }

    async def test_request_page_does_not_mutate_params(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=_user_page_json(["u2"], before="u1", after="u3"))
        httpx_mock.add_response(json=_user_page_json(["u1"]))
        params: Dict[str, Any] = {"before": "u3", "limit": 1}

        page = await async_workos.request_page(
            "get", ("user_management", "users"), model=FakeItem, params=params
        )
        assert [i.id async for i in page.auto_paging_iter()] == ["u2", "u1"]

        assert params == {"before": "u3", "limit": 1}
        assert len(httpx_mock.get_requests()) == 2
