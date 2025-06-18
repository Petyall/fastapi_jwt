from typing import Any, Generic, Type, TypeVar, Optional, List
from sqlalchemy import delete, insert, select, update

from src.database import get_async_session


T = TypeVar("T")

class BaseRepository(Generic[T]):
    """Базовый репозиторий с CRUD-операциями"""

    model: Type[T]

    @classmethod
    async def find_by_id(cls, model_id: int) -> Optional[T]:
        async with get_async_session() as session:
            result = await session.execute(select(cls.model).filter_by(id=model_id))
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by: Any) -> Optional[T]:
        async with get_async_session() as session:
            result = await session.execute(select(cls.model).filter_by(**filter_by))
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by: Any) -> List[T]:
        async with get_async_session() as session:
            result = await session.execute(select(cls.model).filter_by(**filter_by))
            return result.scalars().all()

    @classmethod
    async def add(cls, **data: Any) -> Optional[T]:
        async with get_async_session() as session:
            query = insert(cls.model).values(**data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalars().one_or_none()

    @classmethod
    async def delete(cls, id: int) -> None:
        async with get_async_session() as session:
            async with session.begin():
                await session.execute(delete(cls.model).where(cls.model.id == id))
                await session.commit()

    @classmethod
    async def update(cls, id: int, **data: Any) -> Optional[T]:
        async with get_async_session() as session:
            query = update(cls.model).where(cls.model.id == id).values(**data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalars().one_or_none()
