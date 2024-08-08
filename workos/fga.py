from enum import Enum
from typing import Protocol, Optional, Any, Dict

import workos
from workos.resources.fga import Resource, ResourceType, Warrant, WriteWarrantResponse
from workos.resources.list import ListArgs, ListMetadata, WorkOsListResource, ListPage
from workos.utils.http_client import SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder, Order
from workos.utils.request_helper import (
    RequestHelper,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_PUT,
    REQUEST_METHOD_DELETE,
)
from workos.utils.validation import validate_settings, Module

DEFAULT_RESPONSE_LIMIT = 10


class WarrantWriteOperation(Enum):
    CREATE = "create"
    DELETE = "delete"


class ResourceListFilters(ListArgs, total=False):
    resource_type: Optional[str]
    search: Optional[str]


ResourceListResource = WorkOsListResource[Resource, ResourceListFilters, ListMetadata]

ResourceTypeListResource = WorkOsListResource[Resource, ListArgs, ListMetadata]


class WarrantListFilters(ListArgs, total=False):
    resource_type: Optional[str]
    resource_id: Optional[str]
    relation: Optional[str]
    subject_type: Optional[str]
    subject_id: Optional[str]
    subject_relation: Optional[str]
    warrant_token: Optional[str]


WarrantListResource = WorkOsListResource[Warrant, WarrantListFilters, ListMetadata]


class FGAModule(Protocol):
    def get_resource(self, resource_type: str, resource_id: str) -> Resource: ...

    def list_resources(
        self,
        resource_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = Order.Desc.value,
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
        order: PaginationOrder = Order.Desc.value,
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
        order: PaginationOrder = Order.Desc.value,
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


class FGA(FGAModule):
    _http_client: SyncHTTPClient

    @validate_settings(Module.FGA)
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
            token=workos.api_key,
        )

        return Resource.model_validate(response)

    def list_resources(
        self,
        resource_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = Order.Desc.value,
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
            token=workos.api_key,
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
            token=workos.api_key,
            params={
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
            token=workos.api_key,
            params={"meta": meta},
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
            token=workos.api_key,
        )

    def list_resource_types(
        self,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = Order.Desc.value,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> WorkOsListResource[ResourceType, ListArgs, ListMetadata]:

        list_params = {"limit": limit, "order": order, "before": before, "after": after}

        response = self._http_client.request(
            "fga/v1/resource-types",
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
            params=list_params,
        )

        return WorkOsListResource[ResourceType, ListArgs, ListMetadata](
            list_method=self.list_resources,
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
        order: PaginationOrder = Order.Desc.value,
        before: Optional[str] = None,
        after: Optional[str] = None,
        warrant_token: Optional[str] = None,
    ) -> WorkOsListResource[Warrant, WarrantListFilters, ListMetadata]:
        list_params = {
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
            token=workos.api_key,
            params=list_params,
            headers={"Warrant-Token": warrant_token},
        )

        next_list_args = {**list_params, "warrant_token": warrant_token}

        return WorkOsListResource[Warrant, WarrantListFilters, ListMetadata](
            list_method=self.list_resources,
            list_args=next_list_args,
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
            "op": op.value,
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
            token=workos.api_key,
            params=params,
        )

        return WriteWarrantResponse.model_validate(response)

    def batch_write_warrants(self):
        raise NotImplementedError

    def check(self):
        raise NotImplementedError

    def check_batch(self):
        raise NotImplementedError

    def query(self):
        raise NotImplementedError
