from abc import abstractmethod
from typing import (
    List,
    Any,
    Literal,
    TypeVar,
    Generic,
    Callable,
    Iterator,
    Optional,
)

from workos.resources.base import WorkOSBaseResource
from workos.resources.organizations import Organization

from pydantic import BaseModel, Extra


class WorkOSListResource(WorkOSBaseResource):
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


# add all possible generics of List Resource
T = TypeVar("T", Organization, Any)


class ListMetadata(BaseModel):
    after: Optional[str] = None
    before: Optional[str] = None


class ListArgs(BaseModel, extra=Extra.allow):
    limit: Optional[int] = 10
    before: Optional[str] = None
    after: Optional[str] = None
    order: Literal["asc", "desc"] = "desc"

    class Config:
        extra = "allow"


class WorkOsListResource(BaseModel, Generic[T]):
    object: Literal["list"]
    data: List[T]
    list_metadata: ListMetadata

    list_method: Callable
    list_args: ListArgs

    def auto_paging_iter(self) -> Iterator[T]:
        next_page: WorkOsListResource[T]

        after = self.list_metadata.after
        order = self.list_args.order

        fixed_pagination_params = {"order": order, "limit": self.list_args.limit}
        filter_params = self.list_args.model_dump(
            exclude={"after", "before", "order", "limit"}
        )

        asc_order = order == "asc"
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
