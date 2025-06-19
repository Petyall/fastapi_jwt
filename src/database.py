from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.config import settings


# Создание асинхронного движка SQLAlchemy для подключения к базе данных
engine = create_async_engine(settings.DATABASE_URL)

# Фабрика сессий для создания асинхронных сессий SQLAlchemy
get_async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Используется для определения общей структуры моделей и их маппинга на таблицы базы данных.
    """
    pass
