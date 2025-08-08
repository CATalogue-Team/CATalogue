import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from api.database import get_db, Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from uuid import uuid4

from fastapi.testclient import TestClient
from api.database import AsyncSessionLocal

@pytest_asyncio.fixture
async def client(db_session):
    # 创建新的应用实例
    from api.main import create_app
    test_app = create_app()
    
    # 覆盖app的数据库依赖
    def override_get_db():
        return db_session
        
    test_app.dependency_overrides[get_db] = override_get_db
    
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

@pytest.fixture
def auth_headers():
    # 返回测试用的认证头
    return {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }

from pytest_mock import MockerFixture

@pytest.fixture
def mocker(pytestconfig) -> MockerFixture:
    return MockerFixture(pytestconfig)

@pytest.fixture
def test_user_data():
    return {
        "username": f"testuser_{uuid4().hex[:8]}",
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "password": "testpassword123",
        "full_name": "API Test User",
        "hashed_password": "hashed_testpassword123"
    }
