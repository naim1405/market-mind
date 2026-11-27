from app.modules.facebook.client import FacebookClient
from app.modules.facebook.schemas import MessagingType
from app.modules.facebook.webhook.schemas import WebhookMessagingEventSchema
from app.modules.pages.repositories import PagesRepository


class WebhookService:
    def __init__(
        self,
        facebook_client: FacebookClient,
        pages_repo: PagesRepository,
    ):
        self.facebook_client = facebook_client
        self.pages_repo = pages_repo

    # reply to a message a customer sent to one of our pages
    async def reply_to_page_message(self, event: WebhookMessagingEventSchema):
        page = await self.pages_repo.get_page_by_facebook_id(event.recipient.id)
        if not page:
            # page is not connected to any user in our db
            return

        # TODO: generate a real reply
        reply_text = f"Thanks for your message! You said: {event.message.text}"

        await self.facebook_client.send_message(
            page_id=page.facebook_id,
            page_access_token=page.access_token,
            recipient_id=event.sender.id,
            message={"text": reply_text},
            messaging_type=MessagingType.RESPONSE,
        )
