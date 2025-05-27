from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class Role(Base):
    __tablename__ = "roles"

    title: Mapped[str] = mapped_column(String(50), primary_key=True)

    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(512))
    registration_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    last_activity: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Поля, которые можно удалить, в зависимости от нужды проекта
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    paternal_name: Mapped[str] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    birthday: Mapped[date] = mapped_column(Date, nullable=True)

    ban: Mapped[bool] = mapped_column(Boolean, default=False)
    ban_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    role_title: Mapped[str] = mapped_column(ForeignKey("roles.title"))
    role: Mapped["Role"] = relationship(back_populates="users")
