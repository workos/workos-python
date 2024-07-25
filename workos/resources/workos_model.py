from typing_extensions import override
from pydantic import BaseModel


class WorkOSModel(BaseModel):
    @override
    def dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias=False,
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=False
    ):
        return self.model_dump(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
