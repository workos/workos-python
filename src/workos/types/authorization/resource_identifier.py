from typing import Union

from typing_extensions import TypedDict


class ParentResourceIdentifierById(TypedDict):
    parent_resource_id: str


class ParentResourceIdentifierByExternalId(TypedDict):
    parent_resource_type_slug: str
    parent_resource_external_id: str


ParentResourceIdentifier = Union[
    ParentResourceIdentifierById, ParentResourceIdentifierByExternalId
]
