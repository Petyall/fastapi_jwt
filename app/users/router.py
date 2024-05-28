from fastapi import APIRouter, Depends, Response, status
from datetime import datetime
from uuid import uuid4
from jose import JWTError, jwt
from pydantic import EmailStr

from app.config import settings
from app.users.dependencies import get_current_user, check_current_user_and_role, get_refresh_token
from app.users.models import Users
from app.users.authorization import create_refresh_token, get_password_hash, authenticate_user, create_access_token, verify_password
from app.users.services import UserService, RoleService
from app.users.schemas import UserCreate, UserLogin, UserPasswordChange
from app.exceptions import IncorrectFormatTokenException, UserAlreadyExistsException, UserIsNotPresentException, UserNotFoundException, UserAlreadyConfirmedException, IncorrectEmailOrPasswordException
from app.email import send_email_confirmation_email

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация и пользователи"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate) -> dict:
    """
    Регистрация пользователя
    """
    existing_user = await UserService.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException

    hashed_password = get_password_hash(user_data.password)
    await UserService.add(
        email=user_data.email,
        hashed_password=hashed_password,
        # uuid=str(uuid4()),
        is_confirmed=False
    )

    # await send_email_confirmation_email(user_data.email)
    await UserService.update_user(email=user_data.email, confirmation_sent=datetime.now())
    
    return {"message": f"Для подтверждения пользователя {user_data.email} было отправлено письмо с ссылкой для завершения регистрации"}


@router.get("/confirm_email", status_code=status.HTTP_200_OK)
async def confirm_email(email: str, uuid: str) -> dict:
    """
    Подтверждение электронной почты
    """
    user = await UserService.find_one_or_none(email=email, id=uuid)
    if not user:
        raise UserNotFoundException

    if user.is_confirmed:
        raise UserAlreadyConfirmedException

    user = await UserService.update_user(email=email, is_confirmed=True, confirmation_date=datetime.now())
    return {"message": "Электронный адрес подтвержден."}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(response: Response, user_data: UserLogin) -> dict:
    """
    Авторизация пользователя
    """
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True
    )

    return {"message": f"Пользователь {user_data.email} успешно авторизован"}


@router.post("/password_change", status_code=status.HTTP_200_OK)
async def password_change(user_data: UserPasswordChange, current_user: Users = Depends(get_current_user)) -> dict:
    """
    Смена пароля
    """
    user = await UserService.find_one_or_none(email=current_user.email)

    if not user:
        raise IncorrectEmailOrPasswordException
    
    if not verify_password(user_data.current_password, user.hashed_password):
        raise IncorrectEmailOrPasswordException
    
    new_password_hashed = get_password_hash(user_data.new_password)
    await UserService.update_user(email=current_user.email, hashed_password=new_password_hashed)
    return {"message": f"Пароль для {current_user.email} успешно изменен"}


@router.post("/refresh_token", status_code=status.HTTP_200_OK)
async def refresh_token(response: Response, refresh_token: str = Depends(get_refresh_token)) -> dict:
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise IncorrectFormatTokenException

    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException

    user = await UserService.find_by_id(user_id)
    if not user:
        raise UserIsNotPresentException

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True
    )
    return {"message": "Access токен успешно обновлен."}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(response: Response) -> dict:
    """
    Выход пользователя
    """
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "До свидания!"}


@router.get("/me", status_code=status.HTTP_200_OK)
async def read_users_me(current_user: Users = Depends(get_current_user)):
    """
    Получение информации о пользователе
    """
    return current_user


@router.get("/all", status_code=status.HTTP_200_OK)
async def read_users_all(current_user: Users = Depends(check_current_user_and_role)):
    """
    Получение информации обо всех пользователях
    """
    return await UserService.find_all()


@router.get("/id/{user_id}", status_code=status.HTTP_200_OK)
async def read_users_id(user_id: int, current_user: Users = Depends(check_current_user_and_role)):
    """
    Получение информации о пользователе по id
    """
    return await UserService.find_one_or_none(id=user_id)


@router.get("/add_role", status_code=status.HTTP_200_OK)
async def add_role(name: str):
    return await RoleService.add(name=name)