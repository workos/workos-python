from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from workos.types.workos_model import WorkOSModel

from .warrant import Subject


class CheckOperations(Enum):
    ANY_OF = "any_of"
    ALL_OF = "all_of"
    BATCH = "batch"


CheckOperation = Literal["any_of", "all_of", "batch"]


class WarrantCheck(WorkOSModel):
    resource_type: str
    resource_id: str
    relation: str
    subject: Subject
    context: Optional[Dict[str, Any]] = None


class DecisionTreeNode(WorkOSModel):
    check: WarrantCheck
    decision: str
    processing_time: int
    children: Optional[List["DecisionTreeNode"]] = None
    policy: Optional[str] = None


class DebugInfo(WorkOSModel):
    processing_time: int
    decision_tree: DecisionTreeNode


class CheckResults(Enum):
    AUTHORIZED = "authorized"
    NOT_AUTHORIZED = "not_authorized"


CheckResult = Literal["authorized", "not_authorized"]


class CheckResponse(WorkOSModel):
    result: CheckResult
    is_implicit: bool
    debug_info: Optional[DebugInfo] = None

    def authorized(self) -> bool:
        return self.result == CheckResults.AUTHORIZED.value
