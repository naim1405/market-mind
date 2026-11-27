from typing import Annotated

from fastapi import Depends

from app.db.session import SessionDep
from app.modules.messages.repositories import MessageRepository


def get_message_repository(session: SessionDep) -> MessageRepository:
    return MessageRepository(session=session)


MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]
