from fastapi import APIRouter, Depends, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from .services import (
    get_destinations,
    get_destination_by_id,
    create_destination,
    update_destination,
    delete_destination
)
from .schemas import (
    DestinationCreateSchema,
    DestinationUpdateSchema,
    DestinationResponseSchema
)
from accounts.permissions import admin_required
from accounts.handlers import get_current_user
from accounts.models import User

destinations_router = APIRouter()


@destinations_router.get("/destinations", response_model=list[DestinationResponseSchema])
async def list_destinations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_destinations(db)


@destinations_router.get("/destinations/{id}", response_model=DestinationResponseSchema)
async def retrieve_destination(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_destination_by_id(id, db)


@destinations_router.post(
    "/destinations",
    response_model=DestinationResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_destination_endpoint(
    title: str = Form(...),
    description: str | None = Form(None),
    country: str = Form(...),
    city: str = Form(...),
    rating: float = Form(0.0),
    cover_image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    data = DestinationCreateSchema(
        title=title,
        description=description,
        country=country,
        city=city,
        rating=rating
    )
    return await create_destination(data, cover_image, db)


@destinations_router.put(
    "/destinations/{id}",
    response_model=DestinationResponseSchema
)
async def update_destination_endpoint(
    id: int,
    title: str | None = Form(None),
    description: str | None = Form(None),
    country: str | None = Form(None),
    city: str | None = Form(None),
    rating: float | None = Form(None),
    cover_image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    data = DestinationUpdateSchema(
        title=title,
        description=description,
        country=country,
        city=city,
        rating=rating
    )
    return await update_destination(id, data, cover_image, db)


@destinations_router.delete(
    "/destinations/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_destination_endpoint(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    await delete_destination(id, db)
    return None
