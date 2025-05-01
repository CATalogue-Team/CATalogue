
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
