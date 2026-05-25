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
    password_reset_token_expire_minutes: int = 30
    password_reset_debug_return_token: bool = True

    frontend_url: str
    frontend_reset_password_path: str = "/reset-password"

    smtp_host: str | None = None
    smtp_port: int = 1025
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_starttls: bool = False

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
