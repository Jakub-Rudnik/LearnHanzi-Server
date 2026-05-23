from pydantic import BaseModel, Field
from typing import Optional, List

class HanziCreate(BaseModel):
    character: str = Field(..., max_length=10)
    pinyin: str
    meaning_pl: str
    meaning_en: str
    difficulty_level: int = Field(..., ge=1, le=6)
    theme_category: Optional[str] = None

class HanziResponse(BaseModel):
    id: int
    character: str
    pinyin: str
    meaning_pl: str
    meaning_en: str
    difficulty_level: int
    theme_category: Optional[str]

    class Config:
        from_attributes = True

class HanziUpdate(BaseModel):
    character: Optional[str] = None
    pinyin: Optional[str] = None
    meaning_pl: Optional[str] = None
    meaning_en: Optional[str] = None
    difficulty_level: Optional[int] = None
    theme_category: Optional[str] = None

class HanziListResponse(BaseModel):
    items: List[HanziResponse]
    total: int
    limit: int
    offset: int
