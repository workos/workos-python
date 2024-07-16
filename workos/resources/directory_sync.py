from pydantic import BaseModel
from typing import List, Optional, Literal
from enum import Enum

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


DirectoryState = Literal[
    "linked",
    "unlinked",
    "validating",
    "deleting",
    "invalid_credentials",
]


# Should this be WorkOSDirectory?
"""Representation of a Directory Response as returned by WorkOS through the Directory Sync feature.
Attributes:
    OBJECT_FIELDS (list): List of fields a WorkOSConnection is comprised of.
"""


class Directory(BaseModel):
    id: str
    object: Literal["directory"]
    domain: Optional[str] = None
    name: str
    organization_id: str
    state: DirectoryState
    type: DirectoryType
    created_at: str
    updated_at: str


# class WorkOSDirectory(WorkOSBaseResource):
#     """Representation of a Directory Response as returned by WorkOS through the Directory Sync feature.
#     Attributes:
#         OBJECT_FIELDS (list): List of fields a WorkOSConnection is comprised of.
#     """

#     OBJECT_FIELDS = [
#         "object",
#         "id",
#         "domain",
#         "name",
#         "organization_id",
#         "state",
#         "type",
#         "created_at",
#         "updated_at",
#     ]

#     @classmethod
#     def construct_from_response(cls, response):
#         connection_response = super(WorkOSDirectory, cls).construct_from_response(
#             response
#         )

#         return connection_response

#     def to_dict(self):
#         connection_response_dict = super(WorkOSDirectory, self).to_dict()

#         return connection_response_dict


# Should this be WorkOSDirectoryGroup?
"""Representation of a Directory Group as returned by WorkOS through the Directory Sync feature.

Attributes:
    OBJECT_FIELDS (list): List of fields a WorkOSDirectoryGroup is comprised of.
"""


class DirectoryGroup(BaseModel):
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


# class WorkOSDirectoryGroup(WorkOSBaseResource):
#     """Representation of a Directory Group as returned by WorkOS through the Directory Sync feature.

#     Attributes:
#         OBJECT_FIELDS (list): List of fields a WorkOSDirectoryGroup is comprised of.
#     """

#     OBJECT_FIELDS = [
#         "id",
#         "idp_id",
#         "directory_id",
#         "name",
#         "created_at",
#         "updated_at",
#         "raw_attributes",
#         "object",
#     ]

#     @classmethod
#     def construct_from_response(cls, response):
#         return super(WorkOSDirectoryGroup, cls).construct_from_response(response)

#     def to_dict(self):
#         directory_group = super(WorkOSDirectoryGroup, self).to_dict()

#         return directory_group


class DirectoryUserEmail(BaseModel):
    type: Optional[str]
    value: Optional[str]
    primary: Optional[bool]


class Role(BaseModel):
    slug: str


DirectoryUserState = Literal["active", "inactive"]

# Should this be WorkOSDirectoryUser?
"""Representation of a Directory User as returned by WorkOS through the Directory Sync feature.

Attributes:
    OBJECT_FIELDS (list): List of fields a WorkOSDirectoryUser is comprised of.
"""


class DirectoryUser(BaseModel):
    id: str
    object: Literal["directory_user"]
    idp_id: str
    directory_id: str
    organization_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    job_title: Optional[str]
    emails: List[DirectoryUserEmail]
    username: Optional[str]
    # TODO: add groups
    state: DirectoryUserState
    custom_attributes: dict
    raw_attributes: dict
    created_at: str
    updated_at: str
    role: Optional[Role]


# class WorkOSDirectoryUser(WorkOSBaseResource):
#     """Representation of a Directory User as returned by WorkOS through the Directory Sync feature.

#     Attributes:
#         OBJECT_FIELDS (list): List of fields a WorkOSDirectoryUser is comprised of.
#     """

#     OBJECT_FIELDS = [
#         "id",
#         "idp_id",
#         "directory_id",
#         "organization_id",
#         "first_name",
#         "last_name",
#         "job_title",
#         "emails",
#         "username",
#         "groups",
#         "state",
#         "created_at",
#         "updated_at",
#         "custom_attributes",
#         "raw_attributes",
#         "object",
#         "role",  # [OPTIONAL]
#     ]

#     @classmethod
#     def construct_from_response(cls, response):
#         return super(WorkOSDirectoryUser, cls).construct_from_response(response)

#     def to_dict(self):
#         directory_group = super(WorkOSDirectoryUser, self).to_dict()

#         return directory_group

#     def primary_email(self):
#         self_dict = self.to_dict()
#         return next((email for email in self_dict["emails"] if email["primary"]), None)
