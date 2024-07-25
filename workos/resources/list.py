import abc
from typing import (
    AsyncIterator,
    Awaitable,
    Dict,
    List,
    Literal,
    TypeVar,
    Generic,
    Callable,
    Iterator,
    Optional,
    Union,
    cast,
)
from typing_extensions import Required, TypedDict
from workos.resources.base import WorkOSBaseResource
from workos.resources.directory_sync import (
    Directory,
    DirectoryGroup,
    DirectoryUser,
    DirectoryUserWithGroups,
)
from workos.resources.events import Event
from workos.resources.mfa import AuthenticationFactor
from workos.resources.organizations import Organization
from pydantic import BaseModel, Field
from workos.resources.sso import Connection
from workos.resources.user_management import Invitation, OrganizationMembership, User
from workos.resources.workos_model import WorkOSModel


class WorkOSListResource(WorkOSBaseResource):
    # TODO: THIS OLD RESOURCE GOES AWAY
    """Representation of a WorkOS List Resource as returned through the API.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSListResource is comprised of.
    """

    OBJECT_FIELDS = ["data", "list_metadata", "metadata"]

    @classmethod
    def construct_from_response(cls, response):
        """Returns an instance of WorkOSListResource.

        Args:
            response (dict): Resource data from a WorkOS API response

        Returns:
            WorkOSListResource: Instance of a WorkOSListResource with OBJECT_FIELDS fields set
        """
        obj = cls()
        for field in cls.OBJECT_FIELDS:
            setattr(obj, field, response.get(field))

        return obj

    def to_dict(self):
        """Returns a dict representation of the WorkOSListResource.

        Returns:
            dict: A dict representation of the WorkOSListResource
        """
        obj_dict = {}
        for field in self.OBJECT_FIELDS:
            obj_dict[field] = getattr(self, field, None)

        return obj_dict

    def auto_paging_iter(self):
        """
        This function returns the entire list of items when there are more than 100 unless a limit has been specified.
        """
        data_dict = self.to_dict()
        data = data_dict["data"]
        after = data_dict["list_metadata"]["after"]
        before = data_dict["list_metadata"]["before"]
        method = data_dict["metadata"]["method"]
        order = data_dict["metadata"]["params"]["order"]

        keys_to_remove = ["after", "before"]
        resource_specific_params = {
            k: v
            for k, v in self.to_dict()["metadata"]["params"].items()
            if k not in keys_to_remove
        }

        if "default_limit" not in resource_specific_params:
            if len(data) == resource_specific_params["limit"]:
                yield data
                return
        else:
            del resource_specific_params["default_limit"]

            if before is None:
                next_page_marker = after
                string_direction = "after"
            else:
                order = None
                next_page_marker = before
                string_direction = "before"

            params = {
                "after": after,
                "before": before,
                "order": order or "desc",
            }
            params.update(resource_specific_params)

            params = {k: v for k, v in params.items() if v is not None}

            while next_page_marker is not None:
                response = method(self, **params)
                if type(response) != dict:
                    response = response.to_dict()
                for i in response["data"]:
                    data.append(i)
                next_page_marker = response["list_metadata"][string_direction]
                yield data
                data = []


ListableResource = TypeVar(
    # add all possible generics of List Resource
    "ListableResource",
    AuthenticationFactor,
    Connection,
    Directory,
    DirectoryGroup,
    DirectoryUserWithGroups,
    Event,
    Invitation,
    Organization,
    OrganizationMembership,
    User,
)


class ListAfterMetadata(BaseModel):
    after: Optional[str] = None


class ListMetadata(ListAfterMetadata):
    before: Optional[str] = None


ListMetadataType = TypeVar("ListMetadataType", ListAfterMetadata, ListMetadata)


class ListPage(WorkOSModel, Generic[ListableResource]):
    object: Literal["list"]
    data: List[ListableResource]
    list_metadata: ListMetadata


class ListArgs(TypedDict, total=False):
    before: Optional[str]
    after: Optional[str]
    limit: Required[int]
    order: Optional[Literal["asc", "desc"]]


ListAndFilterParams = TypeVar("ListAndFilterParams", bound=ListArgs)


class BaseWorkOsListResource(
    WorkOSModel,
    Generic[ListableResource, ListAndFilterParams, ListMetadataType],
):
    object: Literal["list"]
    data: List[ListableResource]
    list_metadata: ListMetadataType

    list_method: Callable = Field(exclude=True)
    list_args: ListAndFilterParams = Field(exclude=True)

    def _parse_params(self):
        fixed_pagination_params = cast(
            # Type hints consider this a mismatch because it assume the dictionary is dict[str, int]
            Dict[str, Union[int, str, None]],
            {
                "limit": self.list_args["limit"],
            },
        )
        if "order" in self.list_args:
            fixed_pagination_params["order"] = self.list_args["order"]

        # Omit common list parameters
        filter_params = {
            k: v
            for k, v in self.list_args.items()
            if k not in {"order", "limit", "before", "after"}
        }

        return fixed_pagination_params, filter_params

    @abc.abstractmethod
    def auto_paging_iter(
        self,
    ) -> Union[AsyncIterator[ListableResource], Iterator[ListableResource]]: ...


class WorkOsListResource(
    BaseWorkOsListResource,
    Generic[ListableResource, ListAndFilterParams, ListMetadataType],
):
    def auto_paging_iter(self) -> Iterator[ListableResource]:
        next_page: WorkOsListResource[
            ListableResource, ListAndFilterParams, ListMetadataType
        ]
        after = self.list_metadata.after
        fixed_pagination_params, filter_params = self._parse_params()
        index: int = 0

        while True:
            if index >= len(self.data):
                if after is not None:
                    next_page = self.list_method(
                        after=after, **fixed_pagination_params, **filter_params
                    )
                    self.data = next_page.data
                    after = next_page.list_metadata.after
                    index = 0
                    continue
                else:
                    return
            yield self.data[index]
            index += 1


class AsyncWorkOsListResource(
    BaseWorkOsListResource,
    Generic[ListableResource, ListAndFilterParams, ListMetadataType],
):
    async def auto_paging_iter(self) -> AsyncIterator[ListableResource]:
        next_page: WorkOsListResource[
            ListableResource, ListAndFilterParams, ListMetadataType
        ]
        after = self.list_metadata.after
        fixed_pagination_params, filter_params = self._parse_params()
        index: int = 0

        while True:
            if index >= len(self.data):
                if after is not None:
                    next_page = await self.list_method(
                        after=after, **fixed_pagination_params, **filter_params
                    )
                    self.data = next_page.data
                    after = next_page.list_metadata.after
                    index = 0
                    continue
                else:
                    return
            yield self.data[index]
            index += 1


SyncOrAsyncListResource = Union[
    Awaitable[AsyncWorkOsListResource],
    WorkOsListResource,
]
