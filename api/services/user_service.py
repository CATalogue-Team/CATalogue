from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from api.models.user import UserInDB, UserCreate, UserUpdate
from api.security import get_password_hash, verify_password, get_current_user
from fastapi import Depends
from api.database import get_db

class UserService:
    @staticmethod
    async def get_user(
        username: str,
        db: AsyncSession = Depends(get_db)
    ) -> Optional[UserInDB]:
        return await UserInDB.get(username)

    @staticmethod
    async def create_user(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
    ) -> UserInDB:
        hashed_password = get_password_hash(user.password)
        db_user = UserInDB(
            **user.dict(exclude={"password"}),
            hashed_password=hashed_password
        )
        await db_user.save(db)
        return db_user

    @staticmethod
    async def authenticate_user(
        username: str,
        password: str,
        db: AsyncSession = Depends(get_db)
    ) -> Optional[UserInDB]:
        user = await UserInDB.get(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def update_user(
        user_id: UUID,
        user_update: UserUpdate,
        current_user: UserInDB = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> Optional[UserInDB]:
        # 实现用户信息更新逻辑
        pass
