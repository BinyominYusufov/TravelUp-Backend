from pydantic import BaseModel, Field
from datetime import datetime, date
import uuid
from enum import Enum


class BookingStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class BookingCreateSchema(BaseModel):
    destination_id: uuid.UUID
    start_date: date
    end_date: date
    travelers_count: int = Field(gt=0)
    total_price: float = Field(gt=0)


class BookingUpdateStatusSchema(BaseModel):
    status: BookingStatusEnum


class BookingResponseSchema(BaseModel):
    id: uuid.UUID
    user_id: int
    destination_id: uuid.UUID
    start_date: date
    end_date: date
    travelers_count: int
    total_price: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
