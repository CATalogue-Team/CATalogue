from pydantic import BaseModel, field_validator
from typing import Optional, Union
from datetime import datetime
from uuid import UUID
from .user import User

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class Post(PostBase):
    id: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    likes: int
    author: Optional[User] = None

    @field_validator('id', 'author_id', mode='before')
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
                "author_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "likes": 0
            }
        }

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: str
    author_id: str
    post_id: str
    created_at: datetime
    author: Optional[User] = None

    @field_validator('id', 'author_id', 'post_id', mode='before')
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
                "author_id": "123e4567-e89b-12d3-a456-426614174000",
                "post_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2025-01-01T00:00:00"
            }
        }
