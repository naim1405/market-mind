from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.pages.models import Pages
from app.modules.pages.schemas import PageCreate


class PagesRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    # upsert page
    async def upsert_page(self, page_data: PageCreate):
        stmt = (
            insert(Pages)
            .values(
                name=page_data.name,
                facebook_id=page_data.facebook_id,
                access_token=page_data.access_token,
                user_id=page_data.user_id,
            )
            .on_conflict_do_update(
                index_elements=[Pages.facebook_id],
                set_={
                    "name": page_data.name,
                    "facebook_id": page_data.facebook_id,
                    "access_token": page_data.access_token,
                    "user_id": page_data.user_id,
                },
            )
            .returning(Pages)
        )

        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    # TODO:
    # - get page by id
    # - get products
    # - get access_token
    # -
