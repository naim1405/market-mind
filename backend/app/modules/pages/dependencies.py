import uuid
from typing import Annotated

from fastapi import Depends

from app.db.session import SessionDep
from app.modules.pages.repositories import PagesRepository


def get_pages_repository(session: SessionDep) -> PagesRepository:
    return PagesRepository(session=session)


PagesRepositoryDep = Annotated[PagesRepository, Depends(get_pages_repository)]


def get_pages_service(
    pages_repo: PagesRepositoryDep,
) -> PagesRepository:
    return PagesRepository(session=pages_repo.db_session)


PagesServiceDep = Annotated[PagesRepository, Depends(get_pages_service)]


# TODO:
# shortcut: trusts the page_id from the path; later, depend on the JWT user here
# and check the page belongs to them. Every route using PageIdDep is covered then.
def get_page_id(page_id: uuid.UUID) -> uuid.UUID:
    return page_id


PageIdDep = Annotated[uuid.UUID, Depends(get_page_id)]
