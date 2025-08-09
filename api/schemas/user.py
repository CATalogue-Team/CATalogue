from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID

class TokenData(BaseModel):
    username: str

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    is_admin: bool = False
    disabled: bool = False

class User(UserBase):
    id: str
    disabled: bool
    is_admin: bool

    @field_validator('id', mode='before')
    def parse_uuid(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, UUID):
            return str(v)
        raise ValueError("Invalid UUID format")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "disabled": False,
                "is_admin": False
            }
        }

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
