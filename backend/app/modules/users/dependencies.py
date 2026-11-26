# import sql queries/repository, db session, make deps
from typing import Annotated

from fastapi import Depends

from app.db.session import SessionDep
from app.modules.users.repositories import UserRepository
from app.modules.users.services import UserService


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session=session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_user_service(repo: UserRepositoryDep) -> UserService:
    return UserService(repo=repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
