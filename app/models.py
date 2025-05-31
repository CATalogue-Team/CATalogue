from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from typing import Optional
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import DeclarativeBase, Mapped
from . import db

class Base(DeclarativeBase):
    """SQLAlchemy基类"""
    pass

# 关联Flask-SQLAlchemy的metadata
Base.metadata = db.metadata

class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 关系定义
    cats = db.relationship('Cat', backref='owner', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self, expiration=3600):
        """生成认证token"""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({
            'id': self.id,
            'exp': datetime.utcnow().timestamp() + expiration
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('cats.id'), nullable=False)
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 关系定义
    images: db.Mapped[list['CatImage']] = db.relationship('CatImage', backref='cat', lazy=True, cascade='all, delete-orphan')
    
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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<EnvironmentCheck {self.check_name}: {self.status}>'
