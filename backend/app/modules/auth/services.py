# handle application logic
import uuid
from urllib.parse import urlencode

from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token
from app.modules.auth.repositories import AuthRepository
from app.modules.facebook.client import FacebookClient
from app.modules.pages.repositories import PagesRepository
from app.modules.pages.schemas import PageCreate
from app.modules.users.repositories import UserRepository
from app.modules.users.schemas import UserCreate


class AuthService:
    def __init__(
        self,
        auth_repo: AuthRepository,
        facebook_client: FacebookClient,
        user_repo: UserRepository,
        pages_repo: PagesRepository,
    ):
        self.facebook_client = facebook_client
        self.auth_repo = auth_repo
        self.user_repo = user_repo
        self.pages_repo = pages_repo

    def hello_auth(self):
        return {"message": "Hello from AuthService"}

    def login_by_facebook(self):
        settings = get_settings()
        state = uuid.uuid4()
        requested_permissions = ','.join([
            'email',
            'public_profile',
            'pages_show_list',
            'pages_manage_metadata',
            'pages_messaging',
        ])

        params = {
            'client_id': settings.META_APP_ID,
            'redirect_uri': settings.META_REDIRECT_URI,
            'state': state,
            'response_type': 'code',
            'scope': requested_permissions,
        }

        redirect_url = (
            'https://www.facebook.com/v25.0/dialog/oauth?'
            + urlencode(params)
        )
        return redirect_url
    

    async def handle_facebook_callback(self, code):
        verified_code = await self.facebook_client.verify_code(code)
        access_token = verified_code.access_token
        user = await self.facebook_client.get_me(access_token)
        new_user = UserCreate(email=user.email, name=user.name, facebook_id=user.id)

        # upsert user
        result = await self.user_repo.upsert_user(new_user)
        # generate tokens
        access_token = create_access_token(result.id)
        refresh_token = create_refresh_token(result.id)

        # upsert pages with tokens
        await self.auth_repo.upsert_tokens(
            access_token=access_token, refresh_token=refresh_token, user_id=result.id
        )

        # subscribe to webhook
        for page in user.accounts.data:
            # call fb client to subscribe and upsert to page table
            # TODO: move subscribe to webhook to a background task
            await self.facebook_client.subscribe_to_page(
                page_id=page.id, page_access_token=page.access_token
            )
            # upsert page to db
            await self.pages_repo.upsert_page(
                PageCreate(
                    name=page.name,
                    facebook_id=page.id,
                    access_token=page.access_token,
                    user_id=result.id,
                )
            )

        return {
            "message": "Facebook callback handled successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
