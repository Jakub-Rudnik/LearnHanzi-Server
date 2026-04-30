from pydantic import BaseModel


class RecognitionRequest(BaseModel):
    image_base64: str
    character: str | None = None


class PredictionItem(BaseModel):
    character: str
    confidence: float


class RecognitionResponse(BaseModel):
    character: str
    confidence: float
    top_predictions: list[PredictionItem] | None = None
