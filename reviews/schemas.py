from pydantic import BaseModel, Field
from datetime import datetime


class ReviewCreateSchema(BaseModel):
    destination_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewUpdateSchema(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewResponseSchema(BaseModel):
    id: int
    user_id: int
    destination_id: int
    rating: int
    comment: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True
