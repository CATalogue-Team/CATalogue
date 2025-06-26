from typing import List, Optional
from ..models import User
from .base_service import BaseService
from werkzeug.security import generate_password_hash

class UserService(BaseService):
    """用户服务类"""
    def __init__(self, db):
        super().__init__(db, User)
        
    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return self.db.query(self.model).filter_by(username=username).first()
    
    def get_pending_users(self) -> List[User]:
        """获取待审批用户列表"""
        return self.db.query(self.model).filter_by(status='pending').all()
    
    def get_all_users(self) -> List[User]:
        """获取所有用户"""
        return self.db.query(self.model).all()
        
    def create_user(self, username: str, password: str, **kwargs) -> User:
        """创建用户账号"""
        if not username or not password:
            raise ValueError("用户名和密码不能为空")
            
        if self.get_user_by_username(username):
            raise ValueError("用户名已存在")
            
        user = User(username=username, **kwargs)
        user.set_password(password)
        self.db.session.add(user)
        self.db.session.commit()
        return user
    
    def approve_user(self, user_id: int, approved_by: int) -> bool:
        """审批用户账号"""
        if user_id == approved_by:
            return False
            
        user = self.get(user_id)
        if not user:
            return False
            
        user.status = 'approved'
        user.approved_by = approved_by
        self.db.session.commit()
        return True
    
    def reject_user(self, user_id: int, current_user_id: Optional[int] = None) -> bool:
        """拒绝用户账号"""
        if current_user_id and user_id == current_user_id:
            return False
            
        user = self.get(user_id)
        if not user:
            return False
            
        user.status = 'rejected'
        self.db.session.commit()
        return True
    
    def update_user_role(self, user_id: int, is_admin: bool, current_user_id: Optional[int] = None) -> bool:
        """更新用户角色"""
        if current_user_id and user_id == current_user_id:
            return False
        return self.update(user_id, is_admin=is_admin) is not None
    
    def delete_user(self, user_id: int, current_user_id: Optional[int] = None) -> bool:
        """删除用户"""
        if current_user_id and user_id == current_user_id:
            return False
        return self.delete(user_id)
