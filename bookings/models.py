from sqlalchemy import Integer, String, DateTime, ForeignKey, Date, Float, Enum as SQLEnum
from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import BaseModel
import uuid
import enum


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class Booking(BaseModel):
    __tablename__ = "bookings"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    destination_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("destinations.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    travelers_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(SQLEnum(BookingStatus), nullable=False, default=BookingStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    destination: Mapped["Destination"] = relationship("Destination", back_populates="bookings")
    payment: Mapped["Payment"] = relationship("Payment", back_populates="booking", uselist=False)
