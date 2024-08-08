from enum import Enum
from typing import Literal, Optional

from workos.types.workos_model import WorkOSModel


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


class WarrantWriteOperations(Enum):
    CREATE = "create"
    DELETE = "delete"


WarrantWriteOperation = Literal["create", "delete"]


class WarrantWrite(WorkOSModel):
    op: WarrantWriteOperation
    resource_type: str
    resource_id: str
    relation: str
    subject_type: str
    subject_id: str
    subject_relation: Optional[str] = None
    policy: Optional[str] = None
