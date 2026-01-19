from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import uuid
from .services import (
    create_booking,
    get_user_bookings,
    get_all_bookings,
    cancel_booking,
    update_booking_status
)
from .schemas import (
    BookingCreateSchema,
    BookingUpdateStatusSchema,
    BookingResponseSchema
)
from accounts.permissions import admin_required
from accounts.handlers import get_current_user
from accounts.models import User

bookings_router = APIRouter()


@bookings_router.post(
    "/bookings",
    response_model=BookingResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_booking_endpoint(
    data: BookingCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_booking(current_user.id, data, db)


@bookings_router.get("/bookings/my", response_model=list[BookingResponseSchema])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_user_bookings(current_user.id, db)


@bookings_router.get("/bookings", response_model=list[BookingResponseSchema])
async def get_all_bookings_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    return await get_all_bookings(db)


@bookings_router.patch(
    "/bookings/{id}/cancel",
    response_model=BookingResponseSchema
)
async def cancel_booking_endpoint(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await cancel_booking(id, current_user.id, db)


@bookings_router.patch(
    "/bookings/{id}/status",
    response_model=BookingResponseSchema
)
async def update_booking_status_endpoint(
    id: uuid.UUID,
    data: BookingUpdateStatusSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    return await update_booking_status(id, data, db)
