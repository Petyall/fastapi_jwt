from sqlalchemy import delete, insert, select, update

from src.database import async_session_maker


class BaseRequests:
    """Базовый класс с запросами к БД"""

    model = None

    @classmethod
    async def find_by_id(cls, model_id: int):
        """Поиск одного объекта по id с проверкой на существование. Возвращает один объект или None"""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """Поиск одного объекта по фильтру с проверкой на существование. Возвращает один объект или None"""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        """Поиск объектов по фильтру. Возвращает список элементов"""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_last(cls):
        """Поиск последнего объекта. Возвращает один объект или None"""
        async with async_session_maker() as session:
            query = select(cls.model).order_by(cls.model.id.desc()).limit(1)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **data):
        """Добавление объектов"""
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()

            created_object = result.scalars().one_or_none()
            return created_object

    @classmethod
    async def delete(cls, id):
        """Удаление объектов"""
        async with async_session_maker() as session:
            async with session.begin():
                query = delete(cls.model).where(cls.model.id == id)
                await session.execute(query)
                await session.commit()

    @classmethod
    async def update(cls, id, **data):
        """Обновление объектов"""
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.id == id).values(**data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()

            updated_object = result.scalars().one_or_none()
            return updated_object

    @classmethod
    async def select_all_filter(cls, *args, **kwargs):
        """Выборка объектов по фильтру"""
        async with async_session_maker() as session:
            query = select(cls.model).filter(*args, **kwargs)
            result = await session.execute(query)
            return result.scalars().all()
