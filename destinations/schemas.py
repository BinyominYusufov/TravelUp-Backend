from pydantic import BaseModel
from datetime import datetime


class DestinationCreateSchema(BaseModel):
    title: str
    description: str | None = None
    country: str
    city: str
    cover_image: str | None = None
    rating: float = 0.0


class DestinationUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    country: str | None = None
    city: str | None = None
    cover_image: str | None = None
    rating: float | None = None


class DestinationResponseSchema(BaseModel):
    id: int
    title: str
    description: str | None
    country: str
    city: str
    cover_image: str | None
    rating: float
    created_at: datetime
    
    class Config:
        from_attributes = True
