from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from api.models.user import UserInDB, UserCreate, UserUpdate
from fastapi import Depends
from api.database import get_db

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, username: str) -> Optional[UserInDB]:
        return await UserInDB.get(username, self.db)

    async def create_user(self, user: UserCreate) -> UserInDB:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        db_user = UserInDB(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=pwd_context.hash(user.password)
        )
        return await db_user.save(self.db)

    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[UserInDB]:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        user = await UserInDB.get(username, self.db)
        if not user or not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    async def update_user(
        self,
        user_id: UUID,
        user_update: UserUpdate,
        current_user: UserInDB
    ) -> Optional[UserInDB]:
        """更新用户信息"""
        # 验证当前用户权限
        if str(current_user.id) != str(user_id):
            raise PermissionError("无权更新其他用户信息")

        # 获取要更新的用户
        user = await UserInDB.get_by_id(user_id, self.db)
        if not user:
            return None

        # 更新字段
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        if user_update.password is not None:
            user.hashed_password = pwd_context.hash(user_update.password)

        # 保存更新
        await self.db.commit()
        return user

    async def delete_user(self, user_id: UUID) -> bool:
        """删除用户"""
        user = await UserInDB.get_by_id(user_id, self.db)
        if not user:
            return False
            
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def generate_password_reset_token(self, email: str) -> str:
        """生成密码重置令牌"""
        # 简化实现，实际应使用JWT等安全机制
        user = await UserInDB.get_by_email(email, self.db)
        if not user:
            raise ValueError("Email not registered")
            
        return f"reset_token_{user.id}"

    async def reset_password(self, token: str, new_password: str) -> bool:
        """重置密码"""
        if not token.startswith("reset_token_"):
            raise ValueError("Invalid token format")
            
        user_id = token.split("_")[-1]
        try:
            uuid_obj = UUID(user_id)
            user = await UserInDB.get_by_id(uuid_obj, self.db)
            if not user:
                raise ValueError("Invalid token")
                
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            user.hashed_password = pwd_context.hash(new_password)
            await self.db.commit()
            return True
        except ValueError:
            raise ValueError("Invalid token format")

    async def send_reset_email(self, email: str, token: str) -> bool:
        """发送密码重置邮件(模拟实现)"""
        return True
