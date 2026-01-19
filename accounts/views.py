from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from database import get_db
from .models import User, Role, Permission, BlackListTokens, RefreshToken
from .schemas import *
from .utils import hash_password, verify_password
from .handlers import generate_tokens, get_current_user, validate_refresh_token
from .permissions import is_admin_user, get_user, required_permission, role_required


auth_route = APIRouter()


@auth_route.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def user_register(
    user_data: UserRegisterSchema,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=user_data.username,
        password=hash_password(user_data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Загружаем relationships для сериализации
    result = await db.execute(
        select(User)
        .where(User.id == user.id)
        .options(
            selectinload(User.permissions),
            selectinload(User.roles).selectinload(Role.permissions)
        )
    )
    user_with_relations = result.scalar_one()
    return user_with_relations


@auth_route.post("/login", response_model=TokenResponseSchema)
async def user_login(
    user_data: UserLoginSchema,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return await generate_tokens(user.id, db)


@auth_route.post("/logout")
async def user_logout(
    token: UserLogoutSchema,
    db: AsyncSession = Depends(get_db),
):
    blacked = BlackListTokens(token=token.token)
    db.add(blacked)
    await db.commit()
    return {"message": "Logged out"}


@auth_route.post("/refresh", response_model=TokenResponseSchema)
async def refresh_tokens(
    token_data: RefreshTokenSchema,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token and rotate refresh token"""
    # Validate the refresh token
    refresh_token = await validate_refresh_token(token_data.refresh_token, db)
    
    if not refresh_token:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired refresh token"
        )
    
    user_id = refresh_token.user_id
    
    # Blacklist the old refresh token
    blacklisted = BlackListTokens(token=refresh_token.token)
    db.add(blacklisted)
    
    # Delete the old refresh token from database
    await db.execute(delete(RefreshToken).where(RefreshToken.id == refresh_token.id))
    await db.commit()
    
    # Generate new tokens (access + new refresh token)
    return await generate_tokens(user_id, db)


@auth_route.get("/me", response_model=UserSchema)
async def me(current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return current_user


@auth_route.get("/profile", response_model=UserSchema)
async def get_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user profile"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Перезагружаем пользователя с relationships для получения актуальных данных
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.permissions),
            selectinload(User.roles).selectinload(Role.permissions)
        )
    )
    user = result.scalar_one()
    return user


@auth_route.patch("/profile", response_model=UserSchema)
async def update_profile(
    profile_data: ProfileUpdateSchema,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if profile_data.theme is not None:
        current_user.theme = profile_data.theme.value
    
    await db.commit()
    # Перезагружаем пользователя с relationships
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.permissions),
            selectinload(User.roles).selectinload(Role.permissions)
        )
    )
    user = result.scalar_one()
    return user


@auth_route.get("/roles", response_model=list[RoleSchema])
async def get_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions))
    )
    return result.scalars().all()




@auth_route.post("/set-permissions-to-user", dependencies=[Depends(is_admin_user)], response_model=UserSchema)
async def set_permissions_to_user_api_view(data:SetUserPermissionsSchema, db:AsyncSession=Depends(get_db)):
    user = await get_user(user_id=data.user_id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User doesn't exist!")
    result = await db.execute(select(Permission).where(Permission.id.in_(data.permissions)))
    permissions = result.scalars().all()
    if not permissions:
        raise HTTPException(detail="Permission doesn't exist", status_code=status.HTTP_400_BAD_REQUEST)
    
    for perm in permissions:
        if perm not in user.permissions:
            user.permissions.append(perm)
    await db.commit()
    # Перезагружаем пользователя с relationships
    result = await db.execute(
        select(User)
        .where(User.id == user.id)
        .options(
            selectinload(User.permissions),
            selectinload(User.roles).selectinload(Role.permissions)
        )
    )
    user = result.scalar_one()
    return user


@auth_route.post("/add-role", response_model=RoleSchema)
async def create_role_api_view(data:AddRoleSchema, db:AsyncSession=Depends(get_db)):
    role = Role(name=data.name)
    db.add(role)
    await db.commit()
    # Перезагружаем роль с relationships
    result = await db.execute(
        select(Role)
        .where(Role.id == role.id)
        .options(selectinload(Role.permissions))
    )
    role = result.scalar_one()
    return role


@auth_route.post("/add-permissions-to-role", response_model=RoleSchema)
async def add_permissions_to_role(data:SetRolePermissionsSchema, db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(Role).where(Role.id==data.role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found!")
    result = await db.execute(select(Permission).where(Permission.id.in_(data.permissions)))
    permissions = result.scalars().all()
    if not permissions:
        raise HTTPException(detail="Permission doesn't exist", status_code=status.HTTP_400_BAD_REQUEST)
    
    for perm in permissions:
        if perm not in role.permissions:
            role.permissions.append(perm)
    await db.commit()
    # Перезагружаем роль с relationships
    result = await db.execute(
        select(Role)
        .where(Role.id == role.id)
        .options(selectinload(Role.permissions))
    )
    role = result.scalar_one()
    return role


@auth_route.post("/add-role-to-user", response_model=UserSchema)
async def add_role_to_user_view(data:SetRoleToUserSchema, db:AsyncSession=Depends(get_db)):
    user = await get_user(user_id=data.user_id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist!")
    result = await db.execute(select(Role).where(Role.id.in_(data.roles)))
    roles = result.scalars().all()
    if not roles:
        raise HTTPException(detail="Roles don't exist", status_code=status.HTTP_400_BAD_REQUEST)
    
    for r in roles:
        if r not in user.roles:
            user.roles.append(r)
    await db.commit()
    # Перезагружаем пользователя с relationships
    result = await db.execute(
        select(User)
        .where(User.id == user.id)
        .options(
            selectinload(User.permissions),
            selectinload(User.roles).selectinload(Role.permissions)
        )
    )
    user = result.scalar_one()
    return user



@auth_route.post("/add-user", response_model=AddUserShcema)
async def add_user_api_view(data:AddUserShcema, db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(detail="User already exists!", status_code=status.HTTP_400_BAD_REQUEST)
    user = User(username=data.username, password=hash_password(data.password), is_admin=data.is_admin)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return data
