from pydantic import BaseModel, EmailStr


class RoleBase(BaseModel):
    name: str


class Role(RoleBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str


class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True
