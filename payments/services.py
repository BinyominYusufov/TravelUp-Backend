from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from .models import Payment, PaymentStatus
from .schemas import PaymentCreateSchema
from bookings.models import Booking


async def create_payment(user_id: int, data: PaymentCreateSchema, db: AsyncSession) -> Payment:
    booking_result = await db.execute(select(Booking).where(Booking.id == data.booking_id))
    booking = booking_result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create payments for your own bookings"
        )
    
    existing_payment_result = await db.execute(select(Payment).where(Payment.booking_id == data.booking_id))
    existing_payment = existing_payment_result.scalar_one_or_none()
    
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already exists for this booking"
        )
    
    payment = Payment(
        booking_id=data.booking_id,
        amount=data.amount,
        currency=data.currency,
        provider=data.provider,
        status=PaymentStatus.pending
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def get_user_payments(user_id: int, db: AsyncSession) -> list[Payment]:
    result = await db.execute(
        select(Payment)
        .join(Booking)
        .where(Booking.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_all_payments(db: AsyncSession) -> list[Payment]:
    result = await db.execute(select(Payment))
    return list(result.scalars().all())
