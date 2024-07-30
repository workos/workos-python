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
from workos.resources.directory_sync import (
    Directory,
    DirectoryGroup,
    DirectoryUserWithGroups,
)
from workos.resources.events import Event
from workos.resources.mfa import AuthenticationFactor
from workos.resources.organizations import Organization
from pydantic import BaseModel, Field
from workos.resources.sso import ConnectionWithDomains
from workos.resources.user_management import Invitation, OrganizationMembership, User
from workos.resources.workos_model import WorkOSModel


ListableResource = TypeVar(
    # add all possible generics of List Resource
    "ListableResource",
    AuthenticationFactor,
    ConnectionWithDomains,
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
