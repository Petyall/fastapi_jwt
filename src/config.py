from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # --- Пароли ---
    PASSWORD_VALIDATION_LEVEL: str
    PASSWORDS_COMMON_LIST_PATH: str

    # --- База данных ---
    DB_TYPE: str
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "postgresql":
            if not all([self.DB_HOST, self.DB_PORT, self.DB_USER, self.DB_PASS, self.DB_NAME]):
                raise ValueError("В файле .env заданы не все переменные окружения для PostgreSQL")
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        elif self.DB_TYPE == "sqlite":
            return "sqlite+aiosqlite:///./db.sqlite3"
        else:
            raise ValueError(f"В файле .env указана неизвестная база данных (DB_TYPE): {self.DB_TYPE}")

    # --- JWT ---
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE: int
    JWT_REFRESH_TOKEN_EXPIRE: int
    JWT_RESET_TOKEN_EXPIRE: int
    JWT_PRIVATE_KEY_PATH: str
    JWT_PUBLIC_KEY_PATH: str

    # --- Email ---
    EMAIL_TEMPLATES: str
    ENABLE_EMAIL_CONFIRMATION: bool
    EMAIL_CONFIRM_TOKEN_EXPIRE: int
    EMAIL_FROM: str
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_HOST: str
    SMTP_PORT: int

    # --- Frontend ---
    FRONTEND_URL: str

    # --- Ограничения ---
    ENABLE_RATE_LIMITER: bool


settings = Settings()
