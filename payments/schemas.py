from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class PaymentCreateSchema(BaseModel):
    booking_id: uuid.UUID
    amount: float = Field(gt=0)
    currency: str = "USD"
    provider: str


class PaymentResponseSchema(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    amount: float
    currency: str
    provider: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
