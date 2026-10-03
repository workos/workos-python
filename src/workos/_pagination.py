# @oagen-ignore-file

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Literal,
    Optional,
    TypeVar,
)

from ._types import Deserializable

T = TypeVar("T", bound=Deserializable)

PaginationDirection = Literal["forward", "backward"]
"""Direction a page paginates in: ``forward`` follows ``after``, ``backward`` follows ``before``."""


@dataclass(slots=True)
class ListMetadata:
    """Pagination cursor metadata."""

    before: Optional[str] = None
    after: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListMetadata":
        return cls(before=data.get("before"), after=data.get("after"))


@dataclass
class SyncPage(Generic[T]):
    """A page of results with auto-pagination support."""

    data: List[T]
    list_metadata: ListMetadata
    _fetch_page: Optional[Callable[..., "SyncPage[T]"]] = field(
        default=None, repr=False
    )
    _direction: PaginationDirection = field(default="forward", repr=False)

    @property
    def before(self) -> Optional[str]:
        """Cursor for the previous page, if available."""
        return self.list_metadata.before

    @property
    def after(self) -> Optional[str]:
        """Cursor for the next page, if available."""
        return self.list_metadata.after

    def has_more(self) -> bool:
        """Whether there are more pages available."""
        return self.after is not None

    def auto_paging_iter(self) -> Iterator[T]:
        """Iterate through all items across all pages.

        Follows the page's direction: forward pages keep fetching with
        ``after``; a page first requested with a ``before`` cursor keeps
        fetching with ``before`` and yields each page's items reversed.
        """
        page = self
        backward = page._direction == "backward"
        while True:
            items = reversed(page.data) if backward else page.data
            yield from items
            if not page.data:
                break
            if backward:
                if page.before is None or page._fetch_page is None:
                    break
                page = page._fetch_page(before=page.before)
            else:
                if not page.has_more() or page._fetch_page is None:
                    break
                page = page._fetch_page(after=page.after)

    def __iter__(self) -> Iterator[T]:
        """Iterate through all items across all pages."""
        return self.auto_paging_iter()


@dataclass
class AsyncPage(Generic[T]):
    """A page of results with async auto-pagination support."""

    data: List[T]
    list_metadata: ListMetadata
    _fetch_page: Optional[Callable[..., Awaitable["AsyncPage[T]"]]] = field(
        default=None, repr=False
    )
    _direction: PaginationDirection = field(default="forward", repr=False)

    @property
    def before(self) -> Optional[str]:
        """Cursor for the previous page, if available."""
        return self.list_metadata.before

    @property
    def after(self) -> Optional[str]:
        """Cursor for the next page, if available."""
        return self.list_metadata.after

    def has_more(self) -> bool:
        """Whether there are more pages available."""
        return self.after is not None

    async def auto_paging_iter(self) -> AsyncIterator[T]:
        """Iterate through all items across all pages.

        Follows the page's direction: forward pages keep fetching with
        ``after``; a page first requested with a ``before`` cursor keeps
        fetching with ``before`` and yields each page's items reversed.
        """
        page = self
        backward = page._direction == "backward"
        while True:
            items = reversed(page.data) if backward else page.data
            for item in items:
                yield item
            if not page.data:
                break
            if backward:
                if page.before is None or page._fetch_page is None:
                    break
                page = await page._fetch_page(before=page.before)
            else:
                if not page.has_more() or page._fetch_page is None:
                    break
                page = await page._fetch_page(after=page.after)

    def __aiter__(self) -> AsyncIterator[T]:
        """Iterate through all items across all pages."""
        return self.auto_paging_iter()
