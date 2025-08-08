import pytest
from fastapi import status
from uuid import UUID
from unittest.mock import AsyncMock
from api.services.user_service import UserService
from api.models.user import UserInDB, UserCreate, UserUpdate
from passlib.context import CryptContext

class TestUserService:
    @pytest.mark.asyncio
    async def test_create_user_with_password_hashing(self, mocker):
        """测试创建用户时密码哈希处理"""
        # 准备测试数据
        test_password = "securepassword123"
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password=test_password
        )
        
        # Mock数据库和UserInDB
        mock_db = AsyncMock()
        mock_user = UserInDB(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # 模拟bcrypt哈希后的密码
        )
        mocker.patch.object(UserInDB, "save", return_value=mock_user)
        
        # Mock passlib的CryptContext
        mock_pwd_context = mocker.MagicMock()
        mock_pwd_context.hash.return_value = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
        mock_pwd_context.verify.return_value = True
        mocker.patch(
            "passlib.context.CryptContext",
            return_value=mock_pwd_context
        )
        
        # 测试
        service = UserService(mock_db)
        created_user = await service.create_user(user_data)
        
        # 验证
        assert created_user.username == user_data.username
        assert created_user.hashed_password != test_password  # 密码应被哈希
        assert created_user.hashed_password.startswith("$2b$")  # bcrypt哈希格式

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, mocker):
        """测试用户认证成功"""
        # 准备测试数据
        test_password = "securepassword123"
        
        # Mock数据库返回用户
        mock_db = AsyncMock()
        mock_user = UserInDB(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # 模拟bcrypt哈希后的密码
        )
        mocker.patch.object(UserInDB, "get", return_value=mock_user)
        
        # Mock passlib的CryptContext
        mock_pwd_context = mocker.MagicMock()
        mock_pwd_context.verify.return_value = True
        mocker.patch(
            "passlib.context.CryptContext",
            return_value=mock_pwd_context
        )
        
        # 测试
        service = UserService(mock_db)
        authenticated_user = await service.authenticate_user(
            username="testuser",
            password=test_password
        )
        
        # 验证
        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"
        mock_pwd_context.verify.assert_called_once_with(test_password, mock_user.hashed_password)

    @pytest.mark.asyncio
    async def test_authenticate_user_failure(self, mocker):
        """测试用户认证失败"""
        # Mock数据库返回None(用户不存在)
        mock_db = AsyncMock()
        mocker.patch.object(UserInDB, "get", return_value=None)
        
        # 测试
        service = UserService(mock_db)
        authenticated_user = await service.authenticate_user(
            username="nonexistent",
            password="wrongpassword"
        )
        
        # 验证
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_update_user_password_hashing(self, mocker):
        """测试更新用户密码时哈希处理"""
        # 准备测试数据
        user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        new_password = "newsecurepassword123"
        current_user = UserInDB(
            id=user_id,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="oldhash"
        )
        
        # Mock数据库
        mock_db = AsyncMock()
        mocker.patch.object(UserInDB, "get_by_id", return_value=current_user)
        
        # 测试
        service = UserService(mock_db)
        updated_user = await service.update_user(
            user_id=user_id,
            user_update=UserUpdate(password=new_password),
            current_user=current_user
        )
        
        # 验证
        assert updated_user is not None
        assert updated_user.hashed_password != new_password  # 密码应被哈希
        assert updated_user.hashed_password.startswith("$2b$")  # bcrypt哈希格式

    @pytest.mark.asyncio
    async def test_reset_password_hashing(self, mocker):
        """测试重置密码时哈希处理"""
        # 准备测试数据
        user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        new_password = "resetpassword123"
        mock_user = UserInDB(
            id=user_id,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="oldhash"
        )
        
        # Mock数据库
        mock_db = AsyncMock()
        mocker.patch.object(UserInDB, "get_by_id", return_value=mock_user)
        
        # 测试
        service = UserService(mock_db)
        result = await service.reset_password(
            token=f"reset_token_{user_id}",
            new_password=new_password
        )
        
        # 验证
        assert result is True
        assert mock_user.hashed_password != new_password  # 密码应被哈希
        assert mock_user.hashed_password.startswith("$2b$")  # bcrypt哈希格式

    @pytest.mark.asyncio
    async def test_update_user_permission_check(self, mocker):
        """测试更新用户时的权限检查"""
        # 准备测试数据
        user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        other_user_id = UUID("223e4567-e89b-12d3-a456-426614174000")
        current_user = UserInDB(
            id=user_id,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hash"
        )
        
        # Mock数据库
        mock_db = AsyncMock()
        
        # 测试
        service = UserService(mock_db)
        with pytest.raises(PermissionError) as excinfo:
            await service.update_user(
                user_id=other_user_id,
                user_update=UserUpdate(
                    full_name="New Name",
                    email=None,
                    password=None
                ),
                current_user=current_user
            )
        
        # 验证
        assert "无权更新其他用户信息" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_update_user_success(self, mocker):
        """测试成功更新用户信息"""
        # 准备测试数据
        user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        current_user = UserInDB(
            id=user_id,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hash"
        )
        
        # Mock数据库
        mock_db = AsyncMock()
        mocker.patch.object(UserInDB, "get_by_id", return_value=current_user)
        
        # 测试
        service = UserService(mock_db)
        updated_user = await service.update_user(
            user_id=user_id,
            user_update=UserUpdate(
                full_name="New Name",
                email=None,
                password=None
            ),
            current_user=current_user
        )
        
        # 验证
        assert updated_user is not None
        assert updated_user.full_name == "New Name"
        mock_db.commit.assert_awaited_once()
