from uuid import UUID
from pydantic import BaseModel, EmailStr


class EmailConfirmation(BaseModel):
    email: EmailStr
    confirmation_token: UUID
    