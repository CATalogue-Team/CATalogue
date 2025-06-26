from typing import Type, Optional, List, Dict, Any
from sqlalchemy.orm import Query
import logging

class BaseService:
    """服务基类"""
    def __init__(self, db, model):
        self.db = db
        self.model = model
        self.logger = logging.getLogger(__name__)

    def get(self, id: int) -> Optional[Any]:
        """获取单个资源"""
        return self.db.session.query(self.model).get(id)

    def get_all(self) -> List[Any]:
        """获取所有资源"""
        return self.db.session.query(self.model).all()

    def create(self, **kwargs) -> Any:
        """创建资源"""
        try:
            instance = self.model(**kwargs)
            self.db.session.add(instance)
            self.db.session.commit()
            return instance
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"创建失败: {str(e)}")
            raise

    def update(self, id: int, **kwargs) -> Optional[Any]:
        """更新资源"""
        instance = self.get(id)
        if not instance:
            return None
            
        try:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.session.commit()
            return instance
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"更新失败: {str(e)}")
            raise

    def delete(self, id: int) -> bool:
        """删除资源"""
        instance = self.get(id)
        if not instance:
            return False
            
        try:
            self.db.session.delete(instance)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"删除失败: {str(e)}")
            return False

    def get_paginated(self, page: int = 1, per_page: int = 10, **filters) -> Dict[str, Any]:
        """获取分页资源"""
        query = self.db.session.query(self.model)
        
        # 应用过滤条件
        for key, value in filters.items():
            if '__' in key:
                field, op = key.split('__', 1)
                if op == 'ilike':
                    query = query.filter(getattr(self.model, field).ilike(f'%{value}%'))
            else:
                query = query.filter(getattr(self.model, key) == value)
                
        return query.paginate(page=page, per_page=per_page, error_out=False)
