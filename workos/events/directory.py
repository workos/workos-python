from typing import Dict, Any, List
from enum import Enum

JsonDict = Dict[str, Any]


class DirectoryType(Enum):
    AZURE_SCIM_v2 = "azure scim v2.0"
    BAMBOO_HR = "bamboohr"
    BREATHE_HR = "breathe hr"
    CEZANNE_HR = "cezanne hr"
    CYBERARK_SCIM_v2 = "cyperark scim v2.0"
    FOURTH_HR = "fourth hr"
    GENERIC_SCIM_v2 = "generic scim v2.0"
    GOOGLE = "gsuite directory"
    GUSTO = "gusto"
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


class OrganizationDomain:
    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.domain: str = attributes["domain"]


class DirectoryActivatedEvent:
    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.name: str = attributes["name"]
        self.type: DirectoryType = DirectoryType(attributes["type"])
        self.state: DirectoryState = DirectoryState.ACTIVE
        self.domains: List[OrganizationDomain] = []
        for domain in attributes["domains"]:
            self.domains.push(OrganizationDomain(domain))
        self.organization_id: str = attributes["organization_id"]
        self.created_at: str = attributes["created_at"]
        self.updated_at: str = attributes["updated_at"]
        self.external_key: str = attributes["external_key"]
        # always 'directory' for this event
        self.object: str = attributes["object"]


class DirectoryDeletedEvent:
    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.name: str = attributes["name"]
        self.type: DirectoryType = DirectoryType(attributes["type"])
        self.state: DirectoryState = DirectoryState.DELETING
        self.domains: List[OrganizationDomain] = []
        for domain in attributes["domains"]:
            self.domains.push(OrganizationDomain(domain))
        self.organization_id: str = attributes["organization_id"]
        self.created_at: str = attributes["created_at"]
        self.updated_at: str = attributes["updated_at"]
        self.external_key: str = attributes["external_key"]
        # always 'directory' for this event
        self.object: str = attributes["object"]
