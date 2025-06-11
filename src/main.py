from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.logs.logger import logger
from src.exceptions import ProjectException
from src.auth.router import router as auth_router
from src.email.router import router as email_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(auth_router)
app.include_router(email_router)

@app.exception_handler(ProjectException)
async def project_exception_handler(request: Request, exc: ProjectException):
    if not exc.expose_to_client:
        logger.error(
            f"{request.method} {request.url} — {type(exc).__name__}: {exc.detail}"
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail if exc.expose_to_client else "Ошибка на сервере. Попробуйте позже."}
    )
