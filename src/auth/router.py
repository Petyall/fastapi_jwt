from uuid import uuid4
from urllib.parse import quote
from datetime import datetime, timedelta

from fastapi.responses import JSONResponse
from fastapi import APIRouter, BackgroundTasks, Depends, status, Request

from src.config import settings
from src.logs.logger import logger
from src.limits.limiter import limiter
from src.auth.constants import UserRole
from src.auth.utils.jwt_handler import jwt_handler
from src.auth.utils.cookie_handler import CookieHandler
from src.auth.utils.password_validator import validator
from src.auth.utils.password_handler import PasswordHandler
from src.auth.services import RefreshTokenRepository, UserRepository
from src.email.utils.email_handler import email_handler
from src.auth.dependencies import get_current_admin_user, get_refresh_token
from src.auth.schemas.responses import MessageResponse, AuthResponse, RefreshTokenResponse
from src.auth.schemas.requests import UserCreateRequest, UserLoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from src.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    InvalidRefreshTokenException,
    InternalServerErrorException,
    RefreshTokenNotFoundException,
    PasswordValidationErrorException,
    InvalidPasswordResetTokenException,
    PasswordIdenticalToPreviousException,
)


router = APIRouter(prefix="/auth", tags=["Модуль авторизации пользователей"])


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("2/minute")
async def user_registration(request: Request, user_data: UserCreateRequest, background_tasks: BackgroundTasks) -> MessageResponse:
    check_user_existing = await UserRepository.find_one_or_none(email=user_data.email)
    if check_user_existing:
        raise UserAlreadyExistsException(user_data.email)

    validation_result = validator.validate(password=user_data.password, email=user_data.email)
    if validation_result is not True:
        raise PasswordValidationErrorException(validation_result)

    hashed_password = PasswordHandler.hash_password(user_data.password)

    email_confirmed = True
    confirmation_token = None
    confirmation_token_created_at = None

    if settings.ENABLE_EMAIL_CONFIRMATION:
        email_confirmed = False
        confirmation_token = str(uuid4())
        confirmation_token_created_at = datetime.now()

    try:
        await UserRepository.add(
            email=user_data.email,
            password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            paternal_name=user_data.paternal_name,
            phone_number=user_data.phone_number,
            birthday=user_data.birthday,
            role_title=UserRole.USER.value,
            email_confirmed=email_confirmed,
            confirmation_token=confirmation_token,
            confirmation_token_created_at=confirmation_token_created_at,
        )
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {type(e).__name__}: {e}")
        raise InternalServerErrorException("Не удалось создать пользователя")

    logger.info(f"Пользователь успешно зарегистрирован: {user_data.email}")

    message = f"Пользователь '{user_data.email}' создан успешно"

    if settings.ENABLE_EMAIL_CONFIRMATION:
        async def send_confirmation_email(email: str, token: str):
            try:
                link = f"{settings.FRONTEND_URL}/email/confirm?email={quote(email)}&token={token}"
                html_content = email_handler.render_template(
                    "confirm_email.html",
                    {"confirmation_link": link}
                )
                await email_handler.send_email(
                    to=email,
                    subject="Подтверждение регистрации",
                    html_content=html_content
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке письма подтверждения для {email}: {type(e).__name__}: {e}")

        background_tasks.add_task(send_confirmation_email, user_data.email, confirmation_token)

        message += " В течение 24 часов, вам придет сообщение на почту для подтверждения регистрации."

    return MessageResponse(message=message)


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def user_login(request: Request, user_data: UserLoginRequest) -> AuthResponse:
    user = await UserRepository.find_one_or_none(email=user_data.email)
    if not user or not PasswordHandler.verify_password(user_data.password, user.password):
        raise InvalidCredentialsException

    access_token = await jwt_handler.create_access_token(subject=user.email)
    refresh_token = await jwt_handler.create_refresh_token(subject=user.email)

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content=AuthResponse(message="Успешный вход", user=user.email).dict()
    )

    CookieHandler.set_auth_tokens(response, access_token, refresh_token)

    return response


