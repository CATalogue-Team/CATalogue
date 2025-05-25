
from typing import Type, TypeVar, Optional
from flask import current_app
from .. import db
from flask_sqlalchemy.pagination import Pagination

ModelType = TypeVar('ModelType')

class BaseService:
    """基础服务类"""
    def __init__(self, db):
        """初始化基础服务
        参数:
            db: 必须包含session属性的数据库对象
        """
        if db is None:
            raise ValueError("db参数不能为None")
        if not hasattr(db, 'session'):
            raise ValueError("db对象必须包含session属性")
        self.db = db
        if not hasattr(self.db.session, 'get'):
            raise ValueError("db.session必须支持get方法")
    
    def get(self, model, id: int):
        """获取单个记录"""
        return self.db.session.get(model, id)
    
    def get_all(self, model):
        """获取所有记录"""
        return self.db.session.query(model).all()
    
    def create(self, model: Type['ModelType'], **kwargs) -> 'ModelType':
        """创建记录"""
        obj = model(**kwargs)
        self.db.session.add(obj)
        self.db.session.commit()
        return obj
    
    def update(self, model: Type['ModelType'], id: int, **kwargs) -> Optional['ModelType']:
        """更新记录"""
        obj = self.db.session.get(model, id)
        if not obj:
            return None
            
        for key, value in kwargs.items():
            setattr(obj, key, value)
            
        self.db.session.commit()
        return obj
    
    def delete(self, model, id: int) -> bool:
        """删除记录"""
        obj = self.db.session.get(model, id)
        if not obj:
            return False
            
        self.db.session.delete(obj)
        self.db.session.commit()
        return True
        
    def get_paginated(self, model, page=1, per_page=None, **filters):
        """
        分页获取记录
        参数:
            model: 模型类
            page: 当前页码
            per_page: 每页记录数(默认使用配置中的ITEMS_PER_PAGE)
            filters: 过滤条件
        返回:
            Pagination对象
        """
        from flask import current_app
        query = model.query
        for key, value in filters.items():
            if hasattr(model, key):
                query = query.filter(getattr(model, key) == value)
        return query.paginate(
            page=page,
            per_page=per_page or current_app.config.get('ITEMS_PER_PAGE', 10),
            error_out=False
        )
