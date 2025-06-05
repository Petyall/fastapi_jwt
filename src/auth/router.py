from datetime import datetime

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.jwt_handler import jwt_handler
from src.auth.schemas import UserCreate, UserLogin
from src.auth.password_handler import PasswordHandler
from src.auth.validation.password_validator import validator
from src.auth.services import RefreshTokenService, UserRequests
from src.auth.dependencies import get_current_admin_user, get_refresh_token


router = APIRouter(prefix="/auth", tags=["Модуль авторизации пользователей"])

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def user_registration(user_data: UserCreate) -> dict:
    check_user_existing = await UserRequests.find_one_or_none(email=user_data.email)
    if check_user_existing:
        return {"error": "Данный пользователь уже зарегистрирован"}

    validation_result = validator.validate(password=user_data.password, email=user_data.email)
    if validation_result is not True:
        return {"error": validation_result}

    hashed_password = PasswordHandler.hash_password(user_data.password)

    try:
        await UserRequests.add(
            email=user_data.email,
            password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            paternal_name=user_data.paternal_name,
            phone_number=user_data.phone_number,
            birthday=user_data.birthday,
            role_title="USER",
        )
    except Exception as e:
        return {"error": str(e)}

    return {"message": "Пользователь создан успешно"}


@router.post("/login")
async def user_login(user_data: UserLogin):
    user = await UserRequests.find_one_or_none(email=user_data.email)

    if not user or not PasswordHandler.verify_password(user_data.password, user.password):
        return {"error": "Неверный email или пароль"}

    access_token = await jwt_handler.create_access_token(subject=user.email)
    refresh_token = await jwt_handler.create_refresh_token(subject=user.email)

    response = JSONResponse(content={"message": "Успешный вход", "user": user.email})

    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="Lax", max_age=18000)
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Lax", max_age=60 * 60 * 24 * 15
    )

    return response


@router.post("/logout", response_model=dict)
async def logout(refresh_token: str = Depends(get_refresh_token)):
    refresh_payload = await jwt_handler.decode_token(refresh_token)

    await RefreshTokenService.revoke(jti=refresh_payload["jti"], revoked=datetime.now())

    response = JSONResponse(content={"message": "Выход выполнен"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_token: str = Depends(get_refresh_token)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh-токен отсутствует")

    payload = await jwt_handler.decode_token(refresh_token)
    jti = payload.get("jti")
    email = payload.get("sub")

    token = await RefreshTokenService.find_one_or_none(jti=jti)
    if not token or token.revoked or token.expires_at < datetime.now():
        raise HTTPException(status_code=401, detail="Refresh-токен недействителен")

    await RefreshTokenService.revoke(jti=jti, revoked=datetime.now())

    new_access_token = await jwt_handler.create_access_token(subject=email)
    new_refresh_token = await jwt_handler.create_refresh_token(subject=email)

    response = JSONResponse(content={"message": "Токены обновлены", "user": email})
    response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=True, samesite="Lax", max_age=18000)
    response.set_cookie(
        key="refresh_token", value=new_refresh_token, httponly=True, secure=True, samesite="Lax", max_age=60 * 60 * 24 * 15
    )
    return response


@router.get("/check")
async def check_admin(user=Depends(get_current_admin_user)):
    return user
