from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import config
from app.api.routes.progress import router as progress_router

app = FastAPI(title="LearnHanzi Progress Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(progress_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

