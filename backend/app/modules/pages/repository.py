from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.pages.models import Page
from app.modules.pages.schemas import PageCreate


class PageRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    # upsert page
    async def upsert_page(self, page_data: PageCreate):
        stmt = (
            insert(Page)
            .values(
                name=page_data.name,
                facebook_id=page_data.facebook_id,
                access_token=page_data.access_token,
            )
            .on_conflict_do_update(
                index_elements=[Page.facebook_id],
                set_={
                    "name": page_data.name,
                    "facebook_id": page_data.facebook_id,
                    "access_token": page_data.access_token,
                },
            )
            .returning(Page)
        )

        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    # TODO:
    # - get page by id
    # - get products
    # - get access_token
    # -
