from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from typing import Optional
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from .database import db
from .base import Base

# 关联Flask-SQLAlchemy的metadata
Base.metadata = db.metadata

class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(128), nullable=False)
    is_admin: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(db.String(20), default='pending', nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(db.DateTime)
    approved_by: Mapped[Optional[int]] = mapped_column(db.Integer, db.ForeignKey('users.id'))
    
    # 关系定义
    cats: Mapped[List['Cat']] = relationship('Cat', back_populates='owner')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self, expiration=3600):
        """生成认证token"""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({
            'id': self.id,
            'exp': datetime.now(timezone.utc).timestamp() + expiration
        })
    
    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'is_admin': self.is_admin,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class CatImage(Base):
    __tablename__ = 'cat_images'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    cat_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('cats.id'), nullable=False)
    cat: Mapped['Cat'] = relationship('Cat', back_populates='images')
    
    def __init__(self, **kwargs):
        url = kwargs.get('url', '')
        if not url.startswith('/static/uploads/'):
            from flask import current_app
            filename = url.split('/')[-1]
            kwargs['url'] = f'/static/uploads/{filename}'
            current_app.logger.warning(f"修正图片URL格式: {url} -> {kwargs['url']}")
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f'<CatImage {self.url}>'

class Cat(Base):
    __tablename__ = 'cats'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(50))
    age = db.Column(db.Integer)
    description = db.Column(db.Text)
    is_adopted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner: Mapped['User'] = relationship('User', back_populates='cats')
    
    # 关系定义
    images: Mapped[List['CatImage']] = relationship('CatImage', back_populates='cat', cascade='all, delete-orphan')
    
    @property
    def primary_image(self) -> Optional[str]:
        """获取猫咪的主图片URL"""
        return next((img.url for img in self.images if img.is_primary), None) if self.images else None
    
    def __repr__(self):
        return f'<Cat {self.name}>'

    def to_dict(self):
        """将猫咪对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'breed': self.breed,
            'age': self.age,
            'description': self.description,
            'is_adopted': self.is_adopted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'primary_image': self.primary_image
        }

class EnvironmentCheck(Base):
    __tablename__ = 'environment_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    check_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f'<EnvironmentCheck {self.check_name}: {self.status}>'
