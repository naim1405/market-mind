import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.messages.models import MessageRole
from app.modules.messages.repositories import MessageRepository

pytestmark = pytest.mark.anyio


async def test_recent_messages_oldest_first_within_one_transaction(db_session, customer):
    repo = MessageRepository(db_session)
    for i in range(5):
        role = MessageRole.USER if i % 2 == 0 else MessageRole.MODEL
        await repo.create_message(customer.id, role, f"msg {i}")

    history = await repo.get_recent_messages(customer.id, limit=3)

    assert [m.content for m in history] == ["msg 2", "msg 3", "msg 4"]
    assert history[0].role == MessageRole.USER


async def test_message_exists_by_mid(db_session, customer):
    repo = MessageRepository(db_session)
    await repo.create_message(customer.id, MessageRole.USER, "hi", mid="m_1")

    assert await repo.message_exists("m_1") is True
    assert await repo.message_exists("m_2") is False


async def test_duplicate_mid_rejected(db_session, customer):
    repo = MessageRepository(db_session)
    await repo.create_message(customer.id, MessageRole.USER, "hi", mid="m_1")
    with pytest.raises(IntegrityError):
        await repo.create_message(customer.id, MessageRole.USER, "hi", mid="m_1")
