from pydantic import BaseModel, EmailStr
from uuid import UUID

class EmailConfirmation(BaseModel):
    email: EmailStr
    uuid: UUID