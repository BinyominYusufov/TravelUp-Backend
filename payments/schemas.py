from pydantic import BaseModel, Field
from datetime import datetime


class PaymentCreateSchema(BaseModel):
    booking_id: int
    amount: float = Field(gt=0)
    currency: str = "USD"
    provider: str


class PaymentResponseSchema(BaseModel):
    id: int
    booking_id: int
    amount: float
    currency: str
    provider: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
