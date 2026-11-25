# handle application logic
import uuid
from urllib.parse import urlencode

from app.core.config import get_settings
from app.modules.facebook.client import FacebookClient


class AuthService:
    def __init__(self, repo, facebook_client:FacebookClient):
        self.facebook_client = facebook_client

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
        result = await self.facebook_client.verify_code(code)

        print('🚀 handling code : ', result)



