from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL = ''
    SECRET_KEY = 'my_secret_key'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

settings = Settings()