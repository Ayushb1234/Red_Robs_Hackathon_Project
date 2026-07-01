from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

import numpy as np

from embedding import EmbeddingEngine


@dataclass
class RetrievalResult:
    indices: List[int]
    scores: List[float]


class RetrievalEngine:
    def __init__(self, embedding_engine: EmbeddingEngine | None = None):
        self.embedding_engine = embedding_engine or EmbeddingEngine()

    def retrieve(self, query_text: str, candidate_texts: Sequence[str], top_k: int = 1000) -> RetrievalResult:
        if not candidate_texts:
            return RetrievalResult(indices=[], scores=[])
        q = self.embedding_engine.encode_one(query_text)
        C = self.embedding_engine.encode(candidate_texts)
        scores = (C @ q.T).toarray().ravel()
        top_k = min(int(top_k), len(scores))
        idx = np.argpartition(-scores, top_k - 1)[:top_k]
        idx = idx[np.argsort(-scores[idx], kind='mergesort')]
        return RetrievalResult(indices=idx.tolist(), scores=scores[idx].astype(float).tolist())
