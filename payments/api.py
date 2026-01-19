from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from .services import (
    create_payment,
    get_user_payments,
    get_all_payments
)
from .schemas import (
    PaymentCreateSchema,
    PaymentResponseSchema
)
from accounts.permissions import admin_required
from accounts.handlers import get_current_user
from accounts.models import User

payments_router = APIRouter()


@payments_router.post(
    "/payments",
    response_model=PaymentResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_payment_endpoint(
    data: PaymentCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_payment(current_user.id, data, db)


@payments_router.get("/payments/my", response_model=list[PaymentResponseSchema])
async def get_my_payments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_user_payments(current_user.id, db)


@payments_router.get("/payments", response_model=list[PaymentResponseSchema])
async def get_all_payments_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    return await get_all_payments(db)
