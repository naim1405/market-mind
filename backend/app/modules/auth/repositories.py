from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import Auth


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def upsert_tokens(
        self,
        access_token: str,
        refresh_token: str | None,
        user_id: UUID,
    ) -> Auth:
        token = Auth(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        self.db_session.add(token)

        return token
