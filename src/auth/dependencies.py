from src.auth.jwt_handler import jwt_handler
from src.auth.services import UserRequests
from fastapi import Request, Depends


async def get_access_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        token = request.headers.get("authorization")
    if not token:
        return("Токен не найден")
    return token


async def get_refresh_token(request: Request) -> str:
    token = request.cookies.get("refresh_token")
    return token

async def get_current_user(token: str = Depends(get_access_token)):
    try:
        payload = await jwt_handler.decode_token(token)
    except Exception as e:
        raise e

    user_email = payload.get("sub")
    user = await UserRequests.find_one_or_none(email = user_email)
    if not user:
        return "пользователь не найден"  

    return user


async def check_is_current_user_admin(user = Depends(get_current_user)):
    if user.role_title != "ADMIN":
        return("Недостаточно прав")
    return user
