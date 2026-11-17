import math
from collections.abc import Sequence
from typing import Any, Literal, Protocol, cast

from google import genai
from google.genai import errors, types
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential
from tenacity.wait import wait_base

from app.models import EMBED_DIM

BATCH_SIZE = 100
EmbedTask = Literal["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"]
RETRYABLE_CODES = frozenset({429, 500, 502, 503, 504})
DEFAULT_WAIT = wait_exponential(multiplier=1, max=30)


class Embedder(Protocol):
    async def embed(self, texts: Sequence[str], task: EmbedTask) -> list[list[float]]: ...


def normalize(vector: Sequence[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vector))
    return [x / norm for x in vector] if norm else list(vector)


def _is_retryable(exc: BaseException) -> bool:
    return isinstance(exc, errors.APIError) and exc.code in RETRYABLE_CODES


class GeminiEmbedder:
    def __init__(
        self,
        client: genai.Client,
        model: str,
        dim: int = EMBED_DIM,
        wait: wait_base = DEFAULT_WAIT,
    ) -> None:
        self._client = client
        self._model = model
        self._dim = dim
        self._wait = wait

    async def _embed_batch(self, texts: list[str], task: EmbedTask) -> list[list[float]]:
        response = await self._client.aio.models.embed_content(
            model=self._model,
            contents=cast(Any, texts),
            config=types.EmbedContentConfig(task_type=task, output_dimensionality=self._dim),
        )
        vectors = [normalize(e.values or []) for e in response.embeddings or []]
        if len(vectors) != len(texts) or any(len(v) != self._dim for v in vectors):
            raise ValueError("Embedding response does not match the request")
        return vectors

    async def embed(self, texts: Sequence[str], task: EmbedTask) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), BATCH_SIZE):
            retrying = AsyncRetrying(
                retry=retry_if_exception(_is_retryable),
                stop=stop_after_attempt(4),
                wait=self._wait,
                reraise=True,
            )
            batch = list(texts[start : start + BATCH_SIZE])
            vectors.extend(await retrying(self._embed_batch, batch, task))
        return vectors
