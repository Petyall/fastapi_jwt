from datetime import datetime
from fastapi import Request, Depends
from jose import jwt, JWTError

from app.users.services import UserService
from app.config import settings
from app.exceptions import TokenAbsentException, IncorrectFormatTokenException, TokenExpiredException, UserIsNotPresentException 


def get_token(request: Request):
    # Получение токена из cookie
    token = request.cookies.get("access_token")
    # Возврат ошибки, если токена нет
    if not token:
        raise TokenAbsentException
    # Возврат токена
    return token


async def get_uuid(email: str):
    # Попытка найти пользователя в БД
    user = await UserService.find_one_or_none(email=email)
    # Возврат ошибки, если пользователя нет
    if not user:
        raise UserIsNotPresentException 
    # Возврат UUID
    return user.uuid


async def get_current_user(token: str = Depends(get_token)):
    # Попытка расшифровать токен
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    # Возврат ошибки, если с токеном что-то не так
    except JWTError:
        raise IncorrectFormatTokenException
    # Получение времени действия токена
    expire: str = payload.get("exp")
    # Возврат ошибки, если время действия токена превратилось
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpiredException
    # Получение id пользователя
    user_id: str = payload.get("sub")
    # Возврат ошибки, если id пользователя не указан
    if not user_id:
        raise UserIsNotPresentException 
    # Поиск пользователя в БД по id
    user = await UserService.find_by_id(int(user_id))
    # Возврат ошибки, если пользователя нет
    if not user:
        raise UserIsNotPresentException  
    # Возврат пользователя
    return user
