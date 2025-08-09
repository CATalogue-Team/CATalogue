import pytest
import pytest_asyncio
import logging
from fastapi import status
from httpx import AsyncClient
from api.database import get_db, Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select
from uuid import uuid4

# 设置日志级别为INFO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from fastapi.testclient import TestClient
from api.database import AsyncSessionLocal
from api.auth import get_current_user, get_admin_user

@pytest_asyncio.fixture
async def client(db_session, test_user):
    # 创建新的应用实例
    from api.main import create_app
    test_app = create_app()
    
    # 覆盖app的数据库依赖
    def override_get_db():
        return db_session
        
    # 普通用户认证覆盖 - 使用夹具创建的测试用户
    async def override_get_current_user():
        return test_user
        
    # 管理员用户认证覆盖
    async def override_get_admin_user():
        from api.models.user_model import DBUser
        user = await DBUser.get_by_username(db_session, "admin_test")
        if not user:
            user = DBUser(
                id=uuid4(),  # 确保有ID
                username="admin_test",
                email="admin@example.com",
                full_name="Admin User",
                hashed_password="hashed_adminpassword123",
                is_admin=True  # 确保设置为True
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
        return user
        
    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = override_get_current_user
    test_app.dependency_overrides[get_admin_user] = override_get_admin_user
    
    async with AsyncClient(
        app=test_app,
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac
        
    # 清理覆盖
    test_app.dependency_overrides.clear()

# 测试数据工厂
@pytest_asyncio.fixture
async def test_cat_data():
    return {
        "name": "Test Cat",
        "breed": "Test Breed",
        "birth_date": "2025-01-01",
        "photos": [],
        "owner_id": "123e4567-e89b-12d3-a456-426614174000"
    }

@pytest_asyncio.fixture
async def test_user(db_session, test_user_data):
    """创建测试用户并返回"""
    from api.models.user_model import DBUser
    user = DBUser(
        username=test_user_data["username"],
        email=test_user_data["email"],
        full_name=test_user_data["full_name"],
        hashed_password=test_user_data["hashed_password"],
        is_admin=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def another_user(db_session, another_user_data):
    """创建另一个测试用户并返回"""
    from api.models.user_model import DBUser
    user = DBUser(
        username=another_user_data["username"],
        email=another_user_data["email"],
        full_name=another_user_data["full_name"],
        hashed_password=another_user_data["hashed_password"],
        is_admin=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_post(db_session, test_user, another_user):
    """测试帖子fixture"""
    from api.models.post import Post
    
    # 创建测试帖子，确保作者是test_user而不是another_user
    post = Post(
        title="测试帖子",
        content="测试内容",
        author_id=test_user.id
    )
    db_session.add(post)
    await db_session.commit()
    
    # 验证作者确实不是another_user
    assert str(post.author_id) != str(another_user.id), "测试帖子作者与another_user相同"
    return post

@pytest_asyncio.fixture
async def test_comment(db_session, test_post, another_user):
    """测试评论fixture"""
    from api.models.post import Comment
    
    # 创建测试评论，确保作者是test_post的作者而不是another_user
    comment = Comment(
        content="测试评论",
        post_id=test_post.id,
        author_id=test_post.author_id
    )
    db_session.add(comment)
    await db_session.commit()
    
    # 验证作者确实不是another_user
    assert str(comment.author_id) != str(another_user.id), "测试评论作者与another_user相同"
    return comment

# 通用断言函数
def assert_response_ok(response, expected_status=status.HTTP_200_OK):
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}"

def assert_response_error(response, expected_status):
    assert response.status_code == expected_status, \
        f"Expected error status {expected_status}, got {response.status_code}"

# 参数化测试数据
CAT_VALIDATION_CASES = [
    ("missing_name", {"breed": "Test"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("long_name", {"name": "A"*101}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("valid_data", {"name": "Valid"}, status.HTTP_201_CREATED)
]

@pytest_asyncio.fixture
async def db_session():
    # 使用测试数据库配置
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    # 确保创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建新的session工厂
    from sqlalchemy.ext.asyncio import async_sessionmaker
    TestingSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession
    )
    
    # 只创建空数据库
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

from api.auth import create_access_token

@pytest_asyncio.fixture
async def auth_headers(test_user):
    """普通用户认证头"""
    token = create_access_token(data={"sub": test_user.username})
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

@pytest_asyncio.fixture
async def admin_auth_headers(admin_user_data, db_session):
    """管理员认证头"""
    from api.models.user_model import DBUser
    
    # 确保管理员用户存在 - 使用唯一数据
    user = await DBUser.get_by_username(db_session, admin_user_data["username"])
    if not user:
        user = DBUser(
            username=admin_user_data["username"],
            email=admin_user_data["email"],
            full_name=admin_user_data["full_name"],
            hashed_password=admin_user_data["hashed_password"],
            is_admin=True  # 确保设置为True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
    
    token = create_access_token(data={"sub": admin_user_data["username"]})
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

@pytest_asyncio.fixture
async def another_auth_headers(another_user_data, db_session):
    """另一个普通用户认证头"""
    from api.models.user_model import DBUser
    
    # 确保用户存在 - 使用唯一数据
    user = await DBUser.get_by_username(db_session, another_user_data["username"])
    if not user:
        user = DBUser(
            username=another_user_data["username"],
            email=another_user_data["email"],
            full_name=another_user_data["full_name"],
            hashed_password=another_user_data["hashed_password"],
            is_admin=False
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
    
    token = create_access_token(data={"sub": another_user_data["username"]})
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

from pytest_mock import MockerFixture

@pytest.fixture
def mocker(pytestconfig) -> MockerFixture:
    return MockerFixture(pytestconfig)

@pytest.fixture
def test_user_data():
    """普通用户测试数据"""
    return {
        "username": f"testuser_{uuid4().hex[:8]}",
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "password": "testpassword123",
        "full_name": "API Test User",
        "hashed_password": "hashed_testpassword123",
        "is_admin": False
    }

@pytest.fixture
def admin_user_data():
    """管理员用户测试数据"""
    return {
        "username": f"admin_{uuid4().hex[:8]}",
        "email": f"admin_{uuid4().hex[:8]}@example.com",
        "password": "adminpassword123",
        "full_name": "Admin User",
        "hashed_password": "hashed_adminpassword123",
        "is_admin": True  # 确保设置为True
    }

@pytest.fixture
def another_user_data():
    """另一个普通用户测试数据"""
    return {
        "username": f"another_{uuid4().hex[:8]}",
        "email": f"another_{uuid4().hex[:8]}@example.com",
        "password": "anotherpassword123",
        "full_name": "Another User",
        "hashed_password": "hashed_anotherpassword123",
        "is_admin": False
    }
