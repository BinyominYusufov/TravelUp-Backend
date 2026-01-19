from sqlalchemy import String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from database import BaseModel
from bookings.models import Booking
from reviews.models import Review


class Destination(BaseModel):
    __tablename__ = "destinations"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    cover_image: Mapped[str | None] = mapped_column(String, nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    bookings:Mapped[list["Booking"]] = relationship("Booking", back_populates="destination")
    reviews:Mapped[list["Review"]] = relationship("Review", back_populates="destination")