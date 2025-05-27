from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parent.parent / ".env")

    PASSWORD_VALIDATION_LEVEL: str
    PASSWORDS_COMMON_LIST_PATH: str

    DB_TYPE: str

    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_USER: str | None = None
    DB_PASS: str | None = None
    DB_NAME: str | None = None

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "postgresql":
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return "sqlite+aiosqlite:///./db.sqlite3"


settings = Settings()