from .models import User
from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, hashed_password):
    return bcrypt.verify(password, hashed_password)

async def check_user(input_user, db: AsyncSession):
    result = await db.execute(select(User).where(User.username==input_user.username))
    return result.scalar_one_or_none()