
from typing import List, Optional
from datetime import datetime
from ..models import Cat, User
from .base_service import BaseService

class CatService(BaseService):
    """猫咪信息服务层"""
    
    @staticmethod
    def get_cat(cat_id: int) -> Optional[Cat]:
        """获取单个猫咪信息(包含主人信息)"""
        return Cat.query.options(db.joinedload(Cat.owner)).get(cat_id)
    
    @staticmethod
    def get_all_cats() -> List[Cat]:
        """获取所有猫咪信息(按更新时间排序)"""
        return Cat.query.order_by(Cat.updated_at.desc()).all()
        
    @staticmethod
    def get_recent_cats(limit: int = 3) -> List[Cat]:
        """获取最近添加的猫咪(包含品种筛选)"""
        return Cat.query.order_by(Cat.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def create_cat(user_id: int, **kwargs) -> Cat:
        """创建猫咪信息(自动关联用户)"""
        if not User.query.get(user_id):
            raise ValueError("用户不存在")
            
        kwargs.update({
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        return BaseService.create(Cat, **kwargs)
    
    @staticmethod
    def update_cat(cat_id: int, **kwargs) -> Optional[Cat]:
        """更新猫咪信息(自动更新修改时间)"""
        kwargs['updated_at'] = datetime.utcnow()
        return BaseService.update(Cat, cat_id, **kwargs)
    
    @staticmethod
    def delete_cat(cat_id: int) -> bool:
        """删除猫咪信息(软删除考虑)"""
        return BaseService.delete(Cat, cat_id)
    
    @staticmethod
    def get_cats_by_breed(breed: str) -> List[Cat]:
        """按品种筛选猫咪"""
        return Cat.query.filter_by(breed=breed).all()
        
    @staticmethod
    def get_adoptable_cats() -> List[Cat]:
        """获取可领养的猫咪"""
        return Cat.query.filter_by(is_adopted=False).all()
