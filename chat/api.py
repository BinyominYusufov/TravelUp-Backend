from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Set
import json
from database import get_db, async_session
from .models import Chat, ChatMessage, ChatParticipant
from .schemas import (
    ChatCreateSchema,
    ChatResponseSchema,
    ChatMessageCreateSchema,
    ChatMessageResponseSchema
)
from .services import (
    create_chat,
    get_user_chats,
    get_chat_by_id,
    check_chat_access,
    create_message,
    get_chat_messages,
    delete_chat,
    delete_message,
    get_message_by_id
)
from accounts.handlers import get_current_user, decode_jwt, is_token_blocked
from accounts.models import User


chat_router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = set()
        self.active_connections[chat_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, chat_id: int):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].discard(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict, chat_id: int):
        if chat_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[chat_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            for connection in disconnected:
                self.disconnect(connection, chat_id)


manager = ConnectionManager()


async def get_user_from_token(token: str, db: AsyncSession) -> User | None:
    payload = decode_jwt(token)
    if not payload:
        return None
    
    if await is_token_blocked(token, db):
        return None
    
    result = await db.execute(
        select(User).where(User.id == payload["user_id"])
    )
    return result.scalar_one_or_none()


@chat_router.post("/chats", response_model=ChatResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_chat_endpoint(
    data: ChatCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await create_chat(data.user_ids, current_user.id, db)


@chat_router.get("/chats/my", response_model=list[ChatResponseSchema])
async def get_my_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await get_user_chats(current_user.id, db)


@chat_router.post("/chats/{chat_id}/messages", response_model=ChatMessageResponseSchema, status_code=status.HTTP_201_CREATED)
async def send_message(
    chat_id: int,
    data: ChatMessageCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    has_access = await check_chat_access(chat_id, current_user.id, current_user.is_admin, db)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    message = await create_message(chat_id, current_user.id, data, db)
    
    message_dict = {
        "id": message.id,
        "chat_id": message.chat_id,
        "sender_id": message.sender_id,
        "content": message.content,
        "created_at": message.created_at.isoformat()
    }
    
    await manager.broadcast(message_dict, chat_id)
    
    return message


@chat_router.get("/chats/{chat_id}/messages", response_model=list[ChatMessageResponseSchema])
async def get_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    has_access = await check_chat_access(chat_id, current_user.id, current_user.is_admin, db)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return await get_chat_messages(chat_id, db)


@chat_router.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_endpoint(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not current_user.is_admin:
        has_access = await check_chat_access(chat_id, current_user.id, False, db)
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied")
    
    await delete_chat(chat_id, db)


@chat_router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message_endpoint(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    message = await get_message_by_id(message_id, db)
    
    if not current_user.is_admin:
        if message.sender_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    await delete_message(message_id, db)


@chat_router.websocket("/ws/chats/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    token: str = Query(...),
):
    async with async_session() as db:
        try:
            user = await get_user_from_token(token, db)
            if not user:
                await websocket.close(code=1008, reason="Unauthorized")
                return
            
            has_access = await check_chat_access(chat_id, user.id, user.is_admin, db)
            if not has_access:
                await websocket.close(code=1008, reason="Access denied")
                return
            
            await manager.connect(websocket, chat_id)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    if "content" not in message_data:
                        await manager.send_personal_message(
                            {"error": "Content is required"},
                            websocket
                        )
                        continue
                    
                    create_schema = ChatMessageCreateSchema(content=message_data["content"])
                    message = await create_message(chat_id, user.id, create_schema, db)
                    
                    message_dict = {
                        "id": message.id,
                        "chat_id": message.chat_id,
                        "sender_id": message.sender_id,
                        "content": message.content,
                        "created_at": message.created_at.isoformat()
                    }
                    
                    await manager.broadcast(message_dict, chat_id)
            except WebSocketDisconnect:
                manager.disconnect(websocket, chat_id)
        except Exception as e:
            await websocket.close(code=1011, reason=str(e))
