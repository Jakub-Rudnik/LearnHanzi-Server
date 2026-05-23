from uuid import UUID

from app.repositories.hanzi import (
    get_all_hanzi,
    get_hanzi_by_id,
    get_hanzi_by_character,
)

def list_hanzi(db, limit: int = 100, offset: int = 0):
    return get_all_hanzi(db, limit=limit, offset=offset)

def get_by_id(db, hanzi_id: UUID):
    hanzi = get_hanzi_by_id(db, hanzi_id)

    if not hanzi:
        return None

    return hanzi

def get_by_character(db, character: str):
    hanzi = get_hanzi_by_character(db, character)

    if not hanzi:
        return None

    return hanzi
