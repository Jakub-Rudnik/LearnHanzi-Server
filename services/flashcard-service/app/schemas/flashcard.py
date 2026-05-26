from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HanziRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    character: str
    pinyin: str
    meaning_pl: str
    meaning_en: str
    difficulty_level: int
    theme_category: str | None = None


class FlashcardItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    hanzi_id: UUID
    position: int


class FlashcardSetCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: str | None = Field(default=None, max_length=500)
    hanzi_ids: list[UUID] = Field(..., min_length=1)


class FlashcardSetUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    hanzi_ids: list[UUID] | None = Field(default=None, min_length=1)


class FlashcardSetSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    cards_count: int
    created_at: datetime
    updated_at: datetime


class FlashcardSetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    cards_count: int
    cards: list[FlashcardItemRead]
    created_at: datetime
    updated_at: datetime


class StudyCardRead(BaseModel):
    card_id: UUID
    set_id: UUID
    position: int
    hanzi: HanziRead
    is_favorite: bool
    is_difficult: bool


class StudySetRead(BaseModel):
    set_id: UUID
    set_name: str
    description: str | None
    cards: list[StudyCardRead]


class FlashcardStateUpdate(BaseModel):
    is_favorite: bool | None = None
    is_difficult: bool | None = None


class FlashcardStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    hanzi_id: UUID
    is_favorite: bool
    is_difficult: bool
    updated_at: datetime


class MarkedHanziRead(BaseModel):
    state: FlashcardStateRead | None = None
    hanzi: HanziRead

