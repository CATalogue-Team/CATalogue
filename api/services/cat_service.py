from typing import Sequence, Optional, AsyncGenerator
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, true
from sqlalchemy.sql.expression import bindparam
from ..models.cat import DBCat as Cat, DBCat
from ..schemas.cat import CatCreate as SchemaCatCreate
from ..database import AsyncSessionLocal, get_db

class CatService:
    @staticmethod
    async def get_all_cats() -> Sequence[Cat]:
        async with AsyncSessionLocal() as session:
            stmt = select(Cat)
            result = await session.execute(stmt)
            return list(result.scalars())

    @staticmethod
    async def get_cat_by_id(cat_id: UUID) -> Optional[Cat]:
        async with AsyncSessionLocal() as session:
            stmt = select(Cat).where(Cat.id == cat_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @staticmethod
    async def create_cat(cat_data: SchemaCatCreate) -> Cat:
        async with AsyncSessionLocal() as session:
            cat_data_dict = cat_data.model_dump()
            db_cat_data = {
                'name': cat_data_dict['name'],
                'breed': cat_data_dict['breed'],
                'birth_date': cat_data_dict['birth_date'],
                'owner_id': cat_data_dict['owner_id']
            }
            cat = DBCat(**db_cat_data)
            session.add(cat)
            await session.commit()
            await session.refresh(cat)
            return cat

    @staticmethod
    async def update_cat(cat_id: UUID, cat_data: dict) -> Optional[Cat]:
        async with AsyncSessionLocal() as session:
            stmt = select(Cat).where(Cat.id == cat_id)
            result = await session.execute(stmt)
            cat = result.scalar_one_or_none()
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
            cat = result.scalar_one_or_none()
            if cat:
                await session.delete(cat)
                await session.commit()
                return True
            return False

    @staticmethod
    async def upload_photos(cat_id: UUID, files: list) -> dict:
        """上传猫咪照片"""
        try:
            # 这里实现实际的照片上传逻辑
            # 返回上传结果
            return {
                "cat_id": str(cat_id),
                "file_count": len(files),
                "filenames": [file.filename for file in files]
            }
        except OSError as e:
            if "No space left on device" in str(e):
                raise OSError("No space left on device") from e
            raise Exception("Storage service unavailable") from e
        except Exception as e:
            raise Exception("Storage service unavailable") from e
