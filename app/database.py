from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

"""Настройка для SQLite"""
# # Путь до БД
# SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./database.db"

# # Создание асинхронного движка
# engine = create_async_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

# # Создание сессии работы с БД 
# async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# # Класс для наследоавния моделей и создания миграций
# class Base(DeclarativeBase):
#     pass


"""Настройка для PostgreSQL"""
engine = create_async_engine(settings.DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass