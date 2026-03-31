"""WorkOS Python SDK."""

from ._client import AsyncWorkOS, WorkOS
from ._errors import (
    WorkOSError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ConfigurationError,
    ForbiddenError,
    NotFoundError,
    RateLimitExceededError,
    ServerError,
    UnprocessableEntityError,
    WorkOSConnectionError,
    WorkOSTimeoutError,
)
from ._pagination import AsyncPage, SyncPage
from ._types import RequestOptions

# Backward-compatible aliases
WorkOSClient = WorkOS
AsyncWorkOSClient = AsyncWorkOS

__all__ = [
    "AsyncWorkOS",
    "AsyncWorkOSClient",
    "WorkOS",
    "WorkOSClient",
    "RequestOptions",
    "WorkOSError",
    "AuthenticationError",
    "BadRequestError",
    "ConflictError",
    "ConfigurationError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitExceededError",
    "ServerError",
    "UnprocessableEntityError",
    "WorkOSConnectionError",
    "WorkOSTimeoutError",
    "AsyncPage",
    "SyncPage",
]
