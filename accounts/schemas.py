from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from enum import Enum

class UserRegisterSchema(BaseModel):
    username:str
    password:str
    confirm_password:str
    
    @field_validator("*", mode="before")
    def not_empty_validate(value):
        if not value:
            raise ValueError("Please fill all fields")
        return value
    
    @model_validator(mode="before")
    def validate_password(self):
        print(self)
        if self["password"] != self["confirm_password"]:
            raise ValueError("passwords do not match")
        return self
    
    
class ThemeEnum(str, Enum):
    light = "light"
    dark = "dark"
    default = "default"


class ProfileUpdateSchema(BaseModel):
    theme: ThemeEnum | None = None
    
class UserLoginSchema(BaseModel):
    username:str
    password:str

class UserLogoutSchema(BaseModel):
    token:str


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str




class AddUserShcema(BaseModel):
    username:str
    password:str
    confirm_password:str
    is_admin:bool = False
    
    @field_validator("*", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("Fields are required")
        return value

    @model_validator(mode="before")
    def check_passwords_match(value):
        if value["password"] != value["confirm_password"]:
            raise ValueError("Passwords do not match")
        return value


class LoginShcema(BaseModel):
    username:str
    password:str
    
    @field_validator("*", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("Fields are required")
        return value
    
class UserSchema(BaseModel):
    id:int
    username:str
    theme:str
    permissions:list["PermissionSchema"]
    roles:list["RoleSchema"]
    
    model_config=ConfigDict(from_attributes=True)
    
    
class SetUserPermissionsSchema(BaseModel):
    user_id:int
    permissions:list[int]
    
    @field_validator("*", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("Fields are required")
        return value

class SetRolePermissionsSchema(BaseModel):
    role_id:int
    permissions:list[int]
    
    @field_validator("*", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("Fields are required")
        return value


class PermissionSchema(BaseModel):
    id:int
    name:str
    description:str


class RoleSchema(BaseModel):
    id:int
    name:str
    permissions:list[PermissionSchema]
    
class AddRoleSchema(BaseModel):
    name:str
    
    @field_validator("name", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("role name must be set!")
        return value


class SetRoleToUserSchema(BaseModel):
    user_id:int
    roles:list[int]
    
    @field_validator("*", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("Fields are required!")
        return value


