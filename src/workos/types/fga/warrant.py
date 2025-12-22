from typing import Literal, Mapping, Optional, Any
from typing_extensions import TypedDict

from workos.types.workos_model import WorkOSModel


class SubjectInput(TypedDict, total=False):
    resource_type: str
    resource_id: str
    relation: Optional[str]


class Subject(WorkOSModel):
    resource_type: str
    resource_id: str
    relation: Optional[str] = None


class Warrant(WorkOSModel):
    resource_type: str
    resource_id: str
    relation: str
    subject: Subject
    policy: Optional[str] = None


class WriteWarrantResponse(WorkOSModel):
    warrant_token: str


WarrantWriteOperation = Literal["create", "delete"]


class WarrantWrite(TypedDict, total=False):
    op: WarrantWriteOperation
    resource_type: str
    resource_id: str
    relation: str
    subject: SubjectInput
    policy: Optional[str]


class WarrantQueryResult(WorkOSModel):
    resource_type: str
    resource_id: str
    relation: str
    warrant: Warrant
    is_implicit: bool
    meta: Optional[Mapping[str, Any]] = None
