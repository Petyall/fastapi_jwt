from fastapi import APIRouter, status, Depends

from src.auth.services import UserRepository
from src.exceptions import UserNotFoundException
from src.users.schemas.requests import FindUserByEmailRequest
from src.auth.dependencies import get_current_user, get_current_admin_user
from src.users.schemas.responses import UserBaseResponse, UserAdminResponse, AllUsersAdminResponse


router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("/me", response_model=UserBaseResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(current_user=Depends(get_current_user)):
    return current_user


@router.get("/all", response_model=AllUsersAdminResponse, status_code=status.HTTP_200_OK)
async def get_all_registered_users(admin_user=Depends(get_current_admin_user)):
    users = await UserRepository.find_all()
    return {"users": users}


@router.post("/find-by-email", response_model=UserAdminResponse)
async def find_user_by_email(data: FindUserByEmailRequest, admin_user=Depends(get_current_admin_user)):
    user = await UserRepository.find_one_or_none(email=data.email)
    if not user:
        raise UserNotFoundException(data.email)
    return user
