from __future__ import annotations

from statistics import mean
from typing import Any

from models import CandidateFeatures
from utils import clamp, safe_float, safe_get, safe_int


TIER_SCORE = {
    'tier_1': 1.00,
    'tier_2': 0.85,
    'tier_3': 0.70,
    'tier_4': 0.55,
    'unknown': 0.60,
}


class FeatureExtractor:
    def education_score(self, candidate: Any) -> float:
        edus = safe_get(candidate, 'education', []) or []
        if not edus:
            return 0.60
        scores = []
        for e in edus:
            tier = str(safe_get(e, 'tier', 'unknown')).lower()
            tier_score = TIER_SCORE.get(tier, 0.60)
            degree = str(safe_get(e, 'degree', '')).lower()
            field = str(safe_get(e, 'field_of_study', '')).lower()
            bonus = 0.0
            if any(k in field for k in ('computer science','ai','artificial intelligence','machine learning','data science','information retrieval')):
                bonus += 0.10
            if any(k in degree for k in ('phd','doctor','master','m.tech','mtech','msc','b.tech','btech','be','b.e')):
                bonus += 0.05
            scores.append(clamp(tier_score + bonus, 0.0, 1.0))
        return mean(scores)

    def build(self, candidate: Any) -> CandidateFeatures:
        skill_list = safe_get(candidate, 'skills', []) or []
        expert_count = 0
        endorsements, durations = [], []
        for s in skill_list:
            prof = str(safe_get(s, 'proficiency', 'beginner')).lower()
            if prof == 'expert':
                expert_count += 1
            endorsements.append(safe_int(safe_get(s, 'endorsements', 0), 0))
            durations.append(safe_int(safe_get(s, 'duration_months', 0), 0))

        sig = safe_get(candidate, 'redrob_signals', None)
        raw = safe_get(sig, 'raw', sig if isinstance(sig, dict) else {}) or {}
        profile = safe_get(candidate, 'profile', {}) or {}

        return CandidateFeatures(
            candidate_id=str(safe_get(candidate, 'candidate_id', '')),
            years_experience=safe_float(profile.get('years_of_experience', 0.0), 0.0),
            skill_count=len(skill_list),
            expert_skill_count=expert_count,
            avg_endorsements=mean(endorsements) if endorsements else 0.0,
            avg_skill_duration=mean(durations) if durations else 0.0,
            github_score=safe_float(raw.get('github_activity_score', -1.0), -1.0),
            recruiter_response=safe_float(raw.get('recruiter_response_rate', 0.0), 0.0),
            interview_completion=safe_float(raw.get('interview_completion_rate', 0.0), 0.0),
            profile_score=safe_float(raw.get('profile_completeness_score', 0.0), 0.0),
            education_score=self.education_score(candidate),
            open_to_work=1.0 if bool(raw.get('open_to_work_flag', False)) else 0.0,
            notice_period_days=safe_int(raw.get('notice_period_days', 180), 180),
            title=str(profile.get('current_title', '')),
            industry=str(profile.get('current_industry', '')),
            current_company=str(profile.get('current_company', '')),
            current_company_size=str(profile.get('current_company_size', '')),
            current_industry=str(profile.get('current_industry', '')),
            location=str(profile.get('location', '')),
        )
