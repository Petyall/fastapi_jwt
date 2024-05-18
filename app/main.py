from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware import RefreshTokenMiddleware
from app.users.router import router as router_users

app = FastAPI()

app.include_router(router_users)

origins = ["*"]

app.add_middleware(RefreshTokenMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Set-Cookie", "Access-Control-Allow-Origin", "Access-Control-Allow-Headers"],
)
