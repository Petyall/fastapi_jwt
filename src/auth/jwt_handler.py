import jwt

from uuid import uuid4
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import HTTPException
from pydantic import EmailStr, ValidationError

from src.auth.services import RefreshTokenService
from src.config import settings


PRIVATE_KEY_PATH = Path(settings.JWT_PRIVATE_KEY_PATH)
PRIVATE_KEY = PRIVATE_KEY_PATH.read_text()

PUBLIC_KEY_PATH = Path(settings.JWT_PUBLIC_KEY_PATH)
PUBLIC_KEY = PUBLIC_KEY_PATH.read_text()

ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE
REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE


class JWTHandler:

    async def create_access_token(self, subject: EmailStr) -> str:
        token, _, _ = await self._create_token(subject, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return token

    async def create_refresh_token(self, subject: str) -> str:
        token, jti, expires_at = await self._create_token(subject, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
        await RefreshTokenService.add(jti=jti, email=subject, expires_at=expires_at)
        return token

    async def _create_token(self, email: str, expires_delta: timedelta) -> tuple[str, str, datetime]:
        try:
            email = EmailStr._validate(email)
        except ValidationError as e:
            raise ValueError(f"Некорректный email: {e}")

        now = datetime.now()
        expire = now + expires_delta
        jti = str(uuid4())

        payload = {"sub": str(email), "iat": int(now.timestamp()), "exp": int(expire.timestamp()), "jti": jti}

        token = jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)
        return token, jti, expire

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Access-токен просрочен")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Неверный токен")


jwt_handler = JWTHandler()
