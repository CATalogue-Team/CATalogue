from tests.shared.factories.base import BaseFactory
from app.models import Cat
from datetime import datetime
import random

class CatFactory(BaseFactory):
    """猫咪测试数据工厂"""
    
    def default_dict(self):
        """默认猫咪数据"""
        return {
            'name': f'测试猫咪_{datetime.now().timestamp()}',
            'breed': self.faker.word(),
            'age': random.randint(0, 20),
            'description': self.faker.text(),
            'created_at': self.created_at
        }
        
    def make_instance(self, **overrides):
        """创建Cat模型实例"""
        from app.extensions import db
        data = self.make_dict(**overrides)
        cat = Cat(**data)
        db.session.add(cat)
        db.session.commit()
        return cat
