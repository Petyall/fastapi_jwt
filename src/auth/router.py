from uuid import uuid4
from urllib.parse import quote
from datetime import datetime, timedelta

from fastapi.responses import JSONResponse
from fastapi import APIRouter, BackgroundTasks, Depends, status

from src.config import settings
from src.logs.logger import logger
from src.auth.jwt_handler import jwt_handler
from src.auth.password_handler import PasswordHandler
from src.auth.validation.password_validator import validator
from src.auth.services import RefreshTokenService, UserRequests
from src.email.email_handler import email_handler, email_templates
from src.auth.dependencies import get_current_admin_user, get_refresh_token
from src.auth.schemas import (ForgotPassword, ResetPassword, UserCreate, UserLogin)
from src.exceptions import (
    UserAlreadyExistsException,
    PasswordValidationErrorException,
    InternalServerErrorException,
    InvalidCredentialsException,
    RefreshTokenNotFoundException,
    InvalidRefreshTokenException,
    InvalidPasswordResetTokenException,
    UserNotFoundException,
    PasswordIdenticalToPreviousException,
)


router = APIRouter(prefix="/auth", tags=["Модуль авторизации пользователей"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def user_registration(user_data: UserCreate, background_tasks: BackgroundTasks) -> dict:
    check_user_existing = await UserRequests.find_one_or_none(email=user_data.email)
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
        await UserRequests.add(
            email=user_data.email,
            password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            paternal_name=user_data.paternal_name,
            phone_number=user_data.phone_number,
            birthday=user_data.birthday,
            role_title="USER",
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
                template = email_templates.get_template("confirm_email.html")
                link = f"{settings.FRONTEND_URL}/email/confirm?email={quote(email)}&token={token}"
                html_content = template.render(confirmation_link=link)
                await email_handler.send_email(to=email, subject="Подтверждение регистрации", html_content=html_content)
            except Exception as e:
                logger.error(f"Ошибка при отправке письма подтверждения для {email}: {type(e).__name__}: {e}")

        background_tasks.add_task(send_confirmation_email, user_data.email, confirmation_token)

        message += " В течение 24 часов, вам придет сообщение на почту для подтверждения регистрации."

    return {"message": message}


@router.post("/login")
async def user_login(user_data: UserLogin):
    user = await UserRequests.find_one_or_none(email=user_data.email)
    if not user or not PasswordHandler.verify_password(user_data.password, user.password):
        raise InvalidCredentialsException

    access_token = await jwt_handler.create_access_token(subject=user.email)
    refresh_token = await jwt_handler.create_refresh_token(subject=user.email)

    response = JSONResponse(content={"message": "Успешный вход", "user": user.email})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE * 60 * 60 * 24,
    )

    return response


@router.post("/logout", response_model=dict)
async def logout(refresh_token: str = Depends(get_refresh_token)):
    if not refresh_token:
        raise RefreshTokenNotFoundException

    payload = await jwt_handler.decode_token(refresh_token)
    jti = payload.get("jti")
    email = payload.get("sub")
    if not jti or not email:
        raise InvalidRefreshTokenException

    refresh_token_check = await RefreshTokenService.revoke(jti=jti, revoked=datetime.now())
    if not refresh_token_check:
        logger.error(f"Не найден Refresh-токен {jti} для пользователя {email}")

    response = JSONResponse(content={"message": "Выход выполнен"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response


@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_token: str = Depends(get_refresh_token)):
    if not refresh_token:
        raise RefreshTokenNotFoundException

    payload = await jwt_handler.decode_token(refresh_token)
    jti = payload.get("jti")
    email = payload.get("sub")
    if not jti or not email:
        raise InvalidRefreshTokenException

    token = await RefreshTokenService.find_one_or_none(jti=jti)
    if not token or token.revoked or datetime.now() - token.created_at > timedelta(days=30):
        raise InvalidRefreshTokenException

    refresh_token_check = await RefreshTokenService.revoke(jti=jti, revoked=datetime.now())
    if not refresh_token_check:
        logger.error(f"Не найден Refresh-токен {jti} для пользователя {email}")

    new_access_token = await jwt_handler.create_access_token(subject=email)
    new_refresh_token = await jwt_handler.create_refresh_token(subject=email)

    response = JSONResponse(content={"message": "Токены обновлены", "user": email})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE * 60 * 60 * 24,
    )

    return response


@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, background_tasks: BackgroundTasks):
    user = await UserRequests.find_one_or_none(email=data.email)
    if user:
        password_reset_token = await jwt_handler.create_reset_token(subject=user.email)

        await UserRequests.update(
            id=user.id, password_reset_token=password_reset_token, password_reset_token_created_at=datetime.now()
        )

        async def send_password_reset_email(email: str, token: str):
            try:
                template = email_templates.get_template("reset_password.html")
                link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
                html_content = template.render(reset_link=link)
                await email_handler.send_email(to=email, subject="Сброс пароля", html_content=html_content)
            except Exception as e:
                logger.error(f"Ошибка при отправке письма подтверждения для {email}: {type(e).__name__}: {e}")

        background_tasks.add_task(send_password_reset_email, user.email, password_reset_token)

    return {"message": "Если пользователь существует, на его email отправлено письмо с инструкцией по сбросу пароля"}


@router.post("/reset-password", response_model=dict)
async def reset_password(data: ResetPassword):
    payload = await jwt_handler.decode_token(data.token)
    email = payload.get("sub")
    if not email:
        raise InvalidPasswordResetTokenException

    user = await UserRequests.find_one_or_none(email=email, password_reset_token=data.token)
    if not user:
        raise UserNotFoundException(email)

    if PasswordHandler.verify_password(data.new_password, user.password):
        raise PasswordIdenticalToPreviousException

    validation_result = validator.validate(password=data.new_password, email=user.email)
    if validation_result is not True:
        raise PasswordValidationErrorException(validation_result)

    new_hashed = PasswordHandler.hash_password(data.new_password)
    await UserRequests.update(id=user.id, password=new_hashed, password_reset_token=None, password_reset_token_created_at=None)

    return {"message": "Пароль успешно изменён"}


@router.get("/check")
async def check_admin(user=Depends(get_current_admin_user)):
    return user
