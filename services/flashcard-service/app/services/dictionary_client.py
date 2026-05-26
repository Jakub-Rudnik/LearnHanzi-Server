from __future__ import annotations

from uuid import UUID

import httpx

from app.core.config import settings


class DictionaryServiceError(RuntimeError):
    pass


class HanziNotFoundError(DictionaryServiceError):
    pass


def get_hanzi(hanzi_id: UUID) -> dict:
    url = f"{settings.dictionary_service_url.rstrip('/')}/hanzi/{hanzi_id}"

    try:
        response = httpx.get(url, timeout=10.0)
    except httpx.RequestError as exc:
        raise DictionaryServiceError("Dictionary service is unavailable") from exc

    if response.status_code == 404:
        raise HanziNotFoundError(f"Hanzi {hanzi_id} not found")

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise DictionaryServiceError("Dictionary service returned an error") from exc

    return response.json()


def get_hanzi_many(hanzi_ids: list[UUID]) -> list[dict]:
    return [get_hanzi(hanzi_id) for hanzi_id in hanzi_ids]

