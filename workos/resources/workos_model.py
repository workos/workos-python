from typing import Any, Dict, override
from pydantic import BaseModel


class WorkOSModel(BaseModel):
    @override
    def dict(self) -> Dict[str, Any]:
        return self.model_dump()
