from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from jose import ExpiredSignatureError, jwt, JWTError
from datetime import datetime
from app.config import settings
from app.users.authorization import create_access_token

class RefreshTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        
        response = await call_next(request)

        if not access_token and not refresh_token:
            return response

        if refresh_token:
            try:
                refresh_payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
            except ExpiredSignatureError:
                response.delete_cookie("access_token")
                response.delete_cookie("refresh_token")
                return response
            except JWTError:
                response.delete_cookie("refresh_token")
                return response
        else:
            if access_token:
                try:
                    payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                except JWTError:
                    response.delete_cookie("access_token")
                    return response

        if access_token:
            try:
                payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                exp = payload.get("exp")
                if exp and datetime.utcnow().timestamp() > exp:
                    raise JWTError
            except JWTError:
                if refresh_token:
                    try:
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
                        response.delete_cookie("access_token")
                        response.delete_cookie("refresh_token")
                        return response
        return response
