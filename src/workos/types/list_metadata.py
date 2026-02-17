from pydantic import BaseModel
from typing import Optional


class ListAfterMetadata(BaseModel):
    after: Optional[str] = None


class ListMetadata(ListAfterMetadata):
    before: Optional[str] = None
