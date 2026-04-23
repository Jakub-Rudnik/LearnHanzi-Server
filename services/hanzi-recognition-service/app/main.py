from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import recognition
from app.core.model import HanziModel

model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    print("Loading model...")
    model = HanziModel()
    app.state.model = model
    print("Model loaded")

    yield

    print("Shutting down...")


app = FastAPI(
    title="LearnHanzi Recognition Service",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recognition.router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}