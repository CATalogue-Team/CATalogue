from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from pydantic import BaseModel, Field, field_validator
from api.db import Base

# SQLAlchemy Model
class DBCat(Base):
    __tablename__ = "cats"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String(100), nullable=False)
    breed = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=True)
    owner_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models
class CatBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    breed: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[date] = None
    photos: List[str] = Field(default_factory=list)

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
        from_attributes = True
