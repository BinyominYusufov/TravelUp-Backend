from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status
import uuid
from .models import Review
from .schemas import ReviewCreateSchema, ReviewUpdateSchema
from bookings.models import Booking


async def create_review(user_id: int, data: ReviewCreateSchema, db: AsyncSession) -> Review:
    booking_result = await db.execute(
        select(Booking).where(
            Booking.user_id == user_id,
            Booking.destination_id == data.destination_id
        )
    )
    booking = booking_result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review destinations you have booked"
        )
    
    existing_review_result = await db.execute(
        select(Review).where(
            Review.user_id == user_id,
            Review.destination_id == data.destination_id
        )
    )
    existing_review = existing_review_result.scalar_one_or_none()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this destination"
        )
    
    review = Review(
        user_id=user_id,
        destination_id=data.destination_id,
        rating=data.rating,
        comment=data.comment
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


async def get_destination_reviews(destination_id: uuid.UUID, db: AsyncSession) -> list[Review]:
    result = await db.execute(select(Review).where(Review.destination_id == destination_id))
    return list(result.scalars().all())


async def get_review_by_id(review_id: uuid.UUID, db: AsyncSession) -> Review:
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review


async def update_review(review_id: uuid.UUID, user_id: int, data: ReviewUpdateSchema, db: AsyncSession) -> Review:
    review = await get_review_by_id(review_id, db)
    
    if review.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    await db.commit()
    await db.refresh(review)
    return review


async def delete_review(review_id: uuid.UUID, user_id: int, is_admin: bool, db: AsyncSession) -> None:
    review = await get_review_by_id(review_id, db)
    
    if review.user_id != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    await db.execute(delete(Review).where(Review.id == review_id))
    await db.commit()
