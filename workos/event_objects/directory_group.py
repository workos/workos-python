from typing import Literal, TypedDict
from workos.utils.types import JsonDict
from directory_user import DirectoryUserEventData, WorkOSDirectoryUserEventData


class DirectoryGroupEventData(TypedDict):
    id: str
    name: str
    idp_id: str
    directory_id: str
    organization_id: str
    created_at: str
    updated_at: str
    raw_attributes: JsonDict
    previous_attributes: JsonDict
    object: Literal["directory_group"]


class WorkOSDirectoryGroupEventData:
    id: str
    name: str
    idp_id: str
    directory_id: str
    organization_id: str
    created_at: str
    updated_at: str
    raw_attributes: JsonDict
    previous_attributes: JsonDict
    object: Literal["directory_group"]

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryGroupEventData:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryGroupCreatedEvent(TypedDict):
    event: Literal["dsync.activated"]
    id: str
    created_at: str
    data: DirectoryGroupEventData


class WorkOSDirectoryGroupCreatedEvent:
    event: Literal["dsync.activated"]
    id: str
    created_at: str
    data: WorkOSDirectoryGroupEventData

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "data":
                setattr(
                    instance,
                    k,
                    WorkOSDirectoryGroupEventData.construct_from_response(v),
                )
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryGroupCreatedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryGroupDeletedEvent(TypedDict):
    event: Literal["dsync.group.deleted"]
    id: str
    created_at: str
    data: DirectoryGroupEventData


class WorkOSDirectoryGroupDeletedEvent:
    event: Literal["dsync.group.deleted"]
    id: str
    created_at: str
    data: WorkOSDirectoryGroupEventData

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "data":
                setattr(
                    instance,
                    k,
                    WorkOSDirectoryGroupEventData.construct_from_response(v),
                )
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryGroupCreatedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryGroupUpdatedEvent(TypedDict):
    event: Literal["dsync.group.updated"]
    id: str
    created_at: str
    data: DirectoryGroupEventData


class WorkOSDirectoryGroupUpdatedEvent:
    event: Literal["dsync.group.updated"]
    id: str
    created_at: str
    data: WorkOSDirectoryGroupEventData

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "data":
                setattr(
                    instance,
                    k,
                    WorkOSDirectoryGroupEventData.construct_from_response(v),
                )
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryGroupUpdatedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryGroupMembershipEventData(TypedDict):
    directory_id: str
    user: DirectoryUserEventData
    group: DirectoryGroupEventData


class DirectoryGroupMembershipEventData:
    directory_id: str
    user: DirectoryUserEventData
    group: DirectoryGroupEventData

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "user":
                setattr(
                    instance,
                    k,
                    WorkOSDirectoryUserEventData.construct_from_response(v),
                )
            elif k == "group":
                setattr(
                    instance,
                    k,
                    WorkOSDirectoryGroupEventData.construct_from_response(v),
                )
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryGroupMembershipEventData:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryGroupUserAddedEvent(TypedDict):
    event: Literal["dsync.group.user_added"]
    id: str
    created_at: str
    data: DirectoryGroupMembershipEventData


class WorkOSDirectoryGroupUserAddedEvent:
    event: Literal["dsync.group.user_added"]
    id: str
    created_at: str
    data: DirectoryGroupMembershipEventData

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "data":
                setattr(
                    instance,
                    k,
                    DirectoryGroupMembershipEventData.construct_from_response(v),
                )
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryGroupUserAddedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryGroupUserRemovedEvent(TypedDict):
    event: Literal["dsync.group.user_removed"]
    id: str
    created_at: str
    data: DirectoryGroupMembershipEventData


class WorkOSDirectoryGroupUserRemovedEvent:
    event: Literal["dsync.group.user_removed"]
    id: str
    created_at: str
    data: DirectoryGroupMembershipEventData

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "data":
                setattr(
                    instance,
                    k,
                    DirectoryGroupMembershipEventData.construct_from_response(v),
                )
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryGroupUserRemovedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"
