# 测试数据工厂模块初始化文件
from .base import BaseFactory
from .cat import CatFactory
from .user import UserFactory

__all__ = ['BaseFactory', 'CatFactory', 'UserFactory']
