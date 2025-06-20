from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, EmailStr


class UserBaseResponse(BaseModel):
    first_name: str
    last_name: str
    paternal_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    email_confirmed: bool
    registration_date: datetime

    model_config = {
        "from_attributes": True
    }

class UserAdminResponse(UserBaseResponse):
    id: int
    ban_date: Optional[datetime]
    last_activity: Optional[datetime]
    role_title: str
    email_confirmed_at: Optional[datetime]


class AllUsersAdminResponse(BaseModel):
    users: List[UserAdminResponse]
