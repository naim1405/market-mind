import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.messages.models import Message, MessageRole


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def create_message(
        self,
        customer_id: uuid.UUID,
        role: MessageRole,
        content: str,
        mid: str | None = None,
    ) -> Message:
        message = Message(customer_id=customer_id, role=role, content=content, mid=mid)
        self.db_session.add(message)
        await self.db_session.flush()
        return message

    async def message_exists(self, mid: str) -> bool:
        stmt = select(Message.id).where(Message.mid == mid)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none() is not None

    # last `limit` messages, oldest first, ready to send to the model as history
    async def get_recent_messages(
        self, customer_id: uuid.UUID, limit: int = 20
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.customer_id == customer_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.db_session.execute(stmt)
        return list(reversed(result.scalars().all()))
