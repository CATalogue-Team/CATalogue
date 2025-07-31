from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID

class CatBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    breed: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[date] = None
    photos: List[str] = Field(default_factory=list)

class CatCreate(CatBase):
    owner_id: UUID

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

class CatUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    breed: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[date] = None
    photos: Optional[List[str]] = None

class Cat(CatBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
