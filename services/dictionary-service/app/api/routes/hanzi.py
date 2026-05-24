from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db

from app.schemas.hanzi import (
    HanziResponse,
    HanziCreate,
)

from app.services.hanzi_service import (
    list_hanzi,
    get_by_id,
    get_by_character,
)

router = APIRouter(
    prefix="/hanzi",
    tags=["hanzi"],
)

@router.get("/", response_model=list[HanziResponse])
def get_all_hanzi(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return list_hanzi(db, limit=limit, offset=offset)

@router.get("/{hanzi_id}", response_model=HanziResponse)
def get_hanzi_by_id_endpoint(
    hanzi_id: int,
    db: Session = Depends(get_db),
):
    hanzi = get_by_id(db, hanzi_id)

    if not hanzi:
        raise HTTPException(
            status_code=404,
            detail="Hanzi not found",
        )

    return hanzi

@router.get("/character/{character}", response_model=HanziResponse)
def get_hanzi_by_character_endpoint(
    character: str,
    db: Session = Depends(get_db),
):
    hanzi = get_by_character(db, character)

    if not hanzi:
        raise HTTPException(
            status_code=404,
            detail="Hanzi not found",
        )

    return hanzi
