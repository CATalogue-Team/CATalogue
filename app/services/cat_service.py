
from typing import List, Optional
from ..models import Cat
from .base_service import BaseService

class CatService(BaseService):
    """猫咪信息服务层"""
    
    @staticmethod
    def get_cat(cat_id: int) -> Optional[Cat]:
        """获取单个猫咪信息"""
        return BaseService.get(Cat, cat_id)
    
    @staticmethod
    def get_all_cats() -> List[Cat]:
        """获取所有猫咪信息"""
        return Cat.query.order_by(Cat.created_at.desc()).all()
        
    @staticmethod
    def get_recent_cats(limit: int = 3) -> List[Cat]:
        """获取最近添加的猫咪"""
        return Cat.query.order_by(Cat.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def create_cat(**kwargs) -> Cat:
        """创建猫咪信息"""
        return BaseService.create(Cat, **kwargs)
    
    @staticmethod
    def update_cat(cat_id: int, **kwargs) -> Optional[Cat]:
        """更新猫咪信息"""
        return BaseService.update(Cat, cat_id, **kwargs)
    
    @staticmethod
    def delete_cat(cat_id: int) -> bool:
        """删除猫咪信息"""
        return BaseService.delete(Cat, cat_id)
