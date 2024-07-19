from pydantic import BaseModel
from typing import List, Optional, Literal
from enum import Enum
from workos.typing.enums import EnumOrUntyped
from workos.typing.literals import LiteralOrUntyped

DirectoryState = Literal[
    "linked",
    "unlinked",
    "validating",
    "deleting",
    "invalid_credentials",
]

DirectoryType = Literal[
    "azure scim v2.0",
    "bamboohr",
    "breathe hr",
    "cezanne hr",
    "cyperark scim v2.0",
    "fourth hr",
    "generic scim v2.0",
    "gsuite directory",
    "hibob",
    "jump cloud scim v2.0",
    "okta scim v2.0",
    "onelogin scim v2.0",
    "people hr",
    "personio",
    "pingfederate scim v2.0",
    "rippling v2.0",
    "sftp",
    "sftp workday",
    "workday",
]


class Directory(BaseModel):
    # Should this be WorkOSDirectory?
    """Representation of a Directory Response as returned by WorkOS through the Directory Sync feature.
    Attributes:
        OBJECT_FIELDS (list): List of fields a Directory is comprised of.
    """
    id: str
    object: Literal["directory"]
    domain: Optional[str] = None
    name: str
    organization_id: str
    # Toying around with the differences in type hinting or deserialization for enums vs literals. In the end pretty equivalent,
    # it's a question of whether we want to present strings or DirectoryState.ACTIVE to the user
    # leaving both options here for now until we settle on a preference
    state: LiteralOrUntyped[DirectoryState]
    type: LiteralOrUntyped[DirectoryType]
    created_at: str
    updated_at: str


class DirectoryGroup(BaseModel):
    # Should this be WorkOSDirectoryGroup?
    """Representation of a Directory Group as returned by WorkOS through the Directory Sync feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a DirectoryGroup is comprised of.
    """
    id: str
    object: Literal["directory_group"]
    idp_id: str
    name: str
    directory_id: str
    organization_id: str
    raw_attributes: dict
    created_at: str
    updated_at: str
    # TODO: raw_attributes, yes or no?


class DirectoryUserEmail(BaseModel):
    type: Optional[str] = None
    value: Optional[str] = None
    primary: Optional[bool] = None


class Role(BaseModel):
    slug: str


DirectoryUserState = Literal["active", "inactive"]


class DirectoryUser(BaseModel):
    # Should this be WorkOSDirectoryUser?
    """Representation of a Directory User as returned by WorkOS through the Directory Sync feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a DirectoryUser is comprised of.
    """
    id: str
    object: Literal["directory_user"]
    idp_id: str
    directory_id: str
    organization_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    emails: List[DirectoryUserEmail]
    username: Optional[str] = None
    groups: List[DirectoryGroup]
    state: DirectoryUserState
    custom_attributes: dict
    raw_attributes: dict
    created_at: str
    updated_at: str
    role: Optional[Role] = None

    def primary_email(self):
        return next((email for email in self.emails if email.primary), None)
