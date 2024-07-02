from typing import Literal
from workos.utils.types import JsonDict


class DirectoryGroupEvent:
    def __init__(self, attributes) -> None:
        self.id: str = attributes["id"]
        self.name: str = attributes["name"]
        self.idp_id: str = attributes["idp_id"]
        self.directory_id: str = attributes["directory_id"]
        self.organization_id: str = attributes["organization_id"]
        self.created_at: str = attributes["created_at"]
        self.updated_at: str = attributes["updated_at"]
        self.raw_attributes: JsonDict = attributes.get("raw_attributes", {})
        self.previous_attributes: JsonDict = attributes.get("previous_attributes", {})
        self.object: Literal["directory_group"] = attributes["object"]


class DirectoryGroupCreatedEvent:
    event_name = "dsync.group.created"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: str = attributes["event"]
        self.id: str = attributes["id"]
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryGroupEvent = DirectoryGroupEvent(attributes["data"])


class DirectoryGroupDeletedEvent:
    event_name = "dsync.group.deleted"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: str = attributes["event"]
        self.id: str = attributes["id"]
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryGroupEvent = DirectoryGroupEvent(attributes["data"])


class DirectoryGroupUpdatedEvent:
    event_name = "dsync.group.updated"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: str = attributes["event"]
        self.id: str = attributes["id"]
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryGroupEvent = DirectoryGroupEvent(attributes["data"])
