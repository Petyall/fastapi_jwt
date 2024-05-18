from pydantic import BaseSettings

class Settings(BaseSettings):
    # Если использовать PostgreSQL, то в файле .env нужно 
    # добавить переменные, а затем сделать ссылку до БД
    # DB_HOST:str
    # DB_PORT:int
    # DB_USER:str
    # DB_PASS:str
    # DB_NAME:str

    # @root_validator
    # def get_database_url(cls, v):
    #     v["DATABASE_URL"] = f"postgresql+asyncpg://{v['DB_USER']}:{v['DB_PASS']}@{v['DB_HOST']}:{v['DB_PORT']}/{v['DB_NAME']}"
    #     return v


    # Все переменные необходимо хранить в файле .env,
    # но так как это пример, они останутся здесь, кроме
    # логина и пароля от почты
    # SMTP_HOST:str
    # SMTP_PORT:int
    # SMTP_USER:str
    # SMTP_PASS:str

    SECRET_KEY = 'my_secret_key'
    REFRESH_SECRET_KEY = 'my_refresh_secret_key'
    ALGORITHM = 'HS256'
    # ACCESS_TOKEN_EXPIRE_MINUTES = 1
    APP_ORIGIN='http://127.0.0.1:8000/'

    
    class Config:
        env_file = '.env'

settings = Settings()