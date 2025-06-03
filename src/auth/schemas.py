from pydantic import BaseModel, EmailStr, Field
from datetime import date


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    first_name: str = "test"
    last_name: str = "test"
    paternal_name: str = "test"
    phone_number: str = Field(pattern=r'^\+?\d{10,15}$', default="+79001234567")
    birthday: date = "2008-08-08"


class UserRead(UserBase):
    first_name: str
    last_name: str
    paternal_name: str
    phone_number: str
    birthday: date
    ban: bool


class UserLogin(UserBase):
    password: str
