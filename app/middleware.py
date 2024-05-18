from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from datetime import datetime
from app.config import settings
from app.users.authorization import create_access_token

class RefreshTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = Response("Unauthorized", status_code=401)
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if access_token:
            try:
                payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                exp = payload.get("exp")
                if exp and datetime.utcnow().timestamp() > exp:
                    raise JWTError
            except JWTError:
                if refresh_token:
                    try:
                        refresh_payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
                        user_id = refresh_payload.get("sub")
                        if user_id:
                            new_access_token = create_access_token({"sub": user_id})
                            response = await call_next(request)
                            response.set_cookie(
                                key="access_token",
                                value=new_access_token,
                                httponly=True
                            )
                            return response
                    except JWTError:
                        return response

        response = await call_next(request)
        return response
