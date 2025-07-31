import pytest
from uuid import uuid4
from datetime import datetime
from api.models.user import UserInDB

@pytest.mark.asyncio
async def test_user_model_crud(test_db_session):
    """测试用户模型CRUD操作"""
    # 创建测试用户
    user = UserInDB(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        full_name=None,
        disabled=False
    )

    # 测试创建
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    assert user.id is not None

    # 测试查询
    queried_user = await test_db_session.get(UserInDB, user.id)
    assert queried_user.username == "testuser"

    # 测试更新
    queried_user.full_name = "Test User"
    await test_db_session.commit()
    await test_db_session.refresh(queried_user)
    assert queried_user.full_name == "Test User"

    # 测试删除
    await test_db_session.delete(queried_user)
    await test_db_session.commit()
    deleted_user = await test_db_session.get(UserInDB, user.id)
    assert deleted_user is None
