from typing_extensions import TypeIs
from pydantic import BaseModel, Field, TypeAdapter, ValidationError, ValidationInfo, ValidatorFunctionWrapHandler, WrapValidator
from typing import Annotated, Any, List, LiteralString, Optional, Literal, TypeVar, Union
from enum import Enum

DirectoryType = Literal[
    "azure scim v2.0",
    "bamboohr",
    "breathe hr",
    "cezanne hr",
    "cyperark scim v2.0",
    "fourth hr",
    "generic scim v2.0",
    # TODO: Re-enable. Temp disabling for unknown enum testing.
    # "gsuite directory",
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

# This approach works, but it has some downsides:
# - If the rest of the values are literals, this is a different type of object,
#   it can't just be treated as a string. Maybe that's OK?
# - If you serialize the object, it be a dictionary {raw_value: "foo"} rathe than just a string
# - I wonder if we can do something sneaky like create a custom type guard that considers any
#   string literal that looks like "untyped[FOO]" to be an untyped value and we just return a string
#  if validation fails. The downside there is the return type of all of our literals will look like
#   Literal["a", "b"]  | str
# - Can we do something better if we use enums rather than string literals?


class UntypedValue(BaseModel):
    raw_value: Any


def is_untyped_value(value: Any) -> TypeIs[UntypedValue]:
    return isinstance(value, UntypedValue)


def convert_unknown_enum_to_untyped(
    value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> int:
    try:
        return handler(value)
    except ValidationError as validation_error:
        if validation_error.errors()[0]['type'] == 'literal_error':
            return handler(UntypedValue(raw_value=value))
        else:
            return handler(value)


LiteralType = TypeVar('LiteralType', bound='LiteralString')
SafeLiteral = Annotated[Annotated[Union[LiteralType, UntypedValue], Field(
    union_mode='left_to_right')], WrapValidator(convert_unknown_enum_to_untyped)]

# Should this be WorkOSDirectory?


class Directory(BaseModel):
    """Representation of a Directory Response as returned by WorkOS through the Directory Sync feature.
    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSConnection is comprised of.
    """
    id: str
    object: Literal["directory"]
    domain: Optional[str] = None
    name: str
    organization_id: str
    state: SafeLiteral[DirectoryState]
    # state: DirectoryState
    type: SafeLiteral[DirectoryType]
    # type: DirectoryType
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
class DirectoryGroup(BaseModel):
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

# Should this be WorkOSDirectoryUser?


class DirectoryUser(BaseModel):
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
