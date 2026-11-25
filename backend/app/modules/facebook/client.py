import httpx

from app.core.config import get_settings
from app.modules.facebook.schemas import (
    FacebookAccountsSchema,
    FacebookCodeVerifyResponseSchema,
    FacebookPageSchema,
    FacebookUserSchema,
)

GRAPH_API_BASE = "https://graph.facebook.com/v25.0"


class FacebookClient:

    def __init__(self, http: httpx.AsyncClient):
        self.http = http

    async def graph_fetch(self, url: str, schema):
        response = await self.http.get(url)
        raw = response.json()

        response.raise_for_status()

        return schema.model_validate(raw)

    async def get_me(self, access_token: str):
        response = await self.http.get(
            f"{GRAPH_API_BASE}/me",
            params={
                "fields": "id,name,email,accounts",
                "access_token": access_token,
            },
        )

        response.raise_for_status()

        return FacebookUserSchema.model_validate(response.json())

    async def get_pages(self, access_token: str):
        response = await self.http.get(
            f"{GRAPH_API_BASE}/me",
            params={
                "fields": "accounts{id,name,access_token}",
                "access_token": access_token,
            },
        )

        response.raise_for_status()

        return FacebookAccountsSchema.model_validate(response.json())

    async def get_page(self, page_id: str, access_token: str):
        response = await self.http.get(
            f"{GRAPH_API_BASE}/{page_id}",
            params={
                "fields": "id,name,access_token",
                "access_token": access_token,
            },
        )

        response.raise_for_status()

        return FacebookPageSchema.model_validate(response.json())

    async def verify_code(self, code: str):
        print("🚀 verify_code : ", code)

        settings = get_settings()
        response = await self.http.get(
            f"{GRAPH_API_BASE}/oauth/access_token",
            params={
                "client_id": settings.META_APP_ID,
                "redirect_uri": settings.META_REDIRECT_URI,
                "client_secret": settings.META_APP_SECRET,
                "code": code,
            },
        )

        print("🚀 response  : ", response)

        response.raise_for_status()

        return FacebookCodeVerifyResponseSchema.model_validate(response.json())

    async def subscribe_to_page(
        self,
        page_id: str,
        page_access_token: str,
    ) -> bool:
        response = await self.http.post(
            f"{GRAPH_API_BASE}/{page_id}/subscribed_apps",
            params={
                "access_token": page_access_token,
                "subscribed_fields": "messages,messaging_postbacks",
            },
        )

        response.raise_for_status()

        return response.json().get("success") is True
