
from typing import List, Optional
from ..models import Cat
from .. import db

class CatService:
    """猫咪信息服务层"""
    
    @staticmethod
    def get_cat(cat_id: int) -> Optional[Cat]:
        """获取单个猫咪信息"""
        return Cat.query.get(cat_id)
    
    @staticmethod
    def get_all_cats() -> List[Cat]:
        """获取所有猫咪信息"""
        return Cat.query.order_by(Cat.created_at.desc()).all()
        
    @staticmethod
    def get_recent_cats(limit: int = 3) -> List[Cat]:
        """获取最近添加的猫咪"""
        return Cat.query.order_by(Cat.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def create_cat(name: str, description: str, image: str = None) -> Cat:
        """创建猫咪信息"""
        cat = Cat(name=name, description=description, image=image)
        db.session.add(cat)
        db.session.commit()
        return cat
    
    @staticmethod
    def update_cat(cat_id: int, **kwargs) -> Optional[Cat]:
        """更新猫咪信息"""
        cat = Cat.query.get(cat_id)
        if not cat:
            return None
            
        for key, value in kwargs.items():
            setattr(cat, key, value)
            
        db.session.commit()
        return cat
    
    @staticmethod
    def delete_cat(cat_id: int) -> bool:
        """删除猫咪信息"""
        cat = Cat.query.get(cat_id)
        if not cat:
            return False
            
        db.session.delete(cat)
        db.session.commit()
        return True
