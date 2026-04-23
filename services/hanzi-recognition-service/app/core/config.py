from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_path: str = "/app/models/hanzi_model.pt"
    labels_path: str = "/app/models/labels.json"
    device: str = "cpu"

    class Config:
        env_file = ".env"


settings = Settings()
