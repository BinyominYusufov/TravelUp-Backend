from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status
from .models import Destination
from .schemas import DestinationCreateSchema, DestinationUpdateSchema


async def get_destinations(db: AsyncSession):
    result = await db.execute(select(Destination))
    return result.scalars().all()


async def get_destination_by_id(destination_id: int, db: AsyncSession) -> Destination:
    result = await db.execute(select(Destination).where(Destination.id == destination_id))
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    return destination


async def create_destination(data: DestinationCreateSchema, db: AsyncSession) -> Destination:
    destination = Destination(
        title=data.title,
        description=data.description,
        country=data.country,
        city=data.city,
        cover_image=data.cover_image,
        rating=data.rating
    )
    db.add(destination)
    await db.commit()
    await db.refresh(destination)
    return destination


async def update_destination(
    destination_id: int,
    data: DestinationUpdateSchema,
    db: AsyncSession
) -> Destination:
    destination = await get_destination_by_id(destination_id, db)
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(destination, field, value)
    
    await db.commit()
    await db.refresh(destination)
    return destination


async def delete_destination(destination_id: int, db: AsyncSession) -> None:
    await get_destination_by_id(destination_id, db)
    await db.execute(delete(Destination).where(Destination.id == destination_id))
    await db.commit()
