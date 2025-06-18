import jwt

from uuid import uuid4
from pathlib import Path
from datetime import datetime, timedelta
from pydantic import EmailStr, ValidationError

from src.config import settings
from src.auth.services import RefreshTokenRepository
from src.exceptions import (
    InvalidTokenException,
    ExpiredTokenException,
    InvalidEmailException,
)

PRIVATE_KEY_PATH = Path(settings.JWT_PRIVATE_KEY_PATH)
PRIVATE_KEY = PRIVATE_KEY_PATH.read_text()

PUBLIC_KEY_PATH = Path(settings.JWT_PUBLIC_KEY_PATH)
PUBLIC_KEY = PUBLIC_KEY_PATH.read_text()

ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE
REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE
RESET_TOKEN_EXPIRE_MINUTES = settings.JWT_RESET_TOKEN_EXPIRE


class JWTHandler:

    async def create_access_token(self, subject: EmailStr) -> str:
        token, _, _ = await self._create_token(subject, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return token

    async def create_refresh_token(self, subject: str) -> str:
        token, jti, expires_at = await self._create_token(subject, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
        await RefreshTokenRepository.add(jti=jti, email=subject, expires_at=expires_at)
        return token

    async def create_reset_token(self, subject: str) -> str:
        token, _, _ = await self._create_token(subject, timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES))
        return token

    async def _create_token(self, email: str, expires_delta: timedelta) -> tuple[str, str, datetime]:
        try:
            email = EmailStr._validate(email)
        except ValidationError:
            raise InvalidEmailException

        now = datetime.now()
        expire = now + expires_delta
        jti = str(uuid4())

        payload = {
            "sub": str(email),
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": jti,
        }

        token = jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)
        return token, jti, expire

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise InvalidTokenException


jwt_handler = JWTHandler()
