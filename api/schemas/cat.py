from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID

class CatBase(BaseModel):
    name: str = Field(..., max_length=100)
    breed: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[date] = None
    photos: List[str] = Field(default_factory=list)

class CatCreate(CatBase):
    owner_id: UUID = Field(..., description="Valid UUID of the cat owner")

class Cat(CatBase):
    id: UUID
    owner_id: str

    class Config:
        orm_mode = True
