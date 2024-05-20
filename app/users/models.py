from uuid import uuid4
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Users(Base):
    # Название таблицы
    __tablename__ = "users"

    # Поля
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    # id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(ForeignKey("roles.id"), default=1)
    # uuid = Column(String())
    # uuid = Column(String, default=str(uuid4()))
    is_confirmed = Column(Boolean())
    confirmation_sent = Column(DateTime())
    confirmation_date = Column(DateTime())

    # Создание отношения для SQLAlchemy
    role = relationship("Role", back_populates="users")

    # Фукнция переопределяющая отображения названия модели
    def __str__(self):
        return f"Пользователь {self.email}"
    

class Role(Base):
    # Название таблицы
    __tablename__ = "roles"

    # Поля
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)

    # Создание отношения для SQLAlchemy
    users = relationship("Users", back_populates="role")

    # Фукнция переопределяющая отображения названия модели
    def __str__(self):
        return f"{self.name}"
    