from typing import Protocol, Sequence
from workos.types.widgets.widget_scope import WidgetScope
from workos.types.widgets.widget_token_response import WidgetTokenResponse
from workos.utils.http_client import SyncHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_POST


WIDGETS_GENERATE_TOKEN_PATH = "widgets/token"


class WidgetsModule(Protocol):
    def get_token(
        self,
        *,
        organization_id: str,
        user_id: str,
        scopes: Sequence[WidgetScope],
    ) -> WidgetTokenResponse:
        """Generate a new widget token for the specified organization and user with the provided scopes.

        Kwargs:
            organization_id (str): The ID of the organization the widget token will be generated for.
            user_id (str): The ID of the AuthKit user the widget token will be generated for.
            scopes (Sequence[WidgetScope]): The widget scopes for the generated widget token.

        Returns:
            WidgetTokenResponse: WidgetTokenResponse object with token string.
        """
        ...


class Widgets(WidgetsModule):

    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def get_token(
        self,
        *,
        organization_id: str,
        user_id: str,
        scopes: Sequence[WidgetScope],
    ) -> WidgetTokenResponse:
        json = {
            "organization_id": organization_id,
            "user_id": user_id,
            "scopes": scopes,
        }
        response = self._http_client.request(
            WIDGETS_GENERATE_TOKEN_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return WidgetTokenResponse.model_validate(response)
