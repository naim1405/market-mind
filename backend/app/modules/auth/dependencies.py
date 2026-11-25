# import sql queries/repository, db session, make deps
from typing import Annotated

from fastapi import Depends

from app.db.session import SessionDep
from app.modules.auth.repositories import AuthRepository
from app.modules.auth.services import AuthService
from app.modules.facebook.dependencies import FacebookClientDep


def get_auth_repository(session:SessionDep) -> AuthRepository:
    return AuthRepository(session=session)

AuthRepositoryDep = Annotated[AuthRepository, Depends(get_auth_repository)]


def get_auth_service(
    repo: AuthRepositoryDep, facebook_client: FacebookClientDep
) -> AuthService:
    return AuthService(repo=repo, facebook_client=facebook_client)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
