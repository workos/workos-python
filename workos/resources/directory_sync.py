from pydantic import BaseModel
from typing import List,  Optional, Literal
from enum import Enum
from workos.typing.enums import EnumOrUntyped
from workos.typing.literals import LiteralOrUntyped


class DirectoryType(str, Enum):
    AZURE_SCIM_v2 = "azure scim v2.0"
    BAMBOO_HR = "bamboohr"
    BREATHE_HR = "breathe hr"
    CEZANNE_HR = "cezanne hr"
    CYBERARK_SCIM_v2 = "cyperark scim v2.0"
    FOURTH_HR = "fourth hr"
    GENERIC_SCIM_v2 = "generic scim v2.0"
    GOOGLE = "gsuite directory"
    HIBOB = "hibob"
    JUMPCLOUD_SCIM_v2 = "jump cloud scim v2.0"
    OKTA_SCIM_v2 = "okta scim v2.0"
    ONELOGIN_SCIM_v2 = "onelogin scim v2.0"
    PEOPLE_HR = "people hr"
    PERSONIO = "personio"
    PINGFEDERATE_SCIM_v2 = "pingfederate scim v2.0"
    RIPPLING_SCIM_v2 = "rippling v2.0"
    SFTP = "sftp"
    SFTP_WORKDAY = "sftp workday"
    WORKDAY = "workday"


class DirectoryState(str, Enum):
    ACTIVE = "linked"
    UNLINKED = "unlinked"
    VALIDATING = "validating"
    DELETING = "deleting"
    INVALID_CREDENTIALS = "invalid_credentials"


class Directory(BaseModel):
    # Should this be WorkOSDirectory?
    """Representation of a Directory Response as returned by WorkOS through the Directory Sync feature.
    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSConnection is comprised of.
    """
    id: str
    object: Literal["directory"]
    domain: Optional[str] = None
    name: str
    organization_id: str
    # Toying around with the differences in type hinting or deserialization for enums vs literals. In the end pretty equivalent,
    # it's a question of whether we want to present strings or DirectoryState.ACTIVE to the user
    # leaving both options here for now until we settle on a preference
    state: LiteralOrUntyped[Literal[
        'linked',
        "unlinked",
        "validating",
        "deleting",
        "invalid_credentials",
    ]]
    # state: EnumOrUntyped[Literal[
    #     DirectoryState.ACTIVE,
    #     DirectoryState.UNLINKED,
    #     DirectoryState.VALIDATING,
    #     DirectoryState.DELETING,
    #     DirectoryState.INVALID_CREDENTIALS,
    # ]]
    type: LiteralOrUntyped[Literal[
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
    ]]
    # type: EnumOrUntyped[Literal[
    #     DirectoryType.AZURE_SCIM_v2,
    #     DirectoryType.BAMBOO_HR,
    #     DirectoryType.BREATHE_HR,
    #     DirectoryType.CEZANNE_HR,
    #     DirectoryType.CYBERARK_SCIM_v2,
    #     DirectoryType.FOURTH_HR,
    #     DirectoryType.GENERIC_SCIM_v2,
    #     DirectoryType.GOOGLE,
    #     DirectoryType.HIBOB,
    #     DirectoryType.JUMPCLOUD_SCIM_v2,
    #     DirectoryType.OKTA_SCIM_v2,
    #     DirectoryType.ONELOGIN_SCIM_v2,
    #     DirectoryType.PEOPLE_HR,
    #     DirectoryType.PERSONIO,
    #     DirectoryType.PINGFEDERATE_SCIM_v2,
    #     DirectoryType.RIPPLING_SCIM_v2,
    #     DirectoryType.SFTP,
    #     DirectoryType.SFTP_WORKDAY,
    #     DirectoryType.WORKDAY,
    # ]]
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


class DirectoryGroup(BaseModel):
    # Should this be WorkOSDirectoryGroup?
    """Representation of a Directory Group as returned by WorkOS through the Directory Sync feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSDirectoryGroup is comprised of.
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
        OBJECT_FIELDS (list): List of fields a WorkOSDirectoryUser is comprised of.
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
