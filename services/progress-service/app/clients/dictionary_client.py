# app/clients/dictionary_client.py
import requests
from app.core.config import settings

def get_hanzi(hanzi_id):
    r = requests.get(f"{settings.dictionary_url}/hanzi/{hanzi_id}")
    r.raise_for_status()
    return r.json()
