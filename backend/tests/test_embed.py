import math
from types import SimpleNamespace
from typing import Any

import pytest
from google.genai import errors
from tenacity import wait_none

from app.rag.embed import BATCH_SIZE, GeminiEmbedder, normalize


class FakeModels:
    def __init__(self, dim: int, failures: list[int] | None = None) -> None:
        self.dim = dim
        self.calls: list[dict[str, Any]] = []
        self.failures = failures or []

    async def embed_content(self, *, model: str, contents: list[str], config: Any) -> Any:
        self.calls.append({"model": model, "n": len(contents), "config": config})
        if self.failures:
            raise errors.APIError(self.failures.pop(0), {"error": {"message": "x"}})
        embeddings = [SimpleNamespace(values=[3.0, 4.0] + [0.0] * (self.dim - 2)) for _ in contents]
        return SimpleNamespace(embeddings=embeddings)


def embedder(models: FakeModels, dim: int = 8) -> GeminiEmbedder:
    client: Any = SimpleNamespace(aio=SimpleNamespace(models=models))
    return GeminiEmbedder(client, "test-model", dim=dim, wait=wait_none())


def test_normalize() -> None:
    assert normalize([3.0, 4.0]) == [0.6, 0.8]
    assert normalize([0.0, 0.0]) == [0.0, 0.0]


async def test_batches_and_normalizes() -> None:
    models = FakeModels(dim=8)
    vectors = await embedder(models).embed(["t"] * (BATCH_SIZE * 2 + 5), "RETRIEVAL_DOCUMENT")
    assert [c["n"] for c in models.calls] == [BATCH_SIZE, BATCH_SIZE, 5]
    assert len(vectors) == BATCH_SIZE * 2 + 5
    assert math.isclose(math.sqrt(sum(x * x for x in vectors[0])), 1.0)
    config = models.calls[0]["config"]
    assert (config.task_type, config.output_dimensionality) == ("RETRIEVAL_DOCUMENT", 8)


async def test_retries_rate_limit_then_succeeds() -> None:
    models = FakeModels(dim=8, failures=[429, 503])
    vectors = await embedder(models).embed(["a"], "RETRIEVAL_QUERY")
    assert len(vectors) == 1 and len(models.calls) == 3


async def test_client_error_is_not_retried() -> None:
    models = FakeModels(dim=8, failures=[400])
    with pytest.raises(errors.APIError):
        await embedder(models).embed(["a"], "RETRIEVAL_QUERY")
    assert len(models.calls) == 1


async def test_wrong_dimension_is_rejected() -> None:
    with pytest.raises(ValueError, match="does not match"):
        await embedder(FakeModels(dim=4), dim=8).embed(["a"], "RETRIEVAL_QUERY")
