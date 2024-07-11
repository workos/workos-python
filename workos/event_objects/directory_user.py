from typing import Optional, List, Literal, TypedDict
from enum import Enum
from workos.utils.types import JsonDict
from role import WorkOSRole


class DirectoryUserState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class DirectoryUserEmail(TypedDict):
    type: Optional[str]
    value: Optional[str]
    primary: Optional[bool]

class WorkOSDirectoryUserEmail:
    type: Optional[str]
    value: Optional[str]
    primary: Optional[bool]

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryUserEmail:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryUserEvent(TypedDict):
    id: str
    idp_id: str
    directory_id: str
    organization_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    job_title: Optional[str]
    emails: List[DirectoryUserEmail]
    username: Optional[str]
    state: DirectoryUserState
    custom_attributes: JsonDict
    raw_attributes: JsonDict
    created_at: str
    updated_at: str
    role: Optional[WorkOSRole]
    previous_attributes: JsonDict
    object: Literal["directory_user"]

class WorkOSDirectoryUserEvent:
    id: str
    idp_id: str
    directory_id: str
    organization_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    job_title: Optional[str]
    emails: List[WorkOSDirectoryUserEmail]
    username: Optional[str]
    state: DirectoryUserState
    custom_attributes: JsonDict
    raw_attributes: JsonDict
    created_at: str
    updated_at: str
    role: Optional[WorkOSRole]
    previous_attributes: JsonDict
    object: Literal["directory_user"]

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == 'state':
                setattr(instance, k, DirectoryUserState(v))
            elif k == 'role':
                setattr(instance, k, WorkOSRole.construct_from_response(v))
            elif k == 'email':
                emails = []
                for email in v:
                    emails.append(WorkOSDirectoryUserEmail.construct_from_response(email))
                setattr(instance, k, emails)
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryUserEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"
    

class DirectoryUserCreatedEvent:
    id: str
    event: Literal["dsync.user.created"]
    created_at: str
    data: DirectoryUserEvent


class WorkOSDirectoryUserCreatedEvent:
    id: str
    event: Literal["dsync.user.created"]
    created_at: str
    data: WorkOSDirectoryUserEvent

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == 'data':
                setattr(instance, k, WorkOSDirectoryUserEvent.construct_from_response(v))
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryUserCreatedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryUserDeletedEvent:
    id: str
    event: Literal["dsync.user.deleted"]
    created_at: str
    data: DirectoryUserEvent


class WorkOSDirectoryUserDeletedEvent:
    id: str
    event: Literal["dsync.user.deleted"]
    created_at: str
    data: WorkOSDirectoryUserEvent

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == 'data':
                setattr(instance, k, WorkOSDirectoryUserEvent.construct_from_response(v))
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryUserDeletedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryUserUpdatedEvent:
    id: str
    event: Literal["dsync.user.updated"]
    created_at: str
    data: DirectoryUserEvent

class WorkOSDirectoryUserUpdatedEvent:
    id: str
    event: Literal["dsync.user.updated"]
    created_at: str
    data: WorkOSDirectoryUserEvent

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == 'data':
                setattr(instance, k, WorkOSDirectoryUserEvent.construct_from_response(v))
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryUserUpdatedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"
