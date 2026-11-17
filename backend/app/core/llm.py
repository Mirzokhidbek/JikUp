from functools import lru_cache

from google import genai

from app.core.config import get_settings
from app.rag.embed import Embedder, GeminiEmbedder


@lru_cache(maxsize=1)
def get_llm_client() -> genai.Client | None:
    api_key = get_settings().gemini_api_key.get_secret_value()
    return genai.Client(api_key=api_key) if api_key else None


def get_embedder() -> Embedder | None:
    client = get_llm_client()
    return GeminiEmbedder(client, get_settings().gemini_embed_model) if client else None
