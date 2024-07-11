from typing import TypedDict


class Role(TypedDict):
    slug: str


class WorkOSRole:
    slug: str

    @classmethod
    def construct_from_response(cls, response: dict):
        instance = cls()
        for k, v in response.items():
            setattr(instance, k, v)

        return instance

    def to_dict(self) -> Role:
        return self.__dict__

    def __str__(self):
        return f"{self.__class__.__name__} {self.to_dict()}"
