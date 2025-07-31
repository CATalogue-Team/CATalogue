import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from api.config import settings

@pytest.fixture
async def test_db_session():
    # 使用测试数据库配置
    TEST_DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/test_{settings.DB_NAME}"
    
    engine = create_async_engine(TEST_DATABASE_URL)
    TestingSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False
    )

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
