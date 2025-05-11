
from typing import List, Optional, Type
from .. import db
from ..models import User
from .base_service import BaseService

class UserService(BaseService):
    """用户服务层"""
    def __init__(self, db):
        super().__init__(db)
        
    model = User  # 定义模型类
    
    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        """获取单个用户信息"""
        return BaseService.get(User, user_id)
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_pending_users() -> List[User]:
        """获取待审批用户列表"""
        return User.query.filter_by(status='pending').all()
    
    @staticmethod
    def get_all_users() -> List[User]:
        """获取所有用户"""
        return User.query.all()
        
    @staticmethod
    def get_paginated_users(page: int = 1, per_page: int = 10, search: str = None):
        """
        获取分页用户列表
        参数:
            page: 当前页码
            per_page: 每页记录数
            search: 搜索关键词(用户名)
        返回:
            SQLAlchemy分页对象
        """
        query = User.query.order_by(User.created_at.desc())
        
        if search:
            query = query.filter(User.username.ilike(f'%{search}%'))
            
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def create_user(password: str, **kwargs) -> User:
        """
        创建用户账号
        参数:
            password: 明文密码
            **kwargs: 其他用户属性
        """
        if 'password' in kwargs:
            raise ValueError("请使用password参数而不是kwargs传递密码")
            
        user = User(**kwargs)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def approve_user(user_id: int, approved_by: int) -> bool:
        """审批用户账号"""
        if user_id == approved_by:
            return False
            
        user = User.query.get(user_id)
        if not user:
            return False
            
        user.status = 'approved'
        user.approved_by = approved_by
        BaseService.update(User, user_id, status='approved', approved_by=approved_by)
        return True
    
    @staticmethod
    def reject_user(user_id: int, current_user_id: int = None) -> bool:
        """拒绝用户账号"""
        if current_user_id and user_id == current_user_id:
            return False
            
        user = User.query.get(user_id)
        if not user:
            return False
            
        user.status = 'rejected'
        BaseService.update(User, user_id, status='rejected')
        return True
    
    @staticmethod
    def update_user_role(user_id: int, is_admin: bool, current_user_id: int = None) -> bool:
        """更新用户角色"""
        if current_user_id and user_id == current_user_id:
            return False
        return BaseService.update(User, user_id, is_admin=is_admin) is not None
    
    @staticmethod
    def delete_user(user_id: int, current_user_id: int = None) -> bool:
        """删除用户"""
        if current_user_id and user_id == current_user_id:
            return False
        return BaseService.delete(User, user_id)
