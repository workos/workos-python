from typing import Optional, List
from enum import Enum
from workos.utils.types import JsonDict


class DirectoryUserRole:
    def __init__(self, attributes: JsonDict) -> None:
        self.slug: str = attributes["slug"]


class DirectoryUserEmail:
    def __init__(self, attributes: JsonDict) -> None:
        self.type: Optional[str] = attributes.get("type")
        self.value: Optional[str] = attributes.get("value")
        self.primary: Optional[bool] = attributes.get("primary")


class DirectoryUserState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class DirectoryUserEvent:
    def __init__(self, attributes) -> None:
        self.id: str = attributes["id"]
        self.name: str = attributes["name"]
        self.idp_id: str = attributes["idp_id"]
        self.directory_id: str = attributes["directory_id"]
        self.organization_id: str = attributes["organization_id"]
        self.first_name: Optional[str] = attributes.get("first_name")
        self.last_name: Optional[str] = attributes.get("last_name")
        self.job_title: Optional[str] = attributes.get("job_title")
        self.emails: List[DirectoryUserEmail] = []
        for email in attributes.get("emails"):
            self.emails.push(DirectoryUserEmail(email))
        self.username: Optional[str] = attributes.get("username")
        self.state: DirectoryUserState = DirectoryUserState(attributes["state"])
        self.custom_attributes: JsonDict = attributes.get("custom_attributes", {})
        self.raw_attributes: JsonDict = attributes.get("raw_attributes", {})
        self.created_at: str = attributes["created_at"]
        self.updated_at: str = attributes["updated_at"]
        self.role: Optional[DirectoryUserRole] = (
            DirectoryUserRole(attributes["role"]) if attributes.get("role") else None
        )
        self.previous_attributes: JsonDict = attributes.get("previous_attributes", {})
        # always 'directory_user' for this event
        self.object: str = attributes["object"]


class DirectoryUserCreatedEvent:
    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.event: str = "dsync.user.created"
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryUserEvent = DirectoryUserEvent(attributes["data"])


class DirectoryUserDeletedEvent:
    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.event: str = "dsync.user.deleted"
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryUserEvent = DirectoryUserEvent(attributes["data"])


class DirectoryUserUpdatedEvent:
    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.event: str = "dsync.user.updated"
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryUserEvent = DirectoryUserEvent(attributes["data"])
