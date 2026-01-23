from pydantic import BaseModel
from datetime import datetime
from typing import List


class ChatCreateSchema(BaseModel):
    user_ids: List[int]


class ChatResponseSchema(BaseModel):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessageCreateSchema(BaseModel):
    content: str


class ChatMessageResponseSchema(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
