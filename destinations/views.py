from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from .models import Destination
from .schemas import DestinationListSchema, DestinationDetailSchema
import uuid

destinations_router = APIRouter()


@destinations_router.get("/destinations", response_model=list[DestinationListSchema])
async def get_destinations(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Destination))
    destinations = result.scalars().all()
    return destinations


@destinations_router.get("/destinations/{id}", response_model=DestinationDetailSchema)
async def get_destination(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Destination).where(Destination.id == id))
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    return destination
