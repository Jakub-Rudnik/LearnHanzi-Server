from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import config

app = FastAPI(title="LearnHanzi Dictionary Service", version="0.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

