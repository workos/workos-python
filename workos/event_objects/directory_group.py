from typing import Literal, TypedDict
from workos.utils.types import JsonDict


class DirectoryGroupEvent(TypedDict):
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


class WorkOSDirectoryGroupEvent:
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

    def to_dict(self) -> DirectoryGroupEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryGroupCreatedEvent(TypedDict):
    event: Literal["dsync.activated"]
    id: str
    created_at: str
    data: DirectoryGroupEvent


class WorkOSDirectoryGroupCreatedEvent:
    event: Literal["dsync.activated"]
    id: str
    created_at: str
    data: WorkOSDirectoryGroupEvent

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "data":
                setattr(
                    instance, k, WorkOSDirectoryGroupEvent.construct_from_response(v)
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
    data: DirectoryGroupEvent


class WorkOSDirectoryGroupDeletedEvent:
    event: Literal["dsync.group.deleted"]
    id: str
    created_at: str
    data: WorkOSDirectoryGroupEvent

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "data":
                setattr(
                    instance, k, WorkOSDirectoryGroupEvent.construct_from_response(v)
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
    data: DirectoryGroupEvent


class WorkOSDirectoryGroupUpdatedEvent:
    event: Literal["dsync.group.updated"]
    id: str
    created_at: str
    data: WorkOSDirectoryGroupEvent

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "data":
                setattr(
                    instance, k, WorkOSDirectoryGroupEvent.construct_from_response(v)
                )
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryGroupUpdatedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"
