from pydantic import BaseModel, EmailStr


class MessageResponse(BaseModel):
    message: str


class AuthResponse(MessageResponse):
    user: EmailStr


class RefreshTokenResponse(MessageResponse):
    user: EmailStr
    