from sqlalchemy import select, insert, update

from app.users.models import Users
from app.database import async_session_maker


class UserService():
    model = Users
    
    # Поиск чего-либо по id
    @classmethod
    async def find_by_id(cls, model_id: int):
        # Создание сессии для работы с БД
        async with async_session_maker() as session:
            # Выборка данных из БД по фильтру
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return(result.scalar_one_or_none())
        

    # Добавление чего-либо
    @classmethod
    async def add(cls, **data):
        # Создание сессии для работы с БД
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()


    # Обновление значений у пользователя
    @classmethod
    async def update_user(cls, email, **data):
        # Создание сессии для работы с БД
        async with async_session_maker() as session:
            table = cls.model
            query = update(table).where(table.email==email).values(**data)
            await session.execute(query)
            await session.commit()


    # Поиск чего-либо по фильтру с проверкой на существование
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        # Создание сессии для работы с БД
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return(result.scalar_one_or_none())


    # Поиск чего-либо по фильтру
    @classmethod
    async def find_all(cls, **filter_by):
        # Создание сессии для работы с БД
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return(result.scalars().all())