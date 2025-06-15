from datetime import date
from pydantic import BaseModel, EmailStr, Field


class UserBaseRequest(BaseModel):
    email: EmailStr


class UserCreateRequest(UserBaseRequest):
    password: str
    first_name: str = "test"
    last_name: str = "test"
    paternal_name: str = "test"
    phone_number: str = Field(pattern=r"^\+?\d{10,15}$", default="+79001234567")
    birthday: date = "2008-08-08"


class UserLoginRequest(UserBaseRequest):
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
