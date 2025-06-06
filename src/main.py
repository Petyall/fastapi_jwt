from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.email.router import router as email_router


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(auth_router)
app.include_router(email_router)
