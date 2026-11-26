from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def upsert_user(self, user: User):
        stmt = (
            insert(User)
            .values(
                email=user.email,
                name=user.name,
                is_active=True,
                facebook_id=user.facebook_id,
            )
            .on_conflict_do_update(
                index_elements=[User.facebook_id],
                set_={
                    "email": user.email,
                    "name": user.name,
                    "is_active": True,
                },
            )
            .returning(User)
        )

        result = await self.db_session.execute(stmt)

        return result.scalar_one()
