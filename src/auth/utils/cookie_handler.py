from fastapi.responses import JSONResponse
from src.config import settings


class CookieHandler:

    @staticmethod
    def set_auth_tokens(response: JSONResponse, access_token: str, refresh_token: str) -> None:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=settings.JWT_ACCESS_TOKEN_EXPIRE * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE * 60 * 60 * 24,
        )
