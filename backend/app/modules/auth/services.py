# handle application logic
import uuid
from urllib.parse import urlencode

from app.core.config import get_settings
from app.modules.auth.repositories import AuthRepository
from app.modules.facebook.client import FacebookClient
from app.modules.users.repositories import UserRepository


class AuthService:
    def __init__(
        self,
        repo: AuthRepository,
        facebook_client: FacebookClient,
        user_repo: UserRepository,
    ):
        self.facebook_client = facebook_client
        self.auth_repo = repo
        self.user_repo = repo

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
        print("🚀 user  : ", user)
        # TODO:
        # - upsert user
        # - generate tokens
        # - upsert pages with tokens

        return {"message": "Facebook callback handled successfully", "user": user}
