from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from app.users.services import UserService
from app.config import settings


# Переменная с алгоритмами хеширования пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    # Возврат хэшированного пароля
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    # Проверка пароля на совпадение
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    # Копирование входных данных
    to_encode = data.copy()
    # Время со значением времени жизни токена
    expire = datetime.utcnow() + timedelta(minutes=30)
    # Добавление к токену времени его жизни
    to_encode.update({"exp": expire})
    # Создание токена
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, settings.ALGORITHM
    )
    # Возврат токена
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str):
    # Поиск пользователя
    user = await UserService.find_one_or_none(email=email)
    # Возврат ошибки если пользователя нет или пароль не подошел
    if not user or not verify_password(password, user.hashed_password):
        return None
    # Возврат пользователя
    return user
