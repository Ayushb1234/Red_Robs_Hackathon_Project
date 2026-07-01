from __future__ import annotations

from typing import Sequence, Union

from scipy import sparse
from sklearn.feature_extraction.text import HashingVectorizer

from config import HASHING_N_FEATURES, HASHING_NGRAM_RANGE

TextInput = Union[str, Sequence[str]]


class EmbeddingEngine:
    def __init__(self, n_features: int = HASHING_N_FEATURES, ngram_range: tuple[int, int] = HASHING_NGRAM_RANGE):
        self.vectorizer = HashingVectorizer(
            n_features=n_features,
            alternate_sign=False,
            norm='l2',
            lowercase=True,
            ngram_range=ngram_range,
            stop_words='english',
        )
        self.dim = n_features

    def encode(self, texts: TextInput):
        if isinstance(texts, str):
            texts = [texts]
        else:
            texts = list(texts)
        if not texts:
            return sparse.csr_matrix((0, self.dim), dtype='float32')
        return self.vectorizer.transform(texts).astype('float32')

    def encode_one(self, text: str):
        return self.encode([text])[0]
