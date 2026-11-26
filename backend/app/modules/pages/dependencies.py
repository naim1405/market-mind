from typing import Annotated

from app.modules.pages.repositories import PagesRepository
from fastapi import Depends

from app.db.session import SessionDep


def get_pages_repository(session: SessionDep) -> PagesRepository:
    return PagesRepository(session=session)


PagesRepositoryDep = Annotated[PagesRepository, Depends(get_pages_repository)]


def get_pages_service(
    pages_repo: PagesRepositoryDep,
) -> PagesRepository:
    return PagesRepository(session=pages_repo.db_session)


PagesServiceDep = Annotated[PagesRepository, Depends(get_pages_service)]
