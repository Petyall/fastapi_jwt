from pydantic import BaseModel, EmailStr


class FindUserByEmailRequest(BaseModel):
    email: EmailStr