from typing import Any, Literal, Mapping, Optional, Sequence, TypedDict

from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped

from .warrant import Subject, SubjectInput

CheckOperation = Literal["any_of", "all_of", "batch"]


class WarrantCheckInput(TypedDict, total=False):
    resource_type: str
    resource_id: str
    relation: str
    subject: SubjectInput
    context: Optional[Mapping[str, Any]]


class WarrantCheck(WorkOSModel):
    resource_type: str
    resource_id: str
    relation: str
    subject: Subject
    context: Optional[Mapping[str, Any]] = None


class DecisionTreeNode(WorkOSModel):
    check: WarrantCheck
    decision: str
    processing_time: int
    children: Optional[Sequence["DecisionTreeNode"]] = None
    policy: Optional[str] = None


class DebugInfo(WorkOSModel):
    processing_time: int
    decision_tree: DecisionTreeNode


CheckResult = Literal["authorized", "not_authorized"]


class CheckResponse(WorkOSModel):
    result: LiteralOrUntyped[CheckResult]
    is_implicit: bool
    debug_info: Optional[DebugInfo] = None

    def authorized(self) -> bool:
        return self.result == "authorized"
