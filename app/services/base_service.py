
from typing import Type, TypeVar, Optional
from .. import db
from flask_sqlalchemy.pagination import Pagination

ModelType = TypeVar('ModelType')

class BaseService:
    """基础服务类"""
    def __init__(self, db):
        if db is None:
            raise ValueError("db参数不能为None")
        if not hasattr(db, 'app'):
            raise ValueError("db对象必须包含app属性")
        self.db = db
    
    @staticmethod
    def get(model, id: int):
        """获取单个记录"""
        return db.session.get(model, id)
    
    @staticmethod
    def get_all(model):
        """获取所有记录"""
        return model.query.all()
    
    def create(self, model: Type['ModelType'], **kwargs) -> 'ModelType':
        """创建记录"""
        with self.db.app.app_context():
            obj = model(**kwargs)
            self.db.session.add(obj)
            self.db.session.commit()
            return obj
    
    def update(self, model: Type['ModelType'], id: int, **kwargs) -> Optional['ModelType']:
        """更新记录"""
        with self.db.app.app_context():
            obj = self.db.session.get(model, id)
            if not obj:
                return None
                
            for key, value in kwargs.items():
                setattr(obj, key, value)
                
            self.db.session.commit()
            return obj
    
    @staticmethod
    def delete(model, id: int) -> bool:
        """删除记录"""
        obj = db.session.get(model, id)
        if not obj:
            return False
            
        db.session.delete(obj)
        db.session.commit()
        return True
        
    @staticmethod
    def get_paginated(model, page=1, per_page=None, **filters):
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
