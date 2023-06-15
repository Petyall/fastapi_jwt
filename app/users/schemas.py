from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str


class ItemCreate(RoleBase):
    pass


class Item(RoleBase):
    id: int
    name: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True