
from .. import db
from flask_sqlalchemy.pagination import Pagination

class BaseService:
    """基础服务类"""
    def __init__(self, db=None):
        self.db = db
    
    @staticmethod
    def get(model, id: int):
        """获取单个记录"""
        return db.session.get(model, id)
    
    @staticmethod
    def get_all(model):
        """获取所有记录"""
        return model.query.all()
    
    @staticmethod
    def create(model, **kwargs):
        """创建记录"""
        obj = model(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj
    
    @staticmethod
    def update(model, id: int, **kwargs):
        """更新记录"""
        obj = db.session.get(model, id)
        if not obj:
            return None
            
        for key, value in kwargs.items():
            setattr(obj, key, value)
            
        db.session.commit()
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
