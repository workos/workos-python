from typing import List, Literal, TypedDict
from enum import Enum


class DirectoryType(Enum):
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


class DirectoryState(Enum):
    ACTIVE = "active"
    DELETING = "deleting"


class OrganizationDomain(TypedDict):
    id: str
    domain: str


class WorkOSOrganizationDomain:
    id: str
    domain: str

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            setattr(instance, k, v)

        return instance

    def to_dict(self) -> OrganizationDomain:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryEventWithLegacyFields(TypedDict):
    id: str
    name: str
    type: DirectoryType
    state: DirectoryState
    domains: List[OrganizationDomain]
    organization_id: str
    created_at: str
    updated_at: str
    external_key: str
    object: Literal["directory"]


class WorkOSDirectoryEventWithLegacyFields:
    id: str
    name: str
    type: DirectoryType
    state: DirectoryState
    domains: List[WorkOSOrganizationDomain]
    organization_id: str
    created_at: str
    updated_at: str
    external_key: str
    object: Literal["directory"]

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "domains":
                domains = []
                for domain in v:
                    domains.append(
                        WorkOSOrganizationDomain.construct_from_response(domain)
                    )
                setattr(instance, k, domains)
            elif k == "type":
                setattr(instance, k, DirectoryType(v))
            elif k == "state":
                setattr(instance, k, DirectoryState(v))
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryEventWithLegacyFields:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryEvent:
    id: str
    name: str
    type: DirectoryType
    state: DirectoryState
    organization_id: str
    created_at: str
    updated_at: str
    object: Literal["directory"]


class WorkOSDirectoryEvent:
    id: str
    name: str
    type: DirectoryType
    state: DirectoryState
    organization_id: str
    created_at: str
    updated_at: str
    object: Literal["directory"]

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "type":
                setattr(instance, k, DirectoryType(v))
            elif k == "state":
                setattr(instance, k, DirectoryState(v))
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryActivatedEvent(TypedDict):
    event: str
    id: str
    created_at: str
    data: DirectoryEventWithLegacyFields


class WorkOSDirectoryActivatedEvent:
    event: Literal["dsync.activated"] = "dsync.activated"
    id: str
    created_at: str
    data: WorkOSDirectoryEventWithLegacyFields

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "data":
                setattr(
                    instance,
                    k,
                    WorkOSDirectoryEventWithLegacyFields.construct_from_response(v),
                )
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryActivatedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"


class DirectoryDeletedEvent:
    event: str
    id: str
    created_at: str
    state: DirectoryState
    data: DirectoryEvent


class WorkOSDirectoryDeletedEvent:
    event: Literal["dsync.deleted"] = "dsync.deleted"
    id: str
    created_at: str
    state: DirectoryState
    data: WorkOSDirectoryEvent

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            if k == "data":
                setattr(instance, k, WorkOSDirectoryEvent.construct_from_response(v))
            elif k == "state":
                setattr(instance, k, DirectoryState(v))
            else:
                setattr(instance, k, v)

        return instance

    def to_dict(self) -> DirectoryDeletedEvent:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"
