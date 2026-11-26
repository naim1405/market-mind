# import sql queries/repository, db session, make deps
from typing import Annotated

from fastapi import Depends

from app.db.session import SessionDep
from app.modules.auth.repositories import AuthRepository
from app.modules.auth.services import AuthService
from app.modules.facebook.dependencies import FacebookClientDep
from app.modules.users.dependencies import UserRepositoryDep


def get_auth_repository(session:SessionDep) -> AuthRepository:
    return AuthRepository(session=session)

AuthRepositoryDep = Annotated[AuthRepository, Depends(get_auth_repository)]


def get_auth_service(
    auth_repo: AuthRepositoryDep,
    facebook_client: FacebookClientDep,
    user_repo: UserRepositoryDep,
) -> AuthService:
    return AuthService(
        auth_repo=auth_repo, facebook_client=facebook_client, user_repo=user_repo
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
