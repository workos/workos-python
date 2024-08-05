from pydantic import BaseModel, Field
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Literal,
    Sequence,
    Tuple,
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
from workos.resources.sso import ConnectionWithDomains
from workos.resources.user_management import Invitation, OrganizationMembership, User
from workos.resources.workos_model import WorkOSModel
from workos.typing.sync_or_async import SyncOrAsync


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
    data: Sequence[ListableResource]
    list_metadata: ListMetadata


class ListArgs(TypedDict, total=False):
    before: Optional[str]
    after: Optional[str]
    limit: Required[int]
    order: Optional[Literal["asc", "desc"]]


ListAndFilterParams = TypeVar("ListAndFilterParams", bound=ListArgs)


class WorkOsListResource(
    WorkOSModel,
    Generic[ListableResource, ListAndFilterParams, ListMetadataType],
):
    object: Literal["list"]
    data: Sequence[ListableResource]
    list_metadata: ListMetadataType

    list_method: Callable[
        ...,
        "SyncOrAsync[WorkOsListResource[ListableResource, ListAndFilterParams, ListMetadataType]]",
    ] = Field(exclude=True)
    list_args: ListAndFilterParams = Field(exclude=True)

    def _parse_params(
        self,
    ) -> Tuple[Dict[str, Union[int, str, None]], Dict[str, Any]]:
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

    # Pydantic uses a custom `__iter__` method to support casting BaseModels
    # to dictionaries. e.g. dict(model).
    # As we want to support `for item in page`, this is inherently incompatible
    # with the default pydantic behaviour. It is not possible to support both
    # use cases at once. Fortunately, this is not a big deal as all other pydantic
    # methods should continue to work as expected as there is an alternative method
    # to cast a model to a dictionary, model.dict(), which is used internally
    # by pydantic.
    def __iter__(self) -> Iterator[ListableResource]:  # type: ignore
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

    async def __aiter__(self) -> AsyncIterator[ListableResource]:
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
