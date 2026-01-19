from sqlalchemy import Integer, String, DateTime, Table, Column, ForeignKey, Boolean
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import BaseModel


user_permissions = Table(
    "user_permissions",
    BaseModel.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True)
)

role_permissions = Table(
    "role_permissions",
    BaseModel.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True)
)

user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True)
)

class User(BaseModel):
    __tablename__ = "users"
    
    id:Mapped[int] = mapped_column(primary_key=True)
    username:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password:Mapped[str] = mapped_column(String, nullable=False)
    theme:Mapped[str] = mapped_column(String, nullable=False, default="light")
    is_admin:Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    roles:Mapped[list["Role"]] = relationship("Role", secondary=user_roles, back_populates="users")
    permissions:Mapped[list["Permission"]] = relationship("Permission", secondary=user_permissions, back_populates="users")
    refresh_tokens:Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user")
    bookings:Mapped[list["Booking"]] = relationship("Booking", back_populates="user")
    reviews:Mapped[list["Review"]] = relationship("Review", back_populates="user")


class Permission(BaseModel):
    __tablename__ = "permissions"
    
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description:Mapped[str] = mapped_column(String, nullable=False)
    
    users:Mapped[list["User"]] = relationship("User", secondary=user_permissions, back_populates="permissions")
    roles:Mapped[list["Role"]] = relationship("Role", secondary=role_permissions, back_populates="permissions")


class Role(BaseModel):
    __tablename__ = "roles"
    
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String, nullable=False, unique=True)

    users:Mapped[list["User"]] = relationship("User", secondary=user_roles, back_populates="roles")
    permissions:Mapped[list["Permission"]] = relationship("Permission", secondary=role_permissions, back_populates="roles")




class BlackListTokens(BaseModel):
    __tablename__ = "blacklisted_tokens"
    
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    token:Mapped[str] = mapped_column(String, nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.now())


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    token:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at:Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    
    user:Mapped["User"] = relationship("User", back_populates="refresh_tokens")