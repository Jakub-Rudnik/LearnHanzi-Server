from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    frontend_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "learnhanzi-auth-service"
    jwt_audience: str = "learnhanzi-services"
    dictionary_service_url: str = "http://dictionary:8002"
    accuracy_difficulty_threshold: float = 0.6

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
