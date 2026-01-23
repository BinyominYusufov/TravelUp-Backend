from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from .models import Chat, ChatParticipant, ChatMessage
from .schemas import ChatMessageCreateSchema
from accounts.models import User


async def create_chat(user_ids: list[int], creator_id: int, db: AsyncSession) -> Chat:
    all_user_ids = set(user_ids)
    all_user_ids.add(creator_id)
    
    result = await db.execute(
        select(User).where(User.id.in_(all_user_ids))
    )
    users = result.scalars().all()
    
    if len(users) != len(all_user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more users not found"
        )
    
    chat = Chat()
    db.add(chat)
    await db.flush()
    
    for user_id in all_user_ids:
        participant = ChatParticipant(
            chat_id=chat.id,
            user_id=user_id
        )
        db.add(participant)
    
    await db.commit()
    await db.refresh(chat)
    return chat


async def get_user_chats(user_id: int, db: AsyncSession) -> list[Chat]:
    result = await db.execute(
        select(Chat)
        .join(ChatParticipant)
        .where(ChatParticipant.user_id == user_id)
        .options(
            selectinload(Chat.participants),
            selectinload(Chat.messages)
        )
    )
    return list(result.scalars().all())


async def get_chat_by_id(chat_id: int, db: AsyncSession) -> Chat:
    result = await db.execute(
        select(Chat)
        .where(Chat.id == chat_id)
        .options(
            selectinload(Chat.participants),
            selectinload(Chat.messages)
        )
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return chat


async def check_chat_access(chat_id: int, user_id: int, is_admin: bool, db: AsyncSession) -> bool:
    if is_admin:
        return True
    
    result = await db.execute(
        select(ChatParticipant)
        .where(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id
        )
    )
    participant = result.scalar_one_or_none()
    return participant is not None


async def create_message(
    chat_id: int,
    sender_id: int,
    data: ChatMessageCreateSchema,
    db: AsyncSession
) -> ChatMessage:
    chat = await get_chat_by_id(chat_id, db)
    
    message = ChatMessage(
        chat_id=chat_id,
        sender_id=sender_id,
        content=data.content
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_chat_messages(chat_id: int, db: AsyncSession) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())


async def delete_chat(chat_id: int, db: AsyncSession) -> None:
    chat = await get_chat_by_id(chat_id, db)
    await db.delete(chat)
    await db.commit()


async def get_message_by_id(message_id: int, db: AsyncSession) -> ChatMessage:
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return message


async def delete_message(message_id: int, db: AsyncSession) -> None:
    message = await get_message_by_id(message_id, db)
    await db.delete(message)
    await db.commit()
