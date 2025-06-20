from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded

from src.database import engine
from src.logs.logger import logger
from src.exceptions import ProjectException
from src.auth.router import router as auth_router
from src.email.router import router as email_router
from src.users.router import router as users_router
from src.limits.limiter import limiter, rate_limit_exceeded_handler


# Контекстный менеджер для управления жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет подключением и отключением ресурсов приложения.
    При завершении работы приложения освобождает соединение с базой данных.
    """
    yield
    await engine.dispose()


# Инициализация приложения FastAPI
app = FastAPI(lifespan=lifespan)


# Подключение роутеров
app.include_router(auth_router)
app.include_router(email_router)
app.include_router(users_router)


@app.exception_handler(ProjectException)
async def project_exception_handler(request: Request, exc: ProjectException):
    """
    Обрабатывает исключения типа ProjectException.
    Логирует ошибку, если она не предназначена для клиента.
    Возвращает JSON-ответ с деталями ошибки или общим сообщением.
    """
    if not exc.expose_to_client:
        logger.error(
            f"{request.method} {request.url} — {type(exc).__name__}: {exc.detail}"
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if exc.expose_to_client else "Ошибка на сервере. Попробуйте позже."
        }
    )


# Настройка лимитера запросов
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
