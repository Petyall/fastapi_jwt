from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(ForeignKey("roles.id"), default=1)

    # Создание отношения для SQLAlchemy
    role = relationship("Role", back_populates="users")

    # Фукнция переопределяющая отображения названия модели
    def __str__(self):
        return f"Пользователь {self.email}"
    

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)

    users = relationship("Users", back_populates="role")

    # Фукнция переопределяющая отображения названия модели
    def __str__(self):
        return f"Пользователь {self.email}"