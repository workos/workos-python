from typing import Union

from typing_extensions import TypedDict


class ResourceIdentifierById(TypedDict):
    resource_id: str


class ResourceIdentifierByExternalId(TypedDict):
    resource_external_id: str
    resource_type_slug: str


ResourceIdentifier = Union[ResourceIdentifierById, ResourceIdentifierByExternalId]
