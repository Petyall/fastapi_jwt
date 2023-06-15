from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker



SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./database.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# Создание сессии работы с БД (работает по типу транзакции, т.е. если началось
# какое-то действие, то оно должно завершиться. если этого не произошло, то происходит откат)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# Класс для наследоавния моделей и создания миграций
class Base(DeclarativeBase):
    pass
