from dotenv import load_dotenv
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

#load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "learnhanzi-auth-service"
    jwt_audience: str = "learnhanzi-services"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    frontend_url: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
