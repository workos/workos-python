from typing import Any, Dict
from typing_extensions import override
from pydantic import BaseModel


class WorkOSModel(BaseModel):
    @override
    def dict(self) -> Dict[str, Any]:
        return self.model_dump()
