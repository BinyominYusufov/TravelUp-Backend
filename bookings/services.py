from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import uuid
from .models import Booking, BookingStatus
from .schemas import BookingCreateSchema, BookingUpdateStatusSchema
from destinations.models import Destination


async def create_booking(user_id: int, data: BookingCreateSchema, db: AsyncSession) -> Booking:
    result = await db.execute(select(Destination).where(Destination.id == data.destination_id))
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    booking = Booking(
        user_id=user_id,
        destination_id=data.destination_id,
        start_date=data.start_date,
        end_date=data.end_date,
        travelers_count=data.travelers_count,
        total_price=data.total_price,
        status=BookingStatus.pending
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


async def get_user_bookings(user_id: int, db: AsyncSession) -> list[Booking]:
    result = await db.execute(select(Booking).where(Booking.user_id == user_id))
    return list(result.scalars().all())


async def get_all_bookings(db: AsyncSession) -> list[Booking]:
    result = await db.execute(select(Booking))
    return list(result.scalars().all())


async def get_booking_by_id(booking_id: uuid.UUID, db: AsyncSession) -> Booking:
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return booking


async def cancel_booking(booking_id: uuid.UUID, user_id: int, db: AsyncSession) -> Booking:
    booking = await get_booking_by_id(booking_id, db)
    
    if booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own bookings"
        )
    
    booking.status = BookingStatus.cancelled
    await db.commit()
    await db.refresh(booking)
    return booking


async def update_booking_status(booking_id: uuid.UUID, data: BookingUpdateStatusSchema, db: AsyncSession) -> Booking:
    booking = await get_booking_by_id(booking_id, db)
    booking.status = data.status.value
    await db.commit()
    await db.refresh(booking)
    return booking
