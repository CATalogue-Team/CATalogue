
from typing import Type, TypeVar, Optional, TYPE_CHECKING
from flask import current_app
from .. import db
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar('ModelType', bound=DeclarativeBase)

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
        """创建记录
        参数:
            model: SQLAlchemy模型类
            **kwargs: 模型属性
        返回:
            创建的模型实例
        异常:
            ValueError: 如果缺少必填字段或模型无效
        """
        # 验证模型类型
        if not hasattr(model, '__table__'):
            raise ValueError("无效的模型类 - 必须继承自SQLAlchemy模型")
            
        # 检查必填字段
        required_fields = []
        table = model.__table__
        for column in table.columns:
            if (not column.nullable and 
                column.default is None and 
                column.name != 'id'):
                # 检查字段是否在kwargs中或是否有默认值
                if column.name not in kwargs:
                    required_fields.append(column.name)
        
        if required_fields:
            current_app.logger.debug(f"模型字段验证: {table.columns.keys()}")
            current_app.logger.debug(f"提供参数: {kwargs.keys()}")
            current_app.logger.debug(f"缺少必填字段: {required_fields}")
            raise ValueError(f"缺少必填字段: {', '.join(required_fields)}")
        
        try:
            obj = model(**kwargs)
            self.db.session.add(obj)
            self.db.session.commit()
            return obj
        except Exception as e:
            self.db.session.rollback()
            current_app.logger.error(f"创建记录失败: {str(e)}")
            raise
    
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
