from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import get_db
from .models import BlackListTokens, User, Role, RefreshToken
from datetime import datetime, timedelta
import jwt
import secrets
import time

JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 300
REFRESH_TOKEN_EXPIRE_DAYS = 30


def generate_access_token(user_id: int):
    payload = {
        "user_id": user_id,
        "expires": time.time() + ACCESS_TOKEN_EXPIRE_SECONDS,
        "type": "access"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


async def generate_refresh_token(user_id: int, db: AsyncSession) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(refresh_token)
    await db.commit()
    
    return token


async def generate_tokens(user_id: int, db: AsyncSession):
    access_token = generate_access_token(user_id)
    refresh_token = await generate_refresh_token(user_id, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload if payload["expires"] >= time.time() else None
    except Exception:
        return None


async def validate_refresh_token(token: str, db: AsyncSession) -> RefreshToken | None:
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token)
    )
    refresh_token = result.scalar_one_or_none()
    
    if not refresh_token:
        return None
    
    if refresh_token.expires_at < datetime.now():
        return None
        
    if await is_token_blocked(token, db):
        return None
    
    return refresh_token


async def validate_access_token(token: str, db: AsyncSession) -> User | None:
    payload = decode_jwt(token)
    if not payload:
        return None
    
    if await is_token_blocked(token, db):
        return None
    
    return payload

async def is_token_blocked(
    token: str,
    db: AsyncSession,
) -> bool:
    result = await db.execute(
        select(BlackListTokens).where(BlackListTokens.token == token)
    )
    return result.scalar_one_or_none() is not None


class JWTBearer(HTTPBearer):
    async def __call__(
        self,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid auth scheme")

        if await is_token_blocked(credentials.credentials, db):
            raise HTTPException(status_code=403, detail="Token is blocked")

        payload = decode_jwt(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=403, detail="Invalid or expired token")

        return payload


async def get_current_user(
    payload: dict = Depends(JWTBearer()),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .where(User.id == payload["user_id"])
        .options(
            selectinload(User.permissions),
            selectinload(User.roles).selectinload(Role.permissions)
        )
    )
    return result.scalar_one_or_none()
