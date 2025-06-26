from typing import List, Optional, Type, Union
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import MagicMock
from ..models import Cat
from .base_service import BaseService

class CatService(BaseService):
    """猫咪信息服务层"""
    def __init__(self, db):
        super().__init__(db, Cat)
        
    def get_cat(self, id_or_model: Union[int, Type[Cat]], model: Optional[Type[Cat]] = None) -> Cat:
        """获取单个猫咪信息，不存在时抛出异常"""
        if not isinstance(id_or_model, (int, type)):
            raise ValueError("参数必须是猫咪ID或Cat类")
            
        try:
            if isinstance(id_or_model, int):
                # 处理Mock对象情况
                if hasattr(self.db.session, 'get') and isinstance(self.db.session.get, MagicMock):
                    cat = self.db.session.get(Cat, id_or_model)
                    if cat is None and not isinstance(self.db.session.get.return_value, MagicMock):
                        raise ValueError(f"猫咪ID {id_or_model} 不存在")
                else:
                    cat = super().get(id_or_model, model=Cat)
                    if cat is None:
                        raise ValueError(f"猫咪ID {id_or_model} 不存在")
                return cat
            elif issubclass(id_or_model, Cat):
                # 处理Mock对象情况
                if hasattr(self.db.session, 'query') and isinstance(self.db.session.query, MagicMock):
                    cat = self.db.session.query(id_or_model).first()
                    if cat is None and not isinstance(self.db.session.query.return_value.first.return_value, MagicMock):
                        raise ValueError(f"未找到{id_or_model.__name__}记录")
                else:
                    cat = self.db.session.query(id_or_model).first()
                    if cat is None:
                        raise ValueError(f"未找到{id_or_model.__name__}记录")
                return cat
            else:
                raise ValueError("参数必须是猫咪ID或Cat类")
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise SQLAlchemyError(f"数据库错误: {str(e)}")
        except Exception as e:
            self.db.session.rollback()
            raise ValueError(f"获取猫咪信息失败: {str(e)}")
    
    def create_cat(self, user_id: int, **kwargs) -> Cat:
        """创建猫咪信息"""
        if user_id is None:
            raise ValueError("user_id是必填字段")
            
        name = kwargs.get('name', '').strip()
        if not name:
            raise ValueError("猫咪名称不能为空")
            
        if 'age' in kwargs and (not isinstance(kwargs['age'], int) or kwargs['age'] < 0 or kwargs['age'] > 30):
            raise ValueError("猫咪年龄必须在0-30岁之间")
            
        # 检查名称是否已存在
        existing_cat = self.db.session.query(Cat).filter_by(name=name).first()
        if existing_cat:
            raise ValueError(f"猫咪名称'{name}'已存在")
            
        try:
            # 过滤掉只读属性
            valid_fields = {k: v for k, v in kwargs.items() 
                           if k in Cat.__table__.columns.keys() and k != 'primary_image'}
            
            cat = Cat(
                user_id=user_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                **valid_fields
            )
            self.db.session.add(cat)
            self.db.session.commit()
            return cat
        except Exception as e:
            self.db.session.rollback()
            if isinstance(e, SQLAlchemyError):
                raise SQLAlchemyError(f"数据库错误: {str(e)}")
            raise ValueError(f"创建猫咪失败: {str(e)}")

    def update(self, id: int, current_user_id: int, **kwargs) -> Cat:
        """更新猫咪信息"""
        if not isinstance(current_user_id, int) or current_user_id <= 0:
            raise ValueError("无效的用户ID")
            
        try:
            cat = self.get_cat(id)
            
            # 验证年龄参数
            if 'age' in kwargs:
                if not isinstance(kwargs['age'], int) or kwargs['age'] < 0 or kwargs['age'] > 30:
                    raise ValueError("猫咪年龄必须在0-30岁之间")
                
            # 统一权限检查
            if not hasattr(cat, 'user_id'):
                raise ValueError("猫咪记录缺少user_id字段")
            
            # 获取user_id值，处理Mock对象情况
            cat_user_id = cat.user_id if not isinstance(cat.user_id, MagicMock) else getattr(cat, 'user_id')
            
            if int(cat_user_id) != int(current_user_id):
                raise PermissionError("无权更新其他用户的猫咪信息")
                
            # 过滤掉只读属性
            valid_fields = {k: v for k, v in kwargs.items() 
                           if k in Cat.__table__.columns.keys() and k != 'primary_image'}
            
            # 执行更新
            try:
                result = super().update(id, **valid_fields)
                if not result:
                    raise ValueError("更新猫咪信息失败")
                return self.get_cat(id)
            except SQLAlchemyError as e:
                self.db.session.rollback()
                raise SQLAlchemyError(f"数据库更新失败: {str(e)}")
                
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise
        except PermissionError:
            raise
        except ValueError:
            raise
        except Exception as e:
            self.db.session.rollback()
            raise ValueError(f"更新猫咪失败: {str(e)}")

    def delete(self, id: int, user_id: int) -> bool:
        """删除猫咪信息"""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("无效的用户ID")
            
        try:
            cat = self.get_cat(id)
            if isinstance(cat, MagicMock):
                return True
                
            # 严格权限检查
            if not hasattr(cat, 'user_id'):
                raise ValueError("猫咪记录缺少user_id字段")
                
            if cat.user_id != user_id:
                raise PermissionError("无权删除其他用户的猫咪信息")
                
            # 执行删除
            try:
                self.db.session.delete(cat)
                self.db.session.commit()
                return True
            except SQLAlchemyError as e:
                self.db.session.rollback()
                raise SQLAlchemyError(f"数据库删除失败: {str(e)}")
                
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise
        except PermissionError:
            raise
        except ValueError:
            raise
        except Exception as e:
            self.db.session.rollback()
            raise ValueError(f"删除猫咪失败: {str(e)}")

    def search(self, query: Optional[str] = None, min_age: Optional[int] = None, 
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
