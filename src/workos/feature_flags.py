from typing import Optional, Protocol

from workos.types.feature_flags import FeatureFlag
from workos.types.feature_flags.list_filters import FeatureFlagListFilters
from workos.types.list_resource import ListMetadata, ListPage, WorkOSListResource
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.utils.request_helper import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_PUT,
)

FEATURE_FLAGS_PATH = "feature-flags"

FeatureFlagsListResource = WorkOSListResource[
    FeatureFlag, FeatureFlagListFilters, ListMetadata
]


class FeatureFlagsModule(Protocol):
    """Offers methods through the WorkOS Feature Flags service."""

    def list_feature_flags(
        self,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[FeatureFlagsListResource]:
        """Retrieve a list of feature flags.

        Kwargs:
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided ID. (Optional)
            after (str): Pagination cursor to receive records after a provided ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending order. (Optional)

        Returns:
            FeatureFlagsListResource: Feature flags list response from WorkOS.
        """
        ...

    def get_feature_flag(self, slug: str) -> SyncOrAsync[FeatureFlag]:
        """Gets details for a single feature flag.

        Args:
            slug (str): The unique slug identifier of the feature flag.

        Returns:
            FeatureFlag: Feature flag response from WorkOS.
        """
        ...

    def enable_feature_flag(self, slug: str) -> SyncOrAsync[FeatureFlag]:
        """Enable a feature flag.

        Args:
            slug (str): The unique slug identifier of the feature flag.

        Returns:
            FeatureFlag: Updated feature flag response from WorkOS.
        """
        ...

    def disable_feature_flag(self, slug: str) -> SyncOrAsync[FeatureFlag]:
        """Disable a feature flag.

        Args:
            slug (str): The unique slug identifier of the feature flag.

        Returns:
            FeatureFlag: Updated feature flag response from WorkOS.
        """
        ...

    def add_feature_flag_target(self, slug: str, resource_id: str) -> SyncOrAsync[None]:
        """Add a target to a feature flag.

        Args:
            slug (str): The unique slug identifier of the feature flag.
            resource_id (str): Resource ID in format user_<id> or org_<id>.

        Returns:
            None
        """
        ...

    def remove_feature_flag_target(
        self, slug: str, resource_id: str
    ) -> SyncOrAsync[None]:
        """Remove a target from a feature flag.

        Args:
            slug (str): The unique slug identifier of the feature flag.
            resource_id (str): Resource ID in format user_<id> or org_<id>.

        Returns:
            None
        """
        ...


class FeatureFlags(FeatureFlagsModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list_feature_flags(
        self,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> FeatureFlagsListResource:
        list_params: FeatureFlagListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            FEATURE_FLAGS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[FeatureFlag, FeatureFlagListFilters, ListMetadata](
            list_method=self.list_feature_flags,
            list_args=list_params,
            **ListPage[FeatureFlag](**response).model_dump(),
        )

    def get_feature_flag(self, slug: str) -> FeatureFlag:
        response = self._http_client.request(
            f"{FEATURE_FLAGS_PATH}/{slug}",
            method=REQUEST_METHOD_GET,
        )

        return FeatureFlag.model_validate(response)

    def enable_feature_flag(self, slug: str) -> FeatureFlag:
        response = self._http_client.request(
            f"{FEATURE_FLAGS_PATH}/{slug}/enable",
            method=REQUEST_METHOD_PUT,
            json={},
        )

        return FeatureFlag.model_validate(response)

    def disable_feature_flag(self, slug: str) -> FeatureFlag:
        response = self._http_client.request(
            f"{FEATURE_FLAGS_PATH}/{slug}/disable",
            method=REQUEST_METHOD_PUT,
            json={},
        )

        return FeatureFlag.model_validate(response)

    def add_feature_flag_target(self, slug: str, resource_id: str) -> None:
        self._http_client.request(
            f"{FEATURE_FLAGS_PATH}/{slug}/targets/{resource_id}",
            method=REQUEST_METHOD_POST,
            json={},
        )

    def remove_feature_flag_target(self, slug: str, resource_id: str) -> None:
        self._http_client.request(
            f"{FEATURE_FLAGS_PATH}/{slug}/targets/{resource_id}",
            method=REQUEST_METHOD_DELETE,
        )


class AsyncFeatureFlags(FeatureFlagsModule):
    _http_client: AsyncHTTPClient

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list_feature_flags(
        self,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> FeatureFlagsListResource:
        list_params: FeatureFlagListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            FEATURE_FLAGS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[FeatureFlag, FeatureFlagListFilters, ListMetadata](
            list_method=self.list_feature_flags,
            list_args=list_params,
            **ListPage[FeatureFlag](**response).model_dump(),
        )

    async def get_feature_flag(self, slug: str) -> FeatureFlag:
        response = await self._http_client.request(
            f"{FEATURE_FLAGS_PATH}/{slug}",
            method=REQUEST_METHOD_GET,
        )

        return FeatureFlag.model_validate(response)

    async def enable_feature_flag(self, slug: str) -> FeatureFlag:
        response = await self._http_client.request(
            f"{FEATURE_FLAGS_PATH}/{slug}/enable",
            method=REQUEST_METHOD_PUT,
            json={},
        )

        return FeatureFlag.model_validate(response)

    async def disable_feature_flag(self, slug: str) -> FeatureFlag:
        response = await self._http_client.request(
            f"{FEATURE_FLAGS_PATH}/{slug}/disable",
            method=REQUEST_METHOD_PUT,
            json={},
        )

        return FeatureFlag.model_validate(response)

    async def add_feature_flag_target(self, slug: str, resource_id: str) -> None:
        await self._http_client.request(
            f"{FEATURE_FLAGS_PATH}/{slug}/targets/{resource_id}",
            method=REQUEST_METHOD_POST,
            json={},
        )

    async def remove_feature_flag_target(self, slug: str, resource_id: str) -> None:
        await self._http_client.request(
            f"{FEATURE_FLAGS_PATH}/{slug}/targets/{resource_id}",
            method=REQUEST_METHOD_DELETE,
        )
