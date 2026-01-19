from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import uuid
from .services import (
    create_review,
    get_destination_reviews,
    update_review,
    delete_review
)
from .schemas import (
    ReviewCreateSchema,
    ReviewUpdateSchema,
    ReviewResponseSchema
)
from accounts.permissions import admin_required
from accounts.handlers import get_current_user
from accounts.models import User

reviews_router = APIRouter()


@reviews_router.post(
    "/reviews",
    response_model=ReviewResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_review_endpoint(
    data: ReviewCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_review(current_user.id, data, db)


@reviews_router.get("/destinations/{id}/reviews", response_model=list[ReviewResponseSchema])
async def get_destination_reviews_endpoint(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    return await get_destination_reviews(id, db)


@reviews_router.put(
    "/reviews/{id}",
    response_model=ReviewResponseSchema
)
async def update_review_endpoint(
    id: uuid.UUID,
    data: ReviewUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await update_review(id, current_user.id, data, db)


@reviews_router.delete(
    "/reviews/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_review_endpoint(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await delete_review(id, current_user.id, current_user.is_admin, db)
    return None
