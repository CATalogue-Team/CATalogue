from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from api.db import Base

class DBUser(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(512), unique=True, nullable=False)
    full_name = Column(String(512))
    hashed_password = Column(String(255), nullable=False)
    disabled = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
