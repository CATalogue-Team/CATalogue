from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from api.config import settings
from api.base import Base

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_async_engine(
    DATABASE_URL,
    echo=True  # 添加echo参数便于调试
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

# 模型注册和表创建函数
async def create_tables():
    """创建所有数据库表"""
    import api.models.cat
    import api.models.user
    async with engine.begin() as conn:
        # 添加类型检查以确保conn是AsyncConnection
        if hasattr(conn, 'run_sync'):
            await conn.run_sync(Base.metadata.create_all)
        else:
            # 回退到直接执行
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
            await Base.metadata.create_all(conn)
    return Base.metadata.tables

# 模型注册函数
def register_models():
    """显式注册所有数据库模型"""
    import api.models.cat
    import api.models.user
    return Base.metadata.tables

# 获取数据库会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if not Base.metadata.tables:
        register_models()
    async with AsyncSessionLocal() as session:
        yield session

__all__ = ['AsyncSessionLocal', 'get_db']
