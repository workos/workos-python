# @oagen-ignore-file

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Type, cast


class WorkOSError(Exception):
    """Base error for all WorkOS errors."""

    message: str

    def __init__(self, message: str = "An error occurred") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class APIError(WorkOSError):
    """Base for errors from HTTP requests."""

    status_code: Optional[int]
    request_id: Optional[str]
    code: Optional[str]
    param: Optional[str]
    raw_body: Optional[str]
    request_url: Optional[str]
    request_method: Optional[str]
    response: Optional[Any]
    response_json: Optional[Mapping[str, Any]]
    error: Optional[str]
    errors: Optional[Any]
    error_description: Optional[str]

    def __init__(
        self,
        *args: Any,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        code: Optional[str] = None,
        param: Optional[str] = None,
        raw_body: Optional[str] = None,
        request_url: Optional[str] = None,
        request_method: Optional[str] = None,
        response: Optional[Any] = None,
        response_json: Optional[Mapping[str, Any]] = None,
        error: Optional[str] = None,
        errors: Optional[Any] = None,
        error_description: Optional[str] = None,
    ) -> None:
        message: Optional[str] = None
        if args:
            first = args[0]
            if isinstance(first, str):
                message = first
            else:
                response = first
                if len(args) > 1:
                    response_json = cast(Optional[Mapping[str, Any]], args[1])
        if response is not None and status_code is None:
            status_code = cast(Optional[int], getattr(response, "status_code", None))
        headers = getattr(response, "headers", None)
        if request_id is None and headers is not None:
            request_id = headers.get("X-Request-ID") or headers.get("x-request-id")
        if (
            request_url is None
            and response is not None
            and getattr(response, "request", None) is not None
        ):
            request_url = str(response.request.url)
        if (
            request_method is None
            and response is not None
            and getattr(response, "request", None) is not None
        ):
            request_method = response.request.method
        if response_json is not None:
            if message is None:
                message = str(response_json.get("message", "No message"))
            if error is None:
                error = cast(Optional[str], response_json.get("error"))
            if errors is None:
                errors = response_json.get("errors")
            if code is None:
                code = cast(Optional[str], response_json.get("code"))
            if error_description is None:
                error_description = cast(
                    Optional[str], response_json.get("error_description")
                )
            if param is None:
                param = cast(Optional[str], response_json.get("param"))
        if message is None:
            message = "No message"
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id
        self.code = code
        self.param = param
        self.raw_body = raw_body
        self.request_url = request_url
        self.request_method = request_method
        self.response = response
        self.response_json = response_json
        self.error = error
        self.errors = errors
        self.error_description = error_description

    def __str__(self) -> str:
        exception = f"(message={self.message}, request_id={self.request_id}"
        if self.response_json is not None:
            for key, value in self.response_json.items():
                if key != "message":
                    exception += f", {key}={value}"
        elif self.code is not None:
            exception += f", code={self.code}"
        return exception + ")"


class BadRequestError(APIError):
    """400 Bad Request."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("status_code", 400)
        super().__init__(*args, **kwargs)


class AuthenticationError(APIError):
    """401 Unauthorized."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("status_code", 401)
        super().__init__(*args, **kwargs)


