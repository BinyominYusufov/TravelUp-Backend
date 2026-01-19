from fastapi import HTTPException, Depends, Request
from .handlers import get_current_user
from datetime import datetime
from .models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import status

def can_get_reports(current_user=Depends(get_current_user)):
    # Note: department field removed as it doesn't exist in User model
    # If department check is needed, add the field to User model first
    current_time = datetime.time(datetime.now())
    start_time = datetime.strptime("08:00", "%H:%M").time()
    end_time = datetime.strptime("18:00", "%H:%M").time()
    if not (start_time <= current_time and end_time >= current_time):
        raise HTTPException(status_code=403, detail="In this time you can't access to the data")


def is_authenticated_or_read_only(request:Request, current_user=Depends(get_current_user)):
    if request.method.upper() in ["GET", "HEAD", "OPTIONS"] or current_user:
        return True
    return False


def has_permission(permission):
    def checker(current_user = Depends(get_current_user)):
        user_permissions = [perm.name for perm in current_user.permissions]
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.append(perm.name)
        if not permission in user_permissions:
            raise HTTPException(status_code=403, detail=f"You can't {permission}")
    return checker


def admin_required(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You don't have access")
    return current_user


def required_permission(req_permissions:list):
    def has_permission(user=Depends(get_current_user)):
        user_permissions = [per.name for per in user.permissions]
        for role in user.roles:
            for per in role.permissions:
                user_permissions.append(per.name)
        for permission in req_permissions:
            if permission in user_permissions:
                return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied!"
        )
    return has_permission


def role_required(req_roles:list):
    def has_permission(user=Depends(get_current_user)):
        user_roles = [role.name for role in user.roles]
        
        for role in req_roles:
            if role in user_roles:
                return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied!"
        )
    return has_permission


def is_admin_user(user=Depends(get_current_user)):
    if user.is_admin:
        return True
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied!")


async def get_user(user_id: int, db: AsyncSession):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from .models import Role
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.permissions),
            selectinload(User.roles).selectinload(Role.permissions)
        )
    )
    return result.scalar_one_or_none()
            
        