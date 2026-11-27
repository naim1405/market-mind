import httpx

from app.core.config import get_settings
from app.modules.facebook.schemas import (
    FacebookAccountsSchema,
    FacebookCodeVerifyResponseSchema,
    FacebookPageSchema,
    FacebookUserSchema,
    MessageTag,
    MessagingType,
)

GRAPH_API_BASE = "https://graph.facebook.com/v27.0"


class FacebookClient:

    def __init__(self, http: httpx.AsyncClient):
        self.http = http

    async def graph_fetch(
        self,
        url: str,
        params: dict,
        schema=None,
        method: str = "GET",
        json: dict | None = None,
    ):
        response = await self.http.request(
            method=method,
            url=url,
            params=params,
            json=json,
        )

        response.raise_for_status()

        raw = response.json()

        if schema:
            return schema.model_validate(raw)

        return raw

    async def get_me(self, access_token: str) -> FacebookUserSchema:
        result = await self.graph_fetch(
            url=f"{GRAPH_API_BASE}/me",
            params={
                "fields": "id,name,email,accounts",
                "access_token": access_token,
            },
            schema=FacebookUserSchema,
        )

        return result

    async def get_pages(self, access_token: str):
        return await self.graph_fetch(
            url=f"{GRAPH_API_BASE}/me",
            params={
                "fields": "accounts{id,name,access_token}",
                "access_token": access_token,
            },
            schema=FacebookAccountsSchema,
        )

    async def get_page(self, page_id: str, access_token: str):
        return await self.graph_fetch(
            url=f"{GRAPH_API_BASE}/{page_id}",
            params={
                "fields": "id,name,access_token",
                "access_token": access_token,
            },
            schema=FacebookPageSchema,
        )

    async def verify_code(self, code: str):
        settings = get_settings()

        response = await self.graph_fetch(
            url=f"{GRAPH_API_BASE}/oauth/access_token",
            params={
                "client_id": settings.META_APP_ID,
                "redirect_uri": settings.META_REDIRECT_URI,
                "client_secret": settings.META_APP_SECRET,
                "code": code,
            },
            schema=FacebookCodeVerifyResponseSchema,
        )

        if not response.access_token:
            raise ValueError("Access token not found in the response.")

        return response

    async def subscribe_to_page(
        self,
        page_id: str,
        page_access_token: str,
    ) -> bool:
        response = await self.graph_fetch(
            url=f"{GRAPH_API_BASE}/{page_id}/subscribed_apps",
            params={
                "access_token": page_access_token,
                "subscribed_fields": "messages,messaging_postbacks",
            },
            method="POST",
        )

        print("🚀 subscribe response  : ", response)

        return response.get("success") is True

    async def send_message(
        self,
        page_id: str,
        page_access_token: str,
        recipient_id: str,
        message: dict,
        messaging_type: MessagingType = MessagingType.RESPONSE,
        tag: MessageTag | None = None,
    ):
        """Send any Send API message: text, attachment, template, quick replies.

        `message` is the Send API `message` object, e.g. {"text": "hi"}.
        """
        if (messaging_type == MessagingType.MESSAGE_TAG) != (tag is not None):
            raise ValueError(
                "tag is required with MESSAGE_TAG and only allowed with it"
            )

        body = {
            "recipient": {"id": recipient_id},
            "messaging_type": messaging_type,
            "message": message,
        }
        if tag:
            body["tag"] = tag

        return await self.graph_fetch(
            url=f"{GRAPH_API_BASE}/{page_id}/messages",
            params={"access_token": page_access_token},
            json=body,
            method="POST",
        )
