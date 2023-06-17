from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Путь до БД
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./database.db"

# Создание асинхронного движка
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Создание сессии работы с БД 
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Класс для наследоавния моделей и создания миграций
class Base(DeclarativeBase):
    pass
