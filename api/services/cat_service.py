from typing import Sequence, Optional, AsyncGenerator
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, true
from sqlalchemy.sql.expression import bindparam
from ..models.cat import DBCat as Cat
from ..database import AsyncSessionLocal, get_db

class CatService:
    @staticmethod
    async def get_all_cats() -> Sequence[Cat]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Cat))
            return result.scalars().all()

    @staticmethod
    async def get_cat_by_id(cat_id: UUID) -> Optional[Cat]:
        async with AsyncSessionLocal() as session:
            stmt = select(Cat).where(Cat.id == cat_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    @staticmethod
    async def create_cat(cat_data: dict) -> Cat:
        async with AsyncSessionLocal() as session:
            cat = Cat(**cat_data)
            session.add(cat)
            await session.commit()
            await session.refresh(cat)
            return cat

    @staticmethod
    async def update_cat(cat_id: UUID, cat_data: dict) -> Optional[Cat]:
        async with AsyncSessionLocal() as session:
            stmt = select(Cat).where(Cat.id == cat_id)
            result = await session.execute(stmt)
            cat = result.scalars().first()
            if cat:
                for key, value in cat_data.items():
                    setattr(cat, key, value)
                await session.commit()
                await session.refresh(cat)
            return cat

    @staticmethod
    async def delete_cat(cat_id: UUID) -> bool:
        async with AsyncSessionLocal() as session:
            stmt = select(Cat).where(Cat.id == cat_id)
            result = await session.execute(stmt)
            cat = result.scalars().first()
            if cat:
                await session.delete(cat)
                await session.commit()
                return True
            return False
