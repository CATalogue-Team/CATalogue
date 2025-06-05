from faker import Faker
from datetime import datetime
import random

class BaseFactory:
    """测试数据基础工厂"""
    
    def __init__(self):
        self.faker = Faker()
        self.created_at = datetime.now()
        
    def make_dict(self, **overrides):
        """生成测试数据字典"""
        data = self.default_dict()
        data.update(overrides)
        return data
        
    def default_dict(self):
        """子类必须实现此方法"""
        raise NotImplementedError
        
    def make_instance(self, **overrides):
        """创建模型实例"""
        raise NotImplementedError
