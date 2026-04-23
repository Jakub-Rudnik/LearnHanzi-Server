from fastapi import APIRouter, Request
from app.schemas.recognition import RecognitionRequest, RecognitionResponse

router = APIRouter(tags=["recognition"])


@router.post("/recognize", response_model=RecognitionResponse)
async def recognize_hanzi(request_data: RecognitionRequest, request: Request):

    model = request.app.state.model

    predictions = model.predict(request_data.image_base64, topk=5)

    return RecognitionResponse(
        character=predictions[0]["character"],
        confidence=predictions[0]["confidence"],
        top_predictions=predictions
    )