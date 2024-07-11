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


class DirectoryEvent:
    id: str
    name: str
    type: DirectoryType
    state: DirectoryState
    organization_id: str
    created_at: str
    updated_at: str
    object: Literal["directory"]


class DirectoryActivatedEvent(TypedDict):
    event: str
    id: str
    created_at: str
    data: DirectoryEventWithLegacyFields


class DirectoryDeletedEvent:
    event: str
    id: str
    created_at: str
    state: DirectoryState
    data: DirectoryEvent
