from typing import Annotated

from fastapi import Depends

from app.modules.facebook.dependencies import FacebookClientDep
from app.modules.facebook.webhook.services import WebhookService
from app.modules.pages.dependencies import PagesRepositoryDep


def get_webhook_service(
    facebook_client: FacebookClientDep,
    pages_repo: PagesRepositoryDep,
) -> WebhookService:
    return WebhookService(
        facebook_client=facebook_client,
        pages_repo=pages_repo,
    )


WebhookServiceDep = Annotated[WebhookService, Depends(get_webhook_service)]
