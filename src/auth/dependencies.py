from fastapi import Depends, Request

from src.auth.services import UserRequests
from src.auth.jwt_handler import jwt_handler
from src.exceptions import (
    AccessTokenNotFoundException,
    InvalidAccessTokenException,
    RefreshTokenNotFoundException,
    UserHasNoRightsException, 
    UserNotFoundException
)


async def get_access_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise AccessTokenNotFoundException
    return access_token


async def get_refresh_token(request: Request) -> str:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise RefreshTokenNotFoundException
    return refresh_token


async def get_current_user(token: str = Depends(get_access_token)):
    payload = await jwt_handler.decode_token(token)
    if not payload:
        raise InvalidAccessTokenException

    email = payload.get("sub")
    if not email:
        raise InvalidAccessTokenException

    user = await UserRequests.find_one_or_none(email=email)
    if not user:
        return UserNotFoundException

    return user


async def get_current_admin_user(user=Depends(get_current_user)):
    if user.role_title != "ADMIN":
        raise UserHasNoRightsException
    return user
