from typing import Union

from typing_extensions import TypedDict


class ParentResourceIdentifierById(TypedDict):
    """Identify a parent resource by its WorkOS-assigned ID."""

    parent_resource_id: str


class ParentResourceIdentifierByExternalId(TypedDict):
    """Identify a parent resource by its external ID and resource type."""

    parent_resource_type_slug: str
    parent_resource_external_id: str


ParentResourceIdentifier = Union[
    ParentResourceIdentifierById, ParentResourceIdentifierByExternalId
]
