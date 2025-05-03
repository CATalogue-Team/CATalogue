
from typing import Type, TypeVar, Optional, List, Any
from .. import db

T = TypeVar('T', bound=db.Model)

class BaseService:
    """基础服务类"""
    
    @staticmethod
    def get(model: Type[T], id: int) -> Optional[T]:
        """获取单个记录"""
        return model.query.get(id)
    
    @staticmethod
    def get_all(model: Type[T]) -> List[T]:
        """获取所有记录"""
        return model.query.all()
    
    @staticmethod
    def create(model: Type[T], **kwargs) -> T:
        """创建记录"""
        obj = model(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj
    
    @staticmethod
    def update(model: Type[T], id: int, **kwargs) -> Optional[T]:
        """更新记录"""
        obj = model.query.get(id)
        if not obj:
            return None
            
        for key, value in kwargs.items():
            setattr(obj, key, value)
            
        db.session.commit()
        return obj
    
    @staticmethod
    def delete(model: Type[T], id: int) -> bool:
        """删除记录"""
        obj = model.query.get(id)
        if not obj:
            return False
            
        db.session.delete(obj)
        db.session.commit()
        return True
        
    @staticmethod
    def get_paginated(model: Type[T], page=1, per_page=None, **filters) -> 'flask_sqlalchemy.Pagination':
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
