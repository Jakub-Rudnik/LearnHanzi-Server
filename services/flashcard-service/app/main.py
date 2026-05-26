from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.flashcards import router as flashcards_router
from app.core import config

app = FastAPI(title="LearnHanzi Flashcard Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flashcards_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

