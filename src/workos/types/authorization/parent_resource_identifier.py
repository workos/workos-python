from typing import Union

from typing_extensions import TypedDict


class ParentResourceById(TypedDict):
    parent_resource_id: str


class ParentResourceByExternalId(TypedDict):
    parent_resource_external_id: str
    parent_resource_type_slug: str


ParentResourceIdentifier = Union[ParentResourceById, ParentResourceByExternalId]
