from fastapi import APIRouter, Depends, Response

from app.users.dependences import get_current_user
from app.users.models import Users
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.services import UserService
from app.users.schemas import UserCreate
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException, NotEnoughAuthorityException

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация и пользователи"],
)


@router.post("/register")
async def register_user(user_data: UserCreate):
    """
    Регистрация пользователя
    """
    # Проверка существования пользователя
    existing_user = await UserService.find_one_or_none(email=user_data.email)
    # Возврат ошибки, если такой пользователь уже зарегистрирован
    if existing_user:
        raise UserAlreadyExistsException
    # Преобразование пароля в хэшированный
    hashed_password = get_password_hash(user_data.password)
    # Создание пользователя
    await UserService.add(email=user_data.email, hashed_password=hashed_password)
    # Возврат успешного сообщения
    return f"Пользователь {user_data.email} успешно зарегистрирован"


@router.post("/login")
async def login_user(response: Response, user_data: UserCreate):
    """
    Авторизация пользователя
    """
    # Попытка авторизации пользователя
    user = await authenticate_user(user_data.email, user_data.password)
    # Возврат ошибки, если пользователь не зарегистрирован или не подошел пароль
    if not user:
        raise IncorrectEmailOrPasswordException
    # Создание и передача токена в cookie 
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True
    )
    # Возврат успешного сообщения
    return f"Пользователь {user_data.email} успешно авторизован"


@router.post("/logout")
async def logout_user(response: Response):
    """
    Выход пользователя
    """
    # Удаление токена из cookie
    response.delete_cookie("access_token")
    return "До свидания!"


@router.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    """
    Получение информации о пользователе
    """
    return(current_user)


@router.get("/all")
async def read_users_all(current_user: Users = Depends(get_current_user)):
    """
    Получение информации обо всех пользователях
    """
    # Проверка роли пользователя
    if current_user.role_id == 2:
        # Возврат списка пользователей
        return await UserService.find_all()
    # Возврат ошибки, если пользователь не админ
    else:
        raise NotEnoughAuthorityException


@router.get("/id/{user_id}")
async def read_users_id(user_id: int, current_user: Users = Depends(get_current_user)):
    """
    Получение информации о пользователе по id
    """
    # Проверка роли пользователя
    if current_user.role_id == 2:
        # Возврат конкретного пользователя
        return await UserService.find_one_or_none(id=user_id)
    # Возврат ошибки, если пользователь не админ
    else:
        raise NotEnoughAuthorityException
    