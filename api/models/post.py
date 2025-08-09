from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from api.db import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    likes = Column(Integer, default=0)

    # 关系定义
    author = relationship("DBUser", back_populates="posts", lazy="joined")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan", lazy="joined")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    content = Column(Text, nullable=False)
    author_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    post_id = Column(PG_UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # 关系定义
    author = relationship("DBUser", back_populates="comments", lazy="joined")
    post = relationship("Post", back_populates="comments", lazy="joined")
