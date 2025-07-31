import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from api.services.user_service import UserService
from api.models.user import UserInDB, UserCreate

class TestUserService:
    @pytest.mark.asyncio
    async def test_create_user(self):
        """测试用户创建服务"""
        mock_db = AsyncMock()
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="validpassword123"
        )
        
        # 模拟数据库返回
        from datetime import datetime
        mock_user = UserInDB(
            id=uuid4(),
            username=user_data.username,
            email=user_data.email,
            hashed_password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            full_name=None,
            disabled=False
        )
        mock_db.execute.return_value = mock_user

        result = await UserService.create_user(user_data, mock_db)
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert hasattr(result, "hashed_password")

    @pytest.mark.asyncio
    async def test_authenticate_user(self):
        """测试用户认证服务"""
        mock_db = AsyncMock()
        username = "testuser"
        password = "validpassword123"
        
        # 模拟正确密码情况
        from datetime import datetime
        mock_user = UserInDB(
            id=uuid4(),
            username=username,
            email="test@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # bcrypt hash of "secret"
            created_at=datetime.now(),
            updated_at=datetime.now(),
            full_name=None,
            disabled=False
        )
        UserInDB.get = AsyncMock(return_value=mock_user)
        
        authenticated_user = await UserService.authenticate_user(username, password, mock_db)
        assert authenticated_user is not None
        assert authenticated_user.username == username

        # 测试用户不存在情况
        UserInDB.get = AsyncMock(return_value=None)
        assert await UserService.authenticate_user("nonexistent", "anypassword", mock_db) is None

        # 测试密码错误情况
        mock_user = UserInDB(
            id=uuid4(),
            username=username,
            email="test@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            full_name=None,
            disabled=False
        )
        UserInDB.get = AsyncMock(return_value=mock_user)
        assert await UserService.authenticate_user(username, "wrongpassword", mock_db) is None
