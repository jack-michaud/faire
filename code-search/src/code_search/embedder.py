"""Embedding with nomic-embed-text-v1.5 via fastembed (ONNX)."""

import numpy as np


class Embedder:
    """Lazy-loaded embedding model using fastembed."""

    MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
    DIMENSIONS = 256  # Matryoshka truncation

    def __init__(self):
        self._model = None

    def _ensure_model(self):
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(model_name=self.MODEL_NAME)

    def embed_documents(self, texts: list[str]) -> list[np.ndarray]:
        """Embed document texts with 'search_document:' prefix."""
        if not texts:
            return []
        self._ensure_model()
        prefixed = [f"search_document: {t}" for t in texts]
        embeddings = list(self._model.embed(prefixed))
        return [e[: self.DIMENSIONS].astype(np.float32) for e in embeddings]

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a search query with 'search_query:' prefix."""
        self._ensure_model()
        prefixed = [f"search_query: {query}"]
        embeddings = list(self._model.embed(prefixed))
        return embeddings[0][: self.DIMENSIONS].astype(np.float32)
