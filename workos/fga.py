from typing import Any, Dict, List, Optional, Protocol
from workos.types.fga import (
    CheckOperation,
    CheckResponse,
    Resource,
    ResourceType,
    Warrant,
    WarrantCheck,
    WarrantWrite,
    WarrantWriteOperation,
    WriteWarrantResponse,
)
from workos.types.fga.list_filters import ResourceListFilters, WarrantListFilters
from workos.types.list_resource import (
    ListArgs,
    ListMetadata,
    ListPage,
    WorkOsListResource,
)
from workos.utils.http_client import SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.utils.request_helper import (
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_PUT,
    RequestHelper,
)

DEFAULT_RESPONSE_LIMIT = 10

ResourceListResource = WorkOsListResource[Resource, ResourceListFilters, ListMetadata]

ResourceTypeListResource = WorkOsListResource[Resource, ListArgs, ListMetadata]

WarrantListResource = WorkOsListResource[Warrant, WarrantListFilters, ListMetadata]


class FGAModule(Protocol):
    def get_resource(self, resource_type: str, resource_id: str) -> Resource: ...

    def list_resources(
        self,
        resource_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> ResourceListResource: ...

    def create_resource(
        self,
        resource_type: str,
        resource_id: str,
        meta: Dict[str, Any],
    ) -> Resource: ...

    def update_resource(
        self,
        resource_type: str,
        resource_id: str,
        meta: Dict[str, Any],
    ) -> Resource: ...

    def delete_resource(self, resource_type: str, resource_id: str) -> None: ...

    def list_resource_types(
        self,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> WorkOsListResource[ResourceType, ListArgs, ListMetadata]: ...

    def list_warrants(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        relation: Optional[str] = None,
        subject_type: Optional[str] = None,
        subject_id: Optional[str] = None,
        subject_relation: Optional[str] = None,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
        warrant_token: Optional[str] = None,
    ) -> WorkOsListResource[Warrant, WarrantListFilters, ListMetadata]: ...

    def write_warrant(
        self,
        op: WarrantWriteOperation,
        resource_type: str,
        resource_id: str,
        relation: str,
        subject_type: str,
        subject_id: str,
        subject_relation: Optional[str] = None,
        policy: Optional[str] = None,
    ) -> WriteWarrantResponse: ...

    def batch_write_warrants(
        self, batch: List[WarrantWrite]
    ) -> WriteWarrantResponse: ...

    def check(
        self,
        checks: List[WarrantCheck],
        op: Optional[CheckOperation] = None,
        debug: bool = False,
        warrant_token: Optional[str] = None,
    ) -> CheckResponse: ...


class FGA(FGAModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def get_resource(
        self,
        resource_type: str,
        resource_id: str,
    ) -> Resource:
        if not resource_type or not resource_id:
            raise ValueError(
                "Incomplete arguments: 'resource_type' and 'resource_id' are required arguments"
            )

        response = self._http_client.request(
            RequestHelper.build_parameterized_url(
                "fga/v1/resources/{resource_type}/{resource_id}",
                resource_type=resource_type,
                resource_id=resource_id,
            ),
            method=REQUEST_METHOD_GET,
        )

        return Resource.model_validate(response)

    def list_resources(
        self,
        resource_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> ResourceListResource:

        list_params: ResourceListFilters = {
            "resource_type": resource_type,
            "search": search,
            "limit": limit,
            "order": order,
            "before": before,
            "after": after,
        }

        response = self._http_client.request(
            "fga/v1/resources",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOsListResource[Resource, ResourceListFilters, ListMetadata](
            list_method=self.list_resources,
            list_args=list_params,
            **ListPage[Resource](**response).model_dump(),
        )

    def create_resource(
        self,
        resource_type: str,
        resource_id: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Resource:
        if not resource_type or not resource_id:
            raise ValueError(
                "Incomplete arguments: 'resource_type' and 'resource_id' are required arguments"
            )

        response = self._http_client.request(
            "fga/v1/resources",
            method=REQUEST_METHOD_POST,
            json={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "meta": meta,
            },
        )

        return Resource.model_validate(response)

    def update_resource(
        self,
        resource_type: str,
        resource_id: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Resource:
        if not resource_type or not resource_id:
            raise ValueError(
                "Incomplete arguments: 'resource_type' and 'resource_id' are required arguments"
            )

        response = self._http_client.request(
            RequestHelper.build_parameterized_url(
                "fga/v1/resources/{resource_type}/{resource_id}",
                resource_type=resource_type,
                resource_id=resource_id,
            ),
            method=REQUEST_METHOD_PUT,
            json={"meta": meta},
        )

        return Resource.model_validate(response)

    def delete_resource(self, resource_type: str, resource_id: str) -> None:
        if not resource_type or not resource_id:
            raise ValueError(
                "Incomplete arguments: 'resource_type' and 'resource_id' are required arguments"
            )

        self._http_client.request(
            RequestHelper.build_parameterized_url(
                "fga/v1/resources/{resource_type}/{resource_id}",
                resource_type=resource_type,
                resource_id=resource_id,
            ),
            method=REQUEST_METHOD_DELETE,
        )

    def list_resource_types(
        self,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> WorkOsListResource[ResourceType, ListArgs, ListMetadata]:

        list_params: ListArgs = {
            "limit": limit,
            "order": order,
            "before": before,
            "after": after,
        }

        response = self._http_client.request(
            "fga/v1/resource-types",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOsListResource[ResourceType, ListArgs, ListMetadata](
            list_method=self.list_resource_types,
            list_args=list_params,
            **ListPage[ResourceType](**response).model_dump(),
        )

    def list_warrants(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        relation: Optional[str] = None,
        subject_type: Optional[str] = None,
        subject_id: Optional[str] = None,
        subject_relation: Optional[str] = None,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
        warrant_token: Optional[str] = None,
    ) -> WorkOsListResource[Warrant, WarrantListFilters, ListMetadata]:
        list_params: WarrantListFilters = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "relation": relation,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "subject_relation": subject_relation,
            "limit": limit,
            "order": order,
            "before": before,
            "after": after,
        }

        response = self._http_client.request(
            "fga/v1/warrants",
            method=REQUEST_METHOD_GET,
            params=list_params,
            headers={"Warrant-Token": warrant_token} if warrant_token else None,
        )

        # A workaround to add warrant_token to the list_args for the ListResource iterator
        list_params["warrant_token"] = warrant_token

        return WorkOsListResource[Warrant, WarrantListFilters, ListMetadata](
            list_method=self.list_warrants,
            list_args=list_params,
            **ListPage[Warrant](**response).model_dump(),
        )

    def write_warrant(
        self,
        op: WarrantWriteOperation,
        resource_type: str,
        resource_id: str,
        relation: str,
        subject_type: str,
        subject_id: str,
        subject_relation: Optional[str] = None,
        policy: Optional[str] = None,
    ) -> WriteWarrantResponse:
        params = {
            "op": op,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "relation": relation,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "subject_relation": subject_relation,
            "policy": policy,
        }

        response = self._http_client.request(
            "fga/v1/warrants",
            method=REQUEST_METHOD_POST,
            json=params,
        )

        return WriteWarrantResponse.model_validate(response)

    def batch_write_warrants(self, batch: List[WarrantWrite]) -> WriteWarrantResponse:
        if not batch:
            raise ValueError("Incomplete arguments: No batch warrant writes provided")

        response = self._http_client.request(
            "fga/v1/warrants",
            method=REQUEST_METHOD_POST,
            json=[warrant.dict() for warrant in batch],
        )

        return WriteWarrantResponse.model_validate(response)

    def check(
        self,
        checks: List[WarrantCheck],
        op: Optional[CheckOperation] = None,
        debug: bool = False,
        warrant_token: Optional[str] = None,
    ) -> CheckResponse:
        if not checks:
            raise ValueError("Incomplete arguments: No checks provided")

        body = {
            "checks": [check.dict() for check in checks],
            "op": op,
            "debug": debug,
        }

        response = self._http_client.request(
            "fga/v1/check",
            method=REQUEST_METHOD_POST,
            json=body,
            headers={"Warrant-Token": warrant_token} if warrant_token else None,
        )

        return CheckResponse.model_validate(response)
