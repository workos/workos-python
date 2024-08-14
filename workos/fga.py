from typing import Any, Mapping, Optional, Protocol, Sequence
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
    WarrantQueryResult,
    CheckOperations,
)
from workos.types.fga.list_filters import (
    ResourceListFilters,
    WarrantListFilters,
    QueryListFilters,
)
from workos.types.list_resource import (
    ListArgs,
    ListMetadata,
    ListPage,
    WorkOSListResource,
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

ResourceListResource = WorkOSListResource[Resource, ResourceListFilters, ListMetadata]

ResourceTypeListResource = WorkOSListResource[ResourceType, ListArgs, ListMetadata]

WarrantListResource = WorkOSListResource[Warrant, WarrantListFilters, ListMetadata]

QueryListResource = WorkOSListResource[
    WarrantQueryResult, QueryListFilters, ListMetadata
]


class FGAModule(Protocol):
    def get_resource(self, *, resource_type: str, resource_id: str) -> Resource:
        """
        Get a resource by its type and ID.

        Kwargs:
            resource_type (str): The type of the resource.
            resource_id (str): A unique identifier for the resource.
        Returns:
            Resource: A resource object.
        """
        ...

    def list_resources(
        self,
        *,
        resource_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> ResourceListResource:
        """
        Gets a list of FGA resources.

        Kwargs:
            resource_type (str): The type of the resource. (Optional)
            search (str): Searchable text for a Resource. (Optional)
            limit (int): The maximum number of resources to return. (Optional)
            order ("asc"|"desc"): Sort resources in either ascending or descending (default) order by created_at timestamp. (Optional)
            before (str): A cursor to return resources before. (Optional)
            after (str): A cursor to return resources after. (Optional)
        Returns:
            ResourceListResource: A list of resources with built-in pagination iterator.
        """
        ...

    def create_resource(
        self,
        *,
        resource_type: str,
        resource_id: str,
        meta: Optional[Mapping[str, Any]] = None,
    ) -> Resource:
        """
        Create a new resource.

        Kwargs:
            resource_type (str): The type of the resource.
            resource_id (str): A unique identifier for the resource.
            meta (dict): A dictionary containing additional information about this resource. (Optional)
        Returns:
            Resource: A resource object.
        """
        ...

    def update_resource(
        self,
        *,
        resource_type: str,
        resource_id: str,
        meta: Optional[Mapping[str, Any]] = None,
    ) -> Resource:
        """
        Updates an existing Resource.

        Kwargs:
            resource_type (str): The type of the resource.
            resource_id (str): A unique identifier for the resource.
            meta (dict): A dictionary containing additional information about this resource. (Optional)
        Returns:
            Resource: A resource object.
        """
        ...

    def delete_resource(self, *, resource_type: str, resource_id: str) -> None:
        """
        Deletes a resource by its type and ID.

        Kwargs:
            resource_type (str): The type of the resource.
            resource_id (str): A unique identifier for the resource.

        Returns:
            None
        """
        ...

    def list_resource_types(
        self,
        *,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> ResourceTypeListResource:
        """
        Gets a list of FGA resource types.

        Kwargs:
            limit (int): The maximum number of resources to return. (Optional)
            order ("asc"|"desc"): Sort resource types in either ascending or descending (default) order by created_at timestamp. (Optional)
            before (str): A cursor to return resources before. (Optional)
            after (str): A cursor to return resources after. (Optional)

        Returns:
            ResourceTypeListResource: A list of resource types with built-in pagination iterator.
        """
        ...

    def list_warrants(
        self,
        *,
        subject_type: Optional[str] = None,
        subject_id: Optional[str] = None,
        subject_relation: Optional[str] = None,
        relation: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
        warrant_token: Optional[str] = None,
    ) -> WarrantListResource:
        """
        Gets a list of warrants.

        Kwargs:
            subject_type (str): The type of the subject. (Optional)
            subject_id (str): The ID of the subject. (Optional)
            subject_relation (str): The relation of the subject. (Optional)
            relation (str): The relation of the warrant. (Optional)
            resource_type (str): The type of the resource. (Optional)
            resource_id (str): The ID of the resource. (Optional)
            limit (int): The maximum number of resources to return. (Optional)
            order ("asc"|"desc"): Sort warrants in either ascending or descending (default) order by created_at timestamp. (Optional)
            before (str): A cursor to return resources before. (Optional)
            after (str): A cursor to return resources after. (Optional)
            warrant_token (str): The warrant token. (Optional)

        Returns:
            WarrantListResource: A list of warrants with built-in pagination iterator.
        """
        ...

    def write_warrant(
        self,
        *,
        op: WarrantWriteOperation,
        subject_type: str,
        subject_id: str,
        subject_relation: Optional[str] = None,
        relation: str,
        resource_type: str,
        resource_id: str,
        policy: Optional[str] = None,
    ) -> WriteWarrantResponse:
        """
        Write a warrant.

        Kwargs:
            op ("create"|"delete"): The operation to perform.
            subject_type (str): The type of the subject.
            subject_id (str): The ID of the subject.
            subject_relation (str): The relation of the subject. (Optional)
            relation (str): The relation of the warrant.
            resource_type (str): The type of the resource.
            resource_id (str): The ID of the resource.
            policy (str): The policy to apply. (Optional)

        Returns:
            WriteWarrantResponse: The warrant token.
        """
        ...

    def batch_write_warrants(
        self, *, batch: Sequence[WarrantWrite]
    ) -> WriteWarrantResponse:
        """
        Write a batch of warrants.

        Args:
            batch (Sequence(WarrantWrite)): A list of WarrantWrite objects.

        Returns:
            WriteWarrantResponse: The warrant token.
        """
        ...

    def check(
        self,
        *,
        checks: Sequence[WarrantCheck],
        op: Optional[CheckOperation] = None,
        debug: bool = False,
        warrant_token: Optional[str] = None,
    ) -> CheckResponse:
        """
        Check a warrant.

        Args:
            checks (Sequence(WarrantCheck)): A list of WarrantCheck objects.
            op ("create"|"delete"): The operation to perform. (Optional)
            debug (bool): Whether to return debug information including a decision tree. (Optional)
            warrant_token (str): Optional token to specify desired read consistency. (Optional)
        Returns:
            CheckResponse: A check response.
        """
        ...

    def check_batch(
        self,
        *,
        checks: Sequence[WarrantCheck],
        debug: bool = False,
        warrant_token: Optional[str] = None,
    ) -> Sequence[CheckResponse]:
        """
        Check a batch of warrants.

        Args:
            checks (Sequence(WarrantCheck)): A list of WarrantCheck objects.
            debug (bool): Whether to return debug information including a decision tree. (Optional)
            warrant_token (str): Optional token to specify desired read consistency. (Optional)
        Returns:
            Sequence[CheckResponse]: A list of check responses
        """
        ...

    def query(
        self,
        *,
        q: str,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
        context: Optional[Mapping[str, Any]] = None,
        warrant_token: Optional[str] = None,
    ) -> QueryListResource:
        """
        Query for warrants.

        Args:
            q (str): The query string.
            order ("asc"|"desc"): Sort authorization resources in either ascending or descending (default) order by created_at timestamp. (Optional)
            order (str): The order in which to return resources.
            before (str): A cursor to return resources before. (Optional)
            after (str): A cursor to return resources after. (Optional)
            context (dict): A dictionary containing additional context. (Optional)
            warrant_token (str): Optional token to specify desired read consistency. (Optional)
        Returns:

            QueryListResource: A list of query results with built-in pagination iterator.
        """
        ...


class FGA(FGAModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def get_resource(
        self,
        *,
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
        *,
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

        return WorkOSListResource[Resource, ResourceListFilters, ListMetadata](
            list_method=self.list_resources,
            list_args=list_params,
            **ListPage[Resource](**response).model_dump(),
        )

    def create_resource(
        self,
        *,
        resource_type: str,
        resource_id: str,
        meta: Optional[Mapping[str, Any]] = None,
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
        *,
        resource_type: str,
        resource_id: str,
        meta: Optional[Mapping[str, Any]] = None,
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

    def delete_resource(self, *, resource_type: str, resource_id: str) -> None:
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
        *,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> ResourceTypeListResource:
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

        return WorkOSListResource[ResourceType, ListArgs, ListMetadata](
            list_method=self.list_resource_types,
            list_args=list_params,
            **ListPage[ResourceType](**response).model_dump(),
        )

    def list_warrants(
        self,
        *,
        subject_type: Optional[str] = None,
        subject_id: Optional[str] = None,
        subject_relation: Optional[str] = None,
        relation: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
        warrant_token: Optional[str] = None,
    ) -> WarrantListResource:
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

        return WorkOSListResource[Warrant, WarrantListFilters, ListMetadata](
            list_method=self.list_warrants,
            list_args=list_params,
            **ListPage[Warrant](**response).model_dump(),
        )

    def write_warrant(
        self,
        *,
        op: WarrantWriteOperation,
        subject_type: str,
        subject_id: str,
        subject_relation: Optional[str] = None,
        relation: str,
        resource_type: str,
        resource_id: str,
        policy: Optional[str] = None,
    ) -> WriteWarrantResponse:
        params = {
            "op": op,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "relation": relation,
            "subject": {
                "resource_type": subject_type,
                "resource_id": subject_id,
                "relation": subject_relation,
            },
            "policy": policy,
        }

        response = self._http_client.request(
            "fga/v1/warrants",
            method=REQUEST_METHOD_POST,
            json=params,
        )

        return WriteWarrantResponse.model_validate(response)

    def batch_write_warrants(
        self, *, batch: Sequence[WarrantWrite]
    ) -> WriteWarrantResponse:
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
        *,
        checks: Sequence[WarrantCheck],
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

    def check_batch(
        self,
        *,
        checks: Sequence[WarrantCheck],
        debug: bool = False,
        warrant_token: Optional[str] = None,
    ) -> Sequence[CheckResponse]:
        if not checks:
            raise ValueError("Incomplete arguments: No checks provided")

        body = {
            "checks": [check.dict() for check in checks],
            "op": CheckOperations.BATCH.value,
            "debug": debug,
        }

        response = self._http_client.request(
            "fga/v1/check",
            method=REQUEST_METHOD_POST,
            json=body,
            headers={"Warrant-Token": warrant_token} if warrant_token else None,
        )

        return [CheckResponse.model_validate(check) for check in response]

    def query(
        self,
        *,
        q: str,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
        context: Optional[Mapping[str, Any]] = None,
        warrant_token: Optional[str] = None,
    ) -> QueryListResource:
        list_params: QueryListFilters = {
            "q": q,
            "limit": limit,
            "order": order,
            "before": before,
            "after": after,
            "context": context,
        }

        response = self._http_client.request(
            "fga/v1/query",
            method=REQUEST_METHOD_GET,
            params=list_params,
            headers={"Warrant-Token": warrant_token} if warrant_token else None,
        )

        # A workaround to add warrant_token to the list_args for the ListResource iterator
        list_params["warrant_token"] = warrant_token

        return WorkOSListResource[WarrantQueryResult, QueryListFilters, ListMetadata](
            list_method=self.query,
            list_args=list_params,
            **ListPage[WarrantQueryResult](**response).model_dump(),
        )
