from typing import Optional, List, Literal
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
    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.idp_id: str = attributes["idp_id"]
        self.directory_id: str = attributes["directory_id"]
        self.organization_id: str = attributes["organization_id"]
        self.first_name: Optional[str] = attributes.get("first_name")
        self.last_name: Optional[str] = attributes.get("last_name")
        self.job_title: Optional[str] = attributes.get("job_title")

        self.emails: List[DirectoryUserEmail] = []
        for email in attributes.get("emails"):
            self.emails.append(DirectoryUserEmail(email))

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
        self.object: Literal["directory_user"] = attributes["object"]


class DirectoryUserCreatedEvent:
    event_name = "dsync.user.created"

    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.event: str = attributes["event"]
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryUserEvent = DirectoryUserEvent(attributes["data"])


class DirectoryUserDeletedEvent:
    event_name = "dsync.user.deleted"

    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.event: str = attributes["event"]
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryUserEvent = DirectoryUserEvent(attributes["data"])


class DirectoryUserUpdatedEvent:
    event_name = "dsync.user.updated"

    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.event: str = attributes["event"]
        self.created_at: str = attributes["created_at"]
        self.data: DirectoryUserEvent = DirectoryUserEvent(attributes["data"])
