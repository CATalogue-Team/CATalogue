import asyncio
from api.database import create_tables
from api.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def init_postgres():
    print("Initializing PostgreSQL...")
    tables = await create_tables()
    print(f"Created tables: {list(tables.keys())}")
    return tables

async def init_mongo():
    print("Initializing MongoDB...")
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    
    # 初始化集合(如果不存在)
    collections = await db.list_collection_names()
    needed_collections = {"posts_content", "comments_content"}
    
    for col in needed_collections:
        if col not in collections:
            await db.create_collection(col)
            print(f"Created collection: {col}")
    
    print(f"Existing collections: {await db.list_collection_names()}")
    return db

async def main():
    print("Starting database initialization...")
    postgres_tables = await init_postgres()
    mongo_db = await init_mongo()
    print("Database initialization completed")

if __name__ == "__main__":
    asyncio.run(main())
