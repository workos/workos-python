from typing import List, Optional
from enum import Enum

from workos.types.user_management.impersonator import Impersonator
from workos.types.user_management.user import User
from workos.types.workos_model import WorkOSModel

class AuthenticateWithSessionCookieFailureReason(Enum):
    INVALID_JWT = 'invalid_jwt'
    INVALID_SESSION_COOKIE = 'invalid_session_cookie'
    NO_SESSION_COOKIE_PROVIDED = 'no_session_cookie_provided'

class AuthenticateWithSessionCookieSuccessResponse(WorkOSModel):
    authenticated: bool = True
    sessionId: str
    organizationId: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    user: User
    impersonator: Optional[Impersonator] = None

class AuthenticateWithSessionCookieErrorResponse(WorkOSModel):
    authenticated: bool = False
    reason: AuthenticateWithSessionCookieFailureReason

