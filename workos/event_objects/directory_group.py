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
        # always 'directory_group' for this event
        self.object: str = attributes["object"]


class DirectoryGroupCreatedEvent:
    def __init__(self, attributes: JsonDict) -> None:
        self.event: str = "dsync.group.created"
        self.id: str = attributes["id"]
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryGroupEvent = DirectoryGroupEvent(attributes["data"])


class DirectoryGroupDeletedEvent:
    def __init__(self, attributes: JsonDict) -> None:
        self.event: str = "dsync.group.deleted"
        self.id: str = attributes["id"]
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryGroupEvent = DirectoryGroupEvent(attributes["data"])


class DirectoryGroupUpdatedEvent:
    def __init__(self, attributes: JsonDict) -> None:
        self.event: str = "dsync.group.updated"
        self.id: str = attributes["id"]
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryGroupEvent = DirectoryGroupEvent(attributes["data"])
