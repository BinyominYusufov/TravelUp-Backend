from sqlalchemy import String, DateTime, ForeignKey, Float, Enum as SQLEnum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import BaseModel
import uuid
import enum


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"


class Payment(BaseModel):
    __tablename__ = "payments"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bookings.id"), nullable=False, unique=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    provider: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    
    booking: Mapped["Booking"] = relationship("Booking", back_populates="payment")
