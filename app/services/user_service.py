
from typing import List, Optional
from ..models import User
from .base_service import BaseService

class UserService(BaseService):
    """用户服务层"""
    
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
    def create_user(**kwargs) -> User:
        """创建用户账号"""
        return BaseService.create(User, **kwargs)
    
    @staticmethod
    def approve_user(user_id: int, approved_by: int) -> bool:
        """审批用户账号"""
        user = User.query.get(user_id)
        if not user:
            return False
            
        user.status = 'approved'
        user.approved_by = approved_by
        BaseService.update(User, user_id, status='approved', approved_by=approved_by)
        return True
    
    @staticmethod
    def reject_user(user_id: int) -> bool:
        """拒绝用户账号"""
        user = User.query.get(user_id)
        if not user:
            return False
            
        user.status = 'rejected'
        BaseService.update(User, user_id, status='rejected')
        return True
    
    @staticmethod
    def update_user_role(user_id: int, is_admin: bool) -> bool:
        """更新用户角色"""
        return BaseService.update(User, user_id, is_admin=is_admin) is not None
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """删除用户"""
        return BaseService.delete(User, user_id)
