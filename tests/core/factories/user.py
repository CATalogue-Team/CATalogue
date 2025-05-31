from tests.core.factories.base import BaseFactory
from app.models import User
from datetime import datetime
import random

class UserFactory(BaseFactory):
    """用户测试数据工厂"""
    
    def default_dict(self):
        """默认用户数据"""
        return {
            'username': f'testuser_{datetime.now().timestamp()}',
            'password': self.faker.password(),
            'email': self.faker.email(),
            'created_at': self.created_at
        }
        
    def make_instance(self, **overrides):
        """创建User模型实例"""
        from app.extensions import db
        data = self.make_dict(**overrides)
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return user
