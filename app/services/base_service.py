from typing import Type, Optional, List, Dict, Any
from sqlalchemy.orm import Query, DeclarativeBase
import logging

class BaseService:
    """服务基类"""
    logger = logging.getLogger(__name__)
    
    def __init__(self, db, model=None):
        if db is None:
            raise ValueError("db参数不能为None")
        if not hasattr(db, 'session'):
            raise ValueError("db对象必须包含session属性")
        if not hasattr(db.session, 'get'):
            raise ValueError("db.session必须支持get方法")
        if model is not None and not issubclass(model, DeclarativeBase):
            raise ValueError("无效的模型类 - 必须继承自SQLAlchemy模型")

        self.db = db
        self.model = model
        self.__class__.logger.info("BaseService initialized with db: %s", db)

    def get(self, id: int, model=None) -> Optional[Any]:
        """获取单个资源"""
        model = model or self.model
        if model is None:
            raise ValueError("model参数未设置")
        return self.db.session.query(model).get(id)

    def get_all(self, model=None) -> List[Any]:
        """获取所有资源"""
        model = model or self.model
        if model is None:
            raise ValueError("model参数未设置")
        return self.db.session.query(model).all()

    def create(self, model=None, **kwargs) -> Any:
        """创建资源"""
        model = model or self.model
        if model is None:
            raise ValueError("model参数未设置")
        
        # 检查模型类是否有效
        if not issubclass(model, DeclarativeBase):
            raise ValueError("无效的模型类 - 必须继承自SQLAlchemy模型")
            
        # 检查必填字段（排除自增主键）
        required_fields = [
            col.name for col in model.__table__.columns 
            if not col.nullable and not (col.primary_key and col.autoincrement)
        ]
        missing_fields = [field for field in required_fields if field not in kwargs]
        if missing_fields:
            raise ValueError(f"缺少必填字段: {', '.join(missing_fields)}")
            
        try:
            instance = model(**kwargs)
            self.db.session.add(instance)
            self.db.session.commit()
            return instance
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"创建失败: {str(e)}")
            raise

    def update(self, id: int, model=None, **kwargs) -> Any:
        """更新资源"""
        model = model or self.model
        if model is None:
            raise ValueError("model参数未设置")
            
        instance = self.db.session.get(model, id)
        if not instance:
            raise ValueError(f"资源ID {id} 不存在")
            
        try:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.session.commit()
            return instance
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"更新失败: {str(e)}")
            raise

    def delete(self, id: int, model=None) -> bool:
        """删除资源"""
        model = model or self.model
        if model is None:
            raise ValueError("model参数未设置")
            
        instance = self.db.session.get(model, id)
        if not instance:
            raise ValueError(f"资源ID {id} 不存在")
            
        try:
            self.db.session.delete(instance)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"删除失败: {str(e)}")
            raise

    def get_paginated(self, model=None, page: int = 1, per_page: int = 10, order_by: str = None, **filters) -> Dict[str, Any]:
        """获取分页资源
        Args:
            model: 可选模型类
            page: 页码
            per_page: 每页数量
            order_by: 排序字段(加-前缀表示降序)
            **filters: 过滤条件
        """
        model = model or self.model
        if model is None:
            raise ValueError("model参数未设置，无法执行分页查询")

        query = self.db.session.query(model)
        
        # 应用过滤条件
        for key, value in filters.items():
            if '__' in key:
                field, op = key.split('__', 1)
                if op == 'ilike':
                    query = query.filter(getattr(model, field).ilike(f'%{value}%'))
                elif op == 'gt':
                    query = query.filter(getattr(model, field) > value)
                elif op == 'lt':
                    query = query.filter(getattr(model, field) < value)
            else:
                query = query.filter(getattr(model, key) == value)
        
        # 应用排序
        if order_by:
            if order_by.startswith('-'):
                field = order_by[1:]
                query = query.order_by(getattr(model, field).desc())
            else:
                query = query.order_by(getattr(model, order_by))
                
        try:
            result = query.paginate(page=page, per_page=per_page, error_out=False)
            return result
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"分页查询失败: {str(e)}")
            raise
