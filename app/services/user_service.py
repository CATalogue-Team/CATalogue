
from typing import List, Optional
from ..models import User
from .. import db

class UserService:
    """用户服务层"""
    
    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        """获取单个用户信息"""
        return User.query.get(user_id)
    
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
    def create_user(username: str, password: str, is_admin: bool = False) -> User:
        """创建用户账号"""
        user = User(
            username=username,
            password=password,
            is_admin=is_admin,
            status='pending'
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def approve_user(user_id: int, approved_by: int) -> bool:
        """审批用户账号"""
        user = User.query.get(user_id)
        if not user:
            return False
            
        user.status = 'approved'
        user.approved_by = approved_by
        db.session.commit()
        return True
    
    @staticmethod
    def reject_user(user_id: int) -> bool:
        """拒绝用户账号"""
        user = User.query.get(user_id)
        if not user:
            return False
            
        user.status = 'rejected'
        db.session.commit()
        return True
    
    @staticmethod
    def update_user_role(user_id: int, is_admin: bool) -> bool:
        """更新用户角色"""
        user = User.query.get(user_id)
        if not user:
            return False
            
        user.is_admin = is_admin
        db.session.commit()
        return True
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """删除用户"""
        user = User.query.get(user_id)
        if not user:
            return False
            
        db.session.delete(user)
        db.session.commit()
        return True
