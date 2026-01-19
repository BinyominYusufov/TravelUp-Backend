from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import BaseModel
import uuid

class Review(BaseModel):
    __tablename__ = "reviews"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    destination_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("destinations.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    destination: Mapped["Destination"] = relationship("Destination", back_populates="reviews")