@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(refresh_token: str = Depends(get_refresh_token)) -> MessageResponse:
    if not refresh_token:
        raise RefreshTokenNotFoundException

    payload = await jwt_handler.decode_token(refresh_token)
    jti = payload.get("jti")
    email = payload.get("sub")
    if not jti or not email:
        raise InvalidRefreshTokenException

    refresh_token_check = await RefreshTokenRepository.revoke(jti=jti, revoked=datetime.now())
    if not refresh_token_check:
        logger.error(f"Не найден Refresh-токен {jti} для пользователя {email}")

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content=MessageResponse(message="Выход выполнен").dict()
    )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def refresh_token(request: Request, refresh_token: str = Depends(get_refresh_token)) -> RefreshTokenResponse:
    if not refresh_token:
        raise RefreshTokenNotFoundException

    payload = await jwt_handler.decode_token(refresh_token)
    jti = payload.get("jti")
    email = payload.get("sub")
    if not jti or not email:
        raise InvalidRefreshTokenException

    token = await RefreshTokenRepository.find_one_or_none(jti=jti)
    if not token or token.revoked or datetime.now() - token.created_at > timedelta(days=30):
        raise InvalidRefreshTokenException

    refresh_token_check = await RefreshTokenRepository.revoke(jti=jti, revoked=datetime.now())
    if not refresh_token_check:
        logger.error(f"Не найден Refresh-токен {jti} для пользователя {email}")

    new_access_token = await jwt_handler.create_access_token(subject=email)
    new_refresh_token = await jwt_handler.create_refresh_token(subject=email)

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content=RefreshTokenResponse(message="Токены обновлены", user=email).dict()
    )

    CookieHandler.set_auth_tokens(response, new_access_token, new_refresh_token)

    return response


@router.post("/forgot-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
@limiter.limit("2/minute")
async def forgot_password(request: Request, data: ForgotPasswordRequest, background_tasks: BackgroundTasks) -> MessageResponse:
    user = await UserRepository.find_one_or_none(email=data.email)
    if user:
        password_reset_token = await jwt_handler.create_reset_token(subject=user.email)

        await UserRepository.update(
            id=user.id,
            password_reset_token=password_reset_token,
            password_reset_token_created_at=datetime.now()
        )

        async def send_password_reset_email(email: str, token: str):
            try:
                link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
                html_content = email_handler.render_template(
                    "reset_password.html",
                    {"reset_link": link}
                )
                await email_handler.send_email(to=email, subject="Сброс пароля", html_content=html_content)
            except Exception as e:
                logger.error(f"Ошибка при отправке письма подтверждения для {email}: {type(e).__name__}: {e}")

        background_tasks.add_task(send_password_reset_email, user.email, password_reset_token)

    return MessageResponse(message="Если пользователь существует, на его email отправлено письмо с инструкцией по сбросу пароля")


@router.post("/reset-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def reset_password(request: Request, data: ResetPasswordRequest) -> MessageResponse:
    payload = await jwt_handler.decode_token(data.token)
    email = payload.get("sub")
    if not email:
        raise InvalidPasswordResetTokenException

    user = await UserRepository.find_one_or_none(email=email, password_reset_token=data.token)
    if not user:
        raise InvalidPasswordResetTokenException

    if PasswordHandler.verify_password(data.new_password, user.password):
        raise PasswordIdenticalToPreviousException

    validation_result = validator.validate(password=data.new_password, email=user.email)
    if validation_result is not True:
        raise PasswordValidationErrorException(validation_result)

    new_hashed = PasswordHandler.hash_password(data.new_password)
    await UserRepository.update(id=user.id, password=new_hashed, password_reset_token=None, password_reset_token_created_at=None)

    return MessageResponse(message="Пароль успешно изменён")


@router.get("/check")
async def check_admin(user=Depends(get_current_admin_user)):
    return user
