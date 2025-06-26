from typing import List, Optional, Type, Dict, Any, Union
from datetime import datetime, timezone
from sqlalchemy.orm import Query
from ..models import Cat
from .base_service import BaseService

class CatService(BaseService):
    """猫咪信息服务层"""
    def __init__(self, db):
        super().__init__(db, Cat)
        
    def get_cat(self, id_or_model: Union[int, Type[Cat]], model: Optional[Type[Cat]] = None) -> Optional[Cat]:
        """获取单个猫咪信息"""
        if isinstance(id_or_model, int):
            return super().get(id_or_model)
        elif isinstance(id_or_model, type) and issubclass(id_or_model, Cat):
            return self.db.session.query(id_or_model).first()
        raise ValueError("参数必须是猫咪ID或Cat类")
    
    def create_cat(self, user_id: int, **kwargs) -> Cat:
        """创建猫咪信息"""
        if user_id is None:
            raise ValueError("user_id是必填字段")
            
        if 'name' in kwargs and not kwargs['name'].strip():
            raise ValueError("猫咪名称不能为空")
            
        if 'age' in kwargs and (not isinstance(kwargs['age'], int) or kwargs['age'] < 0 or kwargs['age'] > 30):
            raise ValueError("猫咪年龄必须在0-30岁之间")
            
        try:
            cat = Cat(
                user_id=user_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                **kwargs
            )
            self.db.session.add(cat)
            self.db.session.commit()
            return cat
        except Exception as e:
            self.db.session.rollback()
            raise ValueError(f"创建猫咪失败: {str(e)}")

    def update_cat(self, id: int, current_user_id: int, **kwargs) -> Cat:
        """更新猫咪信息"""
        cat = self.get(id)
        if not cat:
            raise ValueError(f"猫咪ID {id} 不存在")
        if cat.user_id != current_user_id:
            raise PermissionError("无权更新其他用户的猫咪信息")
            
        if 'age' in kwargs and (not isinstance(kwargs['age'], int) or kwargs['age'] < 0 or kwargs['age'] > 30):
            raise ValueError("猫咪年龄必须在0-30岁之间")
            
        try:
            return self.update(id, **kwargs)
        except Exception as e:
            raise ValueError(f"更新猫咪失败: {str(e)}")

    def delete_cat(self, id: int, user_id: int) -> bool:
        """删除猫咪信息"""
        cat = self.get(id)
        if not cat:
            raise ValueError(f"猫咪ID {id} 不存在")
        if cat.user_id != user_id:
            raise PermissionError("无权删除其他用户的猫咪信息")
        return self.delete(id)

    def search_cats(self, query: Optional[str] = None, min_age: Optional[int] = None, 
                  max_age: Optional[int] = None, breed: Optional[str] = None, 
                  is_adopted: Optional[bool] = None) -> List[Cat]:
        """搜索猫咪信息"""
        q = self.db.session.query(Cat)
        
        if query:
            q = q.filter(Cat.name.ilike(f'%{query}%'))
            
        if min_age is not None:
            q = q.filter(Cat.age >= min_age)
            
        if max_age is not None:
            q = q.filter(Cat.age <= max_age)
            
        if breed:
            q = q.filter(Cat.breed.ilike(f'%{breed}%'))
            
        if is_adopted is not None:
            q = q.filter(Cat.is_adopted == is_adopted)
            
        return q.all()
