from __future__ import annotations

from typing import Iterable, List, Sequence, Union, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

try:
    from config import EMBEDDING_MODEL
except Exception:
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"


TextInput = Union[str, Sequence[str]]


class EmbeddingEngine:
    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        device: Optional[str] = None,
        cache_folder: Optional[str] = None,
    ):
        self.model_name = model_name
        self.device = device
        self.cache_folder = cache_folder
        self.model: Optional[SentenceTransformer] = None

    def _load_model(self) -> SentenceTransformer:
        if self.model is None:
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=self.cache_folder,
            )
        return self.model

    def encode(
        self,
        texts: TextInput,
        batch_size: int = 64,
        normalize_embeddings: bool = True,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        model = self._load_model()

        if isinstance(texts, str):
            texts = [texts]
        else:
            texts = list(texts)

        if not texts:
            return np.zeros((0, 384), dtype=np.float32)

        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=normalize_embeddings,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True,
        )

        return np.asarray(embeddings, dtype=np.float32)

    def encode_one(
        self,
        text: str,
        normalize_embeddings: bool = True,
    ) -> np.ndarray:
        return self.encode(
            [text],
            normalize_embeddings=normalize_embeddings,
            show_progress_bar=False,
        )[0]