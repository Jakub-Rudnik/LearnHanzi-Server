from dotenv import load_dotenv
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    database_url: str
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "learnhanzi-auth-service"
    jwt_audience: str = "learnhanzi-services"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    frontend_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()