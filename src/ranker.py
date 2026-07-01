from __future__ import annotations

from typing import List, Sequence

import numpy as np

from anomaly_detector import AnomalyDetector
from behaviour_score import BehaviorScorer
from career_reasoner import CareerReasoner
from config import SHORTLIST_SIZE, TOP_K, WEIGHTS
from document_builder import CandidateDocumentBuilder
from feature_engineering import FeatureExtractor
from jd_parser import JDParser
from models import Candidate, JobDescription, RankResult
from normalizer import normalize_title, normalize_text
from retrieval import RetrievalEngine
from skill_matcher import SkillMatcher
from utils import clamp, safe_get


class HybridRanker:
    def __init__(self):
        self.jdp = JDParser()
        self.feature_extractor = FeatureExtractor()
        self.doc_builder = CandidateDocumentBuilder()
        self.retrieval = RetrievalEngine()
        self.career_reasoner = CareerReasoner()
        self.skill_matcher = SkillMatcher()
        self.behavior_scorer = BehaviorScorer()
        self.anomaly_detector = AnomalyDetector()

    def _title_score(self, candidate: Candidate, jd: JobDescription) -> float:
        title = normalize_title(safe_get(candidate, 'profile', {}).get('current_title', ''))
        if not title:
            return 0.0
        role = normalize_title(jd.role)
        if role and role in title:
            return 1.0
        text = f"{title} {normalize_text(safe_get(candidate, 'profile', {}).get('headline', ''))}"
        for t in ['ml engineer', 'ai engineer', 'machine learning engineer', 'search engineer', 'ranking engineer', 'recommendation engineer', 'retrieval engineer', 'nlp engineer', 'data scientist', 'applied scientist']:
            if t in text:
                return 0.8 if 'engineer' in t else 0.6
        return 0.0

    def _experience_score(self, years: float, jd: JobDescription) -> float:
        lo = max(1, int(jd.experience_min or 5))
        hi = max(lo, int(jd.experience_max or 9))
        if years < lo:
            return clamp(years / float(lo))
        if years <= hi:
            return 1.0
        if years <= hi + 3:
            return 0.92
        return 0.80

    def _build_query_text(self, jd: JobDescription) -> str:
        parts = [jd.role, jd.company, jd.location, jd.employment_type, ' '.join(jd.required_skills or []), ' '.join(jd.preferred_skills or []), ' '.join(jd.preferred_titles or []), ' '.join(jd.preferred_industries or []), jd.notes]
        return '\n'.join([p for p in parts if p])

    def rank(self, candidates: Sequence[Candidate], jd_text: str, top_k: int = TOP_K) -> List[RankResult]:
        jd = self.jdp.parse(jd_text)
        query_text = self._build_query_text(jd)
        if not candidates:
            return []

        feats = [self.feature_extractor.build(c) for c in candidates]
        heuristic_scores = []
        for cand, feat in zip(candidates, feats):
            skill_score, _ = self.skill_matcher.score(cand, jd)
            exp_score = self._experience_score(feat.years_experience, jd)
            beh_score = self.behavior_scorer.score(cand)
            career_score = clamp(self.career_reasoner.analyze(cand)['career_score'] / 8.0)
            title_score = self._title_score(cand, jd)
            github = 0.0 if feat.github_score < 0 else clamp(feat.github_score / 100.0)
            heuristic_scores.append(clamp(0.30*skill_score + 0.20*career_score + 0.15*beh_score + 0.12*exp_score + 0.08*feat.education_score + 0.08*title_score + 0.07*github))

        shortlist_n = min(SHORTLIST_SIZE, len(candidates))
        h_arr = np.asarray(heuristic_scores, dtype=np.float32)
        shortlist_idx = np.argpartition(-h_arr, shortlist_n - 1)[:shortlist_n]
        shortlist_idx = shortlist_idx[np.argsort(-h_arr[shortlist_idx], kind='mergesort')]

        shortlisted = [candidates[i] for i in shortlist_idx]
        shortlisted_feats = [feats[i] for i in shortlist_idx]
        shortlisted_docs = [self.doc_builder.build(c) for c in shortlisted]

        q_vec = self.retrieval.embedding_engine.encode_one(query_text)
        cand_mat = self.retrieval.embedding_engine.encode(shortlisted_docs)
        semantic_scores = (cand_mat @ q_vec.T).toarray().ravel() if len(shortlisted_docs) else np.array([], dtype=np.float32)

        results: List[RankResult] = []
        for cand, feat, sem in zip(shortlisted, shortlisted_feats, semantic_scores):
            skill_score, skill_evidence = self.skill_matcher.score(cand, jd)
            career_result = self.career_reasoner.analyze(cand)
            behavior_score = self.behavior_scorer.score(cand)
            anomaly_penalty, flags = self.anomaly_detector.analyze(cand)
            penalty_multiplier = max(0.05, 1.0 - anomaly_penalty)
            exp_score = self._experience_score(feat.years_experience, jd)
            title_score = self._title_score(cand, jd)
            edu_score = feat.education_score
            github = 0.0 if feat.github_score < 0 else clamp(feat.github_score / 100.0)

            base = (
                WEIGHTS['semantic'] * clamp(float(sem)) +
                WEIGHTS['career'] * clamp(career_result['career_score'] / 8.0) +
                WEIGHTS['skills'] * clamp(skill_score) +
                WEIGHTS['behavior'] * clamp(behavior_score) +
                WEIGHTS['experience'] * clamp(exp_score) +
                WEIGHTS['education'] * clamp(edu_score) +
                WEIGHTS['github'] * clamp(github) +
                WEIGHTS['title'] * clamp(title_score)
            )
            final_score = clamp(base) * penalty_multiplier
            sig = getattr(cand.redrob_signals, 'raw', {}) or {}
            behavior_evidence = []
            if sig.get('open_to_work_flag', False): behavior_evidence.append('open_to_work')
            if sig.get('recruiter_response_rate', 0.0) >= 0.5: behavior_evidence.append('recruiter_response')
            if sig.get('verified_email', False): behavior_evidence.append('verified_email')
            if sig.get('verified_phone', False): behavior_evidence.append('verified_phone')

            results.append(RankResult(
                candidate_id=cand.candidate_id,
                score=round(float(final_score), 6),
                semantic_score=round(float(sem), 6),
                career_score=round(float(clamp(career_result['career_score'] / 8.0)), 6),
                skill_score=round(float(skill_score), 6),
                behavior_score=round(float(behavior_score), 6),
                experience_score=round(float(exp_score), 6),
                education_score=round(float(edu_score), 6),
                title_score=round(float(title_score), 6),
                github_score=round(float(github), 6),
                penalty_multiplier=round(float(penalty_multiplier), 6),
                penalty_flags=flags,
                career_evidence=career_result.get('evidence', []),
                skill_evidence=skill_evidence,
                behavior_evidence=behavior_evidence,
            ))

        results.sort(key=lambda r: (-r.score, r.candidate_id))
        prev = None
        for r in results:
            if prev is not None and r.score > prev:
                r.score = prev
            prev = r.score
        return results[:top_k]
