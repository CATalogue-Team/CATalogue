import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID, uuid4
from datetime import datetime
from api.models.user import (
    UserBase,
    UserCreate,
    UserInDB,
    Token,
    TokenData,
    UserUpdate,
    PasswordResetRequest,
    PasswordResetConfirm
)
from api.models.user_model import DBUser
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def sample_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123",
        "hashed_password": "hashed_testpassword123",
        "disabled": False,
        "is_admin": False
    }

@pytest.mark.asyncio
async def test_user_create_model(sample_user_data):
    """测试用户创建模型验证"""
    user = UserCreate(**sample_user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "testpassword123"

@pytest.mark.asyncio
async def test_user_in_db_model(sample_user_data):
    """测试数据库用户模型"""
    user_id = uuid4()
    user = UserInDB(
        id=user_id,
        **sample_user_data
    )
    assert user.id == user_id
    assert user.hashed_password == "hashed_testpassword123"
    assert user.disabled is False

@pytest.mark.asyncio
async def test_user_get_by_username(mock_db_session, sample_user_data):
    """测试通过用户名获取用户"""
    user_id = uuid4()
    
    # 创建真实对象代替Mock
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("testpassword123")
    
    user_dict = {
        "id": user_id,
        "username": sample_user_data["username"],
        "email": sample_user_data["email"],
        "full_name": sample_user_data["full_name"],
        "hashed_password": hashed_password,
        "disabled": sample_user_data["disabled"],
        "is_admin": sample_user_data["is_admin"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    real_user = DBUser(**user_dict)
    
    # 确保返回的模拟对象属性是直接值而不是协程
    mock_result = MagicMock()
    mock_result.scalar.return_value = real_user
    mock_db_session.execute.return_value = mock_result
    
    user = await UserInDB.get("testuser", mock_db_session)
    assert user is not None
    assert user.username == "testuser"
    assert isinstance(user.id, UUID)

@pytest.mark.asyncio
async def test_user_get_by_id(mock_db_session, sample_user_data):
    """测试通过ID获取用户"""
    user_id = uuid4()
    
    # 创建真实对象代替Mock
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("testpassword123")
    
    user_dict = {
        "id": user_id,
        "username": sample_user_data["username"],
        "email": sample_user_data["email"],
        "full_name": sample_user_data["full_name"],
        "hashed_password": hashed_password,
        "disabled": sample_user_data["disabled"],
        "is_admin": sample_user_data["is_admin"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    real_user = DBUser(**user_dict)
    
    # 确保返回的模拟对象属性是直接值而不是协程
    mock_result = MagicMock()
    mock_result.scalar.return_value = real_user
    mock_db_session.execute.return_value = mock_result
    
    user = await UserInDB.get_by_id(user_id, mock_db_session)
    assert user is not None
    assert user.id == user_id

@pytest.mark.asyncio
async def test_user_authentication_success(mock_db_session, sample_user_data):
    """测试用户认证成功"""
    user_id = uuid4()

    # 创建真实对象代替Mock
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("testpassword123")
    
    user_dict = {
        "id": user_id,
        "username": sample_user_data["username"],
        "email": sample_user_data["email"],
        "full_name": sample_user_data["full_name"],
        "hashed_password": hashed_password,
        "disabled": sample_user_data["disabled"],
        "is_admin": sample_user_data["is_admin"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    real_user = DBUser(**user_dict)

    # 直接返回真实对象而不是协程
    mock_db_session.execute.return_value.scalar = lambda: real_user

    user = await UserInDB.authenticate(
        "testuser",
        "testpassword123",
        mock_db_session
    )
    assert user is not None
    assert UserInDB.verify_password("testpassword123", user.hashed_password)

@pytest.mark.asyncio
async def test_user_authentication_failure(mock_db_session):
    """测试用户认证失败"""
    # 直接返回None而不是协程
    mock_db_session.execute.return_value.scalar = lambda: None

    user = await UserInDB.authenticate(
        "wronguser",
        "wrongpassword",
        mock_db_session
    )
    assert user is None

@pytest.mark.asyncio
async def test_password_reset_flow(mock_db_session, sample_user_data):
    """测试密码重置流程"""
    # 生成重置token
    token = await UserInDB.generate_password_reset_token(
        "test@example.com", 
        mock_db_session
    )
    assert token == "reset_token_123"
    
    # 重置密码
    result = await UserInDB.reset_password(
        token,
        "newpassword123",
        mock_db_session
    )
    assert result is True

@pytest.mark.asyncio
async def test_user_update(mock_db_session, sample_user_data):
    """测试用户更新"""
    user_id = uuid4()
    mock_user = MagicMock(spec=DBUser)
    mock_user.id = user_id
    mock_user.username = sample_user_data["username"]
    mock_user.email = sample_user_data["email"]
    mock_user.full_name = sample_user_data["full_name"]
    mock_user.hashed_password = sample_user_data["hashed_password"]
    mock_user.disabled = sample_user_data["disabled"]
    mock_user.is_admin = sample_user_data["is_admin"]
    
    # 直接返回mock_user而不是协程
    mock_db_session.execute.return_value.scalar = lambda: mock_user

    user = await UserInDB.get("testuser", mock_db_session)
    assert user is not None  # 确保 user 不为 None
    update_data = UserUpdate(
        email="newemail@example.com",
        full_name="Updated Name",
        password="newpassword123"
    )
    updated_user = await user.update(update_data, mock_db_session)
    assert updated_user is not None
    assert updated_user.email == "newemail@example.com"
    assert updated_user.full_name == "Updated Name"

@pytest.mark.asyncio
async def test_user_delete(mock_db_session, sample_user_data):
    """测试用户删除"""
    user_id = uuid4()
    mock_user = MagicMock(spec=DBUser)
    mock_user.id = user_id
    mock_user.username = sample_user_data["username"]
    mock_user.email = sample_user_data["email"]
    mock_user.full_name = sample_user_data["full_name"]
    mock_user.hashed_password = sample_user_data["hashed_password"]
    mock_user.disabled = sample_user_data["disabled"]
    mock_user.is_admin = sample_user_data["is_admin"]
    
    # 直接返回mock_user而不是协程
    mock_db_session.execute.return_value.scalar = lambda: mock_user

    user = await UserInDB.get("testuser", mock_db_session)
    assert user is not None
    await user.delete(mock_db_session)
    assert mock_db_session.delete.called
    assert mock_db_session.commit.called
