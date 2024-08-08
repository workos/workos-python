from typing import Dict, Any, Optional

from workos.types.workos_model import WorkOSModel


class Resource(WorkOSModel):
    resource_type: str
    resource_id: str
    meta: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


class ResourceType(WorkOSModel):
    type: str
    relations: Dict[str, Any]
    created_at: Optional[str] = None


class BatchResourceUpdate(WorkOSModel):
    type: str
    relations: Dict[str, Any]


class Subject(WorkOSModel):
    subject_type: str
    subject_id: str


class Warrant(WorkOSModel):
    resource_type: str
    resource_id: str
    relation: str
    subject: Subject
    policy: Optional[str] = None


class WriteWarrantResponse(WorkOSModel):
    warrant_token: str
