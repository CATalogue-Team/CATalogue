
from typing import List, Optional
from datetime import datetime
from .. import db
from ..models import Cat, User
from .base_service import BaseService

class CatService(BaseService):
    """猫咪信息服务层"""
    model = Cat  # 定义模型类
    
    @classmethod
    def get(cls, id: int) -> Optional[Cat]:
        """获取单个猫咪信息"""
        return super().get(cls.model, id)
    
    @classmethod
    def get_all(cls) -> List[Cat]:
        """获取所有猫咪信息"""
        return super().get_all(cls.model)
    
    @classmethod
    def get_cat(cls, cat_id: int) -> Optional[Cat]:
        """获取单个猫咪信息(包含主人信息)"""
        return cls.model.query.options(db.joinedload(Cat.owner)).get(cat_id)
    
    @classmethod
    def get_all_cats(cls) -> List[Cat]:
        """获取所有猫咪信息(按更新时间排序)"""
        return cls.model.query.order_by(Cat.updated_at.desc()).all()
        
    @staticmethod
    def get_recent_cats(limit: int = 3) -> List[Cat]:
        """获取最近添加的猫咪(包含品种筛选)"""
        return Cat.query.order_by(Cat.created_at.desc()).limit(limit).all()
    
    @classmethod
    def create(cls, **kwargs) -> Cat:
        """创建猫咪信息"""
        if 'user_id' in kwargs and not User.query.get(kwargs['user_id']):
            raise ValueError("用户不存在")
            
        kwargs.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        return super().create(cls.model, **kwargs)
    
    @classmethod
    def update(cls, id: int, **kwargs) -> Optional[Cat]:
        """更新猫咪信息"""
        kwargs['updated_at'] = datetime.utcnow()
        return super().update(cls.model, id, **kwargs)
    
    @classmethod
    def delete(cls, id: int) -> bool:
        """删除猫咪信息"""
        return super().delete(cls.model, id)
    
    @classmethod
    def create_cat(cls, user_id: int, **kwargs) -> Cat:
        """创建猫咪信息(兼容旧接口)"""
        kwargs['user_id'] = user_id
        return cls.create(**kwargs)
    
    @classmethod
    def update_cat(cls, cat_id: int, **kwargs) -> Optional[Cat]:
        """更新猫咪信息(兼容旧接口)"""
        return cls.update(cat_id, **kwargs)
    
    @classmethod
    def delete_cat(cls, cat_id: int) -> bool:
        """删除猫咪信息(兼容旧接口)"""
        return cls.delete(cat_id)
    
    @staticmethod
    def get_cats_by_breed(breed: str) -> List[Cat]:
        """按品种筛选猫咪"""
        return Cat.query.filter_by(breed=breed).all()
        
    @staticmethod
    def get_adoptable_cats() -> List[Cat]:
        """获取可领养的猫咪"""
        return Cat.query.filter_by(is_adopted=False).all()
