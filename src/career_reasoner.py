from __future__ import annotations

from typing import Any, Dict, List

from config import JD_CONCEPTS
from normalizer import normalize_text
from utils import dedupe_keep_order, safe_get


ROLE_SIGNALS = {
    'search': ['search engineer', 'search relevance', 'search ranking', 'search platform'],
    'retrieval': ['retrieval system', 'vector database', 'vector search', 'semantic search'],
    'ranking': ['ranking system', 'ranker', 'learning to rank', 're-ranking'],
    'recommendation': ['recommendation system', 'recommender system', 'personalization'],
    'production_ml': ['production ml', 'ml platform', 'model serving', 'feature store', 'deployment'],
}

EVIDENCE_WEIGHTS = {'retrieval': 1.4, 'ranking': 1.4, 'embeddings': 1.2, 'llm': 0.8, 'production': 1.6}


class CareerReasoner:
    def analyze(self, candidate: Any) -> Dict[str, Any]:
        parts: List[str] = []
        for c in safe_get(candidate, 'career_history', []) or []:
            parts.append(normalize_text(safe_get(c, 'title', '')))
            parts.append(normalize_text(safe_get(c, 'description', '')))
            parts.append(normalize_text(safe_get(c, 'company', '')))
            parts.append(normalize_text(safe_get(c, 'industry', '')))
        text = ' '.join(parts)

        evidence: List[str] = []
        match_counts: Dict[str, int] = {}
        score = 0.0

        for topic, keywords in JD_CONCEPTS.items():
            hits = sum(1 for kw in keywords if normalize_text(kw) in text)
            if hits:
                match_counts[topic] = hits
                evidence.append(topic)
                score += EVIDENCE_WEIGHTS.get(topic, 1.0) * (1.0 + 0.15 * (hits - 1))

        for role_topic, phrases in ROLE_SIGNALS.items():
            if any(normalize_text(p) in text for p in phrases):
                score += 1.25
                evidence.append(role_topic)

        if 'production' in evidence and any(t in evidence for t in ['retrieval', 'ranking', 'embeddings']):
            score += 1.5
            evidence.append('production_ai_combo')
        if 'llm' in evidence and not any(t in evidence for t in ['retrieval', 'ranking', 'embeddings', 'production']):
            score *= 0.75
            evidence.append('llm_without_system_evidence')

        return {'career_score': round(score, 4), 'evidence': dedupe_keep_order(evidence), 'match_counts': match_counts, 'career_text': text}
