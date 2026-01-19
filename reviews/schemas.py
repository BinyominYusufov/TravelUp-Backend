from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class ReviewCreateSchema(BaseModel):
    destination_id: uuid.UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewUpdateSchema(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewResponseSchema(BaseModel):
    id: uuid.UUID
    user_id: int
    destination_id: uuid.UUID
    rating: int
    comment: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True
