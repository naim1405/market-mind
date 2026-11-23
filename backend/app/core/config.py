from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    APP_NAME:str = "Market Mind AI"
    DEBUG: bool = True
    PORT: int = 8000
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DB_HOST: str = "db"
    DB_PORT: str = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: SecretStr = SecretStr(secret_value="postgres")
    DB_NAME: str = "market_mind_ai"
    DB_SCHEMA: str = "public"

    @property
    def DATABASE_URL(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
