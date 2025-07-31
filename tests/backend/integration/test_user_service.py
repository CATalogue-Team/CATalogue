import pytest
from uuid import uuid4
from datetime import datetime
from api.services.user_service import UserService
from api.models.user import UserInDB, UserCreate

@pytest.mark.asyncio
async def test_user_service_integration(test_db_session):
    """测试用户服务集成"""
    # 测试用户创建
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="validpassword123"
    )
    
    created_user = await UserService.create_user(user_data, test_db_session)
    assert created_user.username == "testuser"
    assert created_user.email == "test@example.com"
    assert hasattr(created_user, "hashed_password")

    # 测试用户认证
    authenticated_user = await UserService.authenticate_user(
        "testuser", 
        "validpassword123",
        test_db_session
    )
    assert authenticated_user is not None
    assert authenticated_user.username == "testuser"

    # 测试错误密码
    failed_auth = await UserService.authenticate_user(
        "testuser",
        "wrongpassword",
        test_db_session
    )
    assert failed_auth is None

    # 清理测试数据
    await test_db_session.delete(created_user)
    await test_db_session.commit()