class AuthorizationError(APIError):
    """403 Forbidden."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("status_code", 403)
        super().__init__(*args, **kwargs)


class AuthenticationFlowError(AuthorizationError):
    """Raised when authentication requires an additional step.

    All auth-flow 403 errors carry a pending_authentication_token that
    must be passed to the next step in the authentication flow.
    """

    pending_authentication_token: Optional[str]

    def __init__(
        self,
        *args: Any,
        pending_authentication_token: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        response_json = cast(Optional[Mapping[str, Any]], kwargs.get("response_json"))
        if pending_authentication_token is None and response_json is not None:
            pending_authentication_token = cast(
                Optional[str], response_json.get("pending_authentication_token")
            )
        super().__init__(*args, **kwargs)
        self.pending_authentication_token = pending_authentication_token


class EmailVerificationRequiredError(AuthenticationFlowError):
    """Raised when email verification is required before authentication."""

    email_verification_id: Optional[str]
    email: Optional[str]

    def __init__(
        self,
        *args: Any,
        email_verification_id: Optional[str] = None,
        email: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        response_json = cast(Optional[Mapping[str, Any]], kwargs.get("response_json"))
        if email_verification_id is None and response_json is not None:
            email_verification_id = cast(
                Optional[str], response_json.get("email_verification_id")
            )
        if email is None and response_json is not None:
            email = cast(Optional[str], response_json.get("email"))
        super().__init__(*args, **kwargs)
        self.email_verification_id = email_verification_id
        self.email = email


class MfaEnrollmentError(AuthenticationFlowError):
    """Raised when MFA enrollment is required."""

    user: Optional[Dict[str, Any]]

    def __init__(
        self, *args: Any, user: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> None:
        response_json = cast(Optional[Mapping[str, Any]], kwargs.get("response_json"))
        if user is None and response_json is not None:
            user = cast(Optional[Dict[str, Any]], response_json.get("user"))
        super().__init__(*args, **kwargs)
        self.user = user


class MfaChallengeError(AuthenticationFlowError):
    """Raised when an MFA challenge must be completed."""

    user: Optional[Dict[str, Any]]
    authentication_factors: Optional[List[Dict[str, Any]]]

    def __init__(
        self,
        *args: Any,
        user: Optional[Dict[str, Any]] = None,
        authentication_factors: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        response_json = cast(Optional[Mapping[str, Any]], kwargs.get("response_json"))
        if user is None and response_json is not None:
            user = cast(Optional[Dict[str, Any]], response_json.get("user"))
        if authentication_factors is None and response_json is not None:
            authentication_factors = cast(
                Optional[List[Dict[str, Any]]],
                response_json.get("authentication_factors"),
            )
        super().__init__(*args, **kwargs)
        self.user = user
        self.authentication_factors = authentication_factors


class OrganizationSelectionRequiredError(AuthenticationFlowError):
    """Raised when the user must select an organization."""

    user: Optional[Dict[str, Any]]
    organizations: Optional[List[Dict[str, Any]]]

    def __init__(
        self,
        *args: Any,
        user: Optional[Dict[str, Any]] = None,
        organizations: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        response_json = cast(Optional[Mapping[str, Any]], kwargs.get("response_json"))
        if user is None and response_json is not None:
            user = cast(Optional[Dict[str, Any]], response_json.get("user"))
        if organizations is None and response_json is not None:
            organizations = cast(
                Optional[List[Dict[str, Any]]], response_json.get("organizations")
            )
        super().__init__(*args, **kwargs)
        self.user = user
        self.organizations = organizations


class SsoRequiredError(AuthenticationFlowError):
    """Raised when SSO authentication is required."""

    email: Optional[str]
    connection_ids: Optional[List[str]]

    def __init__(
        self,
        *args: Any,
        email: Optional[str] = None,
        connection_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        response_json = cast(Optional[Mapping[str, Any]], kwargs.get("response_json"))
        if email is None and response_json is not None:
            email = cast(Optional[str], response_json.get("email"))
        if connection_ids is None and response_json is not None:
            connection_ids = cast(
                Optional[List[str]], response_json.get("connection_ids")
            )
        super().__init__(*args, **kwargs)
        self.email = email
        self.connection_ids = connection_ids


class OrganizationAuthMethodsRequiredError(AuthenticationFlowError):
    """Raised when organization-specific authentication methods are required."""

    email: Optional[str]
    sso_connection_ids: Optional[List[str]]
    auth_methods: Optional[Dict[str, bool]]

    def __init__(
        self,
        *args: Any,
        email: Optional[str] = None,
        sso_connection_ids: Optional[List[str]] = None,
        auth_methods: Optional[Dict[str, bool]] = None,
        **kwargs: Any,
    ) -> None:
        response_json = cast(Optional[Mapping[str, Any]], kwargs.get("response_json"))
        if email is None and response_json is not None:
            email = cast(Optional[str], response_json.get("email"))
        if sso_connection_ids is None and response_json is not None:
            sso_connection_ids = cast(
                Optional[List[str]], response_json.get("sso_connection_ids")
            )
        if auth_methods is None and response_json is not None:
            auth_methods = cast(
                Optional[Dict[str, bool]], response_json.get("auth_methods")
            )
        super().__init__(*args, **kwargs)
        self.email = email
        self.sso_connection_ids = sso_connection_ids
        self.auth_methods = auth_methods


class AuthenticationMethodNotAllowedError(AuthenticationFlowError):
    """Raised when the authentication method is not allowed."""


class EmailPasswordAuthDisabledError(AuthenticationFlowError):
    """Raised when email/password authentication is disabled."""


class PasskeyProgressiveEnrollmentError(AuthenticationFlowError):
    """Raised when passkey progressive enrollment is required."""


class RadarChallengeError(AuthenticationFlowError):
    """Raised when a Radar challenge is required."""


class RadarSignUpChallengeError(AuthenticationFlowError):
    """Raised when a Radar sign-up challenge is required."""


class NotFoundError(APIError):
    """404 Not Found."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("status_code", 404)
        super().__init__(*args, **kwargs)


class ConflictError(APIError):
    """409 Conflict."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("status_code", 409)
        super().__init__(*args, **kwargs)


class UnprocessableEntityError(APIError):
    """422 Unprocessable Entity."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("status_code", 422)
        super().__init__(*args, **kwargs)


class RateLimitExceededError(APIError):
    """429 Rate Limited."""

    retry_after: Optional[float]

    def __init__(
        self, *args: Any, retry_after: Optional[float] = None, **kwargs: Any
    ) -> None:
        kwargs.setdefault("status_code", 429)
        super().__init__(*args, **kwargs)
        self.retry_after = retry_after


class ServerError(APIError):
    """500+ Server Error."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("status_code", 500)
        super().__init__(*args, **kwargs)


class ConfigurationError(WorkOSError):
    """Missing or invalid configuration. No request was made."""

    def __init__(self, message: str = "Configuration error") -> None:
        super().__init__(message)


class WorkOSConnectionError(WorkOSError):
    """Raised when the SDK cannot connect to the API (DNS failure, connection refused, etc.)."""

    def __init__(self, message: str = "Connection failed") -> None:
        super().__init__(message)


class WorkOSTimeoutError(WorkOSError):
    """Raised when the API request times out."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message)


STATUS_CODE_TO_ERROR: Dict[int, Type[APIError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: AuthorizationError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitExceededError,
}

# Maps authentication error code/error values to specific error classes.
# Checked by _raise_error() for 403 responses before falling through to AuthorizationError.
_AUTH_CODE_TO_ERROR: Dict[str, Type[AuthenticationFlowError]] = {
    "email_verification_required": EmailVerificationRequiredError,
    "mfa_enrollment": MfaEnrollmentError,
    "mfa_challenge": MfaChallengeError,
    "organization_selection_required": OrganizationSelectionRequiredError,
    "sso_required": SsoRequiredError,
    "organization_authentication_methods_required": OrganizationAuthMethodsRequiredError,
    "authentication_method_not_allowed": AuthenticationMethodNotAllowedError,
    "email_password_auth_disabled": EmailPasswordAuthDisabledError,
    "passkey_progressive_enrollment": PasskeyProgressiveEnrollmentError,
    "radar_challenge": RadarChallengeError,
    "radar_sign_up_challenge": RadarSignUpChallengeError,
}
