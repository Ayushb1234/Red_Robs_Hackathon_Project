# career_reasoner.py
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

AI_TOPICS = {
    "retrieval": [
        "retrieval",
        "semantic search",
        "dense retrieval",
        "vector search",
        "faiss",
        "pinecone",
        "qdrant",
        "weaviate",
        "milvus",
    ],
    "ranking": [
        "ranking",
        "recommendation",
        "recommender",
        "matching",
        "relevance",
        "search",
    ],
    "embeddings": [
        "embedding",
        "embeddings",
        "sentence transformer",
        "sentence-transformer",
        "bge",
        "e5",
        "openai embedding",
    ],
    "llm": [
        "llm",
        "gpt",
        "transformer",
        "bert",
        "t5",
        "llama",
    ],
    "production": [
        "production",
        "deployed",
        "serving",
        "inference",
        "latency",
        "pipeline",
        "microservice",
        "scalable",
        "shipped",
        "launched",
    ],
}

# Stronger signals than generic buzzwords
ROLE_SIGNALS = {
    "search": ["search engineer", "search relevance", "search ranking", "search platform"],
    "retrieval": ["retrieval system", "vector database", "vector search", "semantic search"],
    "ranking": ["ranking system", "ranker", "learning to rank", "re-ranking"],
    "recommendation": ["recommendation system", "recommender system", "personalization"],
    "production_ml": ["production ml", "ml platform", "model serving", "feature store", "deployment"],
}

# Counts more when these appear in the career history text
EVIDENCE_WEIGHTS = {
    "retrieval": 1.4,
    "ranking": 1.4,
    "embeddings": 1.2,
    "llm": 0.8,
    "production": 1.6,
}

def _norm(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())

def _get(obj: Any, key: str, default: Any = "") -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

class CareerReasoner:
    """
    Produces a career-relevance score based on evidence from titles, descriptions,
    companies, and other career-history text.

    Returns:
        {
            "career_score": float,
            "evidence": [str, ...],
            "match_counts": {topic: count}
        }
    """

    def analyze(self, candidate: Any) -> Dict[str, Any]:
        text_parts: List[str] = []

        for c in _get(candidate, "career_history", []) or []:
            text_parts.append(_norm(_get(c, "title", "")))
            text_parts.append(_norm(_get(c, "description", "")))
            text_parts.append(_norm(_get(c, "company", "")))
            text_parts.append(_norm(_get(c, "industry", "")))

        text = " ".join(text_parts)

        evidence: List[str] = []
        match_counts: Dict[str, int] = {}
        score = 0.0

        # Topic-level evidence
        for topic, keywords in AI_TOPICS.items():
            hits = 0
            for kw in keywords:
                kw_n = _norm(kw)
                if kw_n and kw_n in text:
                    hits += 1

            if hits > 0:
                match_counts[topic] = hits
                evidence.append(topic)

                # diminishing returns so spammy keyword stuffing doesn't dominate
                score += EVIDENCE_WEIGHTS.get(topic, 1.0) * (1.0 + 0.15 * (hits - 1))

        # Stronger role evidence from phrases in job history
        for role_topic, phrases in ROLE_SIGNALS.items():
            for phrase in phrases:
                if _norm(phrase) in text:
                    score += 1.25
                    evidence.append(role_topic)
                    break

        # Production + AI combo bonus
        has_production = any(t in evidence for t in ["production"])
        has_core_ai = any(t in evidence for t in ["retrieval", "ranking", "embeddings"])
        if has_production and has_core_ai:
            score += 1.5
            evidence.append("production_ai_combo")

        # If there is only LLM buzz but no retrieval/ranking/production, downweight a bit
        if "llm" in evidence and not (has_core_ai or has_production):
            score *= 0.75
            evidence.append("llm_without_system_evidence")

        return {
            "career_score": round(score, 4),
            "evidence": sorted(set(evidence)),
            "match_counts": match_counts,
        }