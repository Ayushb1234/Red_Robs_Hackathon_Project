from __future__ import annotations

import math
import re
from datetime import date, datetime
from typing import Any, Iterable, List, Optional, Tuple

from config import CONSULTING_COMPANIES, LOW_FIT_TITLES, PENALTY_CLAMP
from utils import days_since, safe_float, safe_int

_RESEARCH_KEYWORDS = {'research','researcher','research scientist','scientist','phd','publication','papers','academic','postdoc','postdoctoral','lab','thesis'}
_PRODUCT_KEYWORDS = {'production','deployed','serving','shipped','launched','users','customer','revenue','latency','throughput','scalable','pipeline','microservice','api','ranking','retrieval','recommendation','search','embedding','vector'}
_AI_BUZZWORDS = {'llm','rag','openai','claude','langchain','crewai','pinecone','qdrant','weaviate','milvus','faiss','embedding','embeddings','sentence transformer','sentence-transformer','bge','e5','transformer','bert','t5','gpt','agent','agents'}


def _norm(s: str) -> str:
    return re.sub(r'\s+', ' ', str(s or '').strip().lower())


def _safe_date(value: Any) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(str(value), '%Y-%m-%d').date()
    except Exception:
        return None


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class AnomalyDetector:
    def __init__(self, consulting_companies: Optional[Iterable[str]] = None, low_fit_titles: Optional[Iterable[str]] = None,
                 research_keywords: Optional[Iterable[str]] = None, product_keywords: Optional[Iterable[str]] = None,
                 ai_buzzwords: Optional[Iterable[str]] = None) -> None:
        self.consulting_companies = {_norm(x) for x in (consulting_companies or CONSULTING_COMPANIES)}
        self.low_fit_titles = {_norm(x) for x in (low_fit_titles or LOW_FIT_TITLES)}
        self.research_keywords = {_norm(x) for x in (research_keywords or _RESEARCH_KEYWORDS)}
        self.product_keywords = {_norm(x) for x in (product_keywords or _PRODUCT_KEYWORDS)}
        self.ai_buzzwords = {_norm(x) for x in (ai_buzzwords or _AI_BUZZWORDS)}

    def penalty(self, candidate: Any) -> float:
        penalty, _ = self.analyze(candidate)
        return penalty

    def multiplier(self, candidate: Any) -> float:
        return max(0.05, 1.0 - self.penalty(candidate))

    def analyze(self, candidate: Any) -> Tuple[float, List[str]]:
        flags: List[str] = []
        penalty = 0.0
        profile = _get(candidate, 'profile', {}) or {}
        sig = _get(candidate, 'redrob_signals', {}) or {}
        career = list(_get(candidate, 'career_history', []) or [])
        skills = list(_get(candidate, 'skills', []) or [])

        skill_names, seen = [], set()
        expert_count = duplicate_count = low_duration_count = 0
        for s in skills:
            name = _norm(_get(s, 'name', ''))
            if not name:
                continue
            skill_names.append(name)
            if name in seen:
                duplicate_count += 1
            else:
                seen.add(name)
            if _norm(_get(s, 'proficiency', '')) == 'expert':
                expert_count += 1
            try:
                dur = int(_get(s, 'duration_months', 0) or 0)
            except Exception:
                dur = 0
            if dur <= 6:
                low_duration_count += 1

        skill_count = len(skill_names)
        if skill_count > 120:
            penalty += 0.18; flags.append('excessive_skill_count')
        if expert_count > 40:
            penalty += 0.18; flags.append('too_many_expert_skills')
        if skill_count >= 20 and duplicate_count / max(1, skill_count) > 0.20:
            penalty += 0.08; flags.append('duplicate_skill_stuffing')
        if skill_count >= 25 and low_duration_count / max(1, skill_count) > 0.75:
            penalty += 0.06; flags.append('skills_with_too_little_usage')

        buzz_count = sum(1 for name in skill_names for kw in self.ai_buzzwords if kw and kw in name)
        career_text = self._career_text(candidate)
        career_ai_hits = sum(1 for kw in self.ai_buzzwords if kw in career_text)
        if buzz_count >= 6 and career_ai_hits <= 1:
            penalty += 0.14; flags.append('ai_keyword_stuffing')
        elif buzz_count >= 4 and career_ai_hits == 0:
            penalty += 0.10; flags.append('ai_keywords_without_career_evidence')

        years = self._years_of_experience(candidate)
        if years is not None:
            if years < 0:
                penalty += 0.40; flags.append('negative_experience')
            elif years > 40:
                penalty += 0.25; flags.append('implausibly_high_experience')
        if self._has_bad_career_dates(career):
            penalty += 0.14; flags.append('invalid_career_dates')
        if self._severe_timeline_mismatch(candidate):
            penalty += 0.12; flags.append('timeline_mismatch')
        if career and self._is_consulting_only(career):
            penalty += 0.12; flags.append('consulting_only_career')
        if self._is_research_only(career):
            penalty += 0.14; flags.append('research_only_career')

        current_title = _norm(_get(profile, 'current_title', ''))
        if current_title in self.low_fit_titles and not self._has_relevant_engineering_evidence(candidate):
            penalty += 0.12; flags.append('low_fit_title_without_support')
        if current_title and any(t in current_title for t in ('manager','writer','designer','support','sales','hr','accountant')):
            if buzz_count >= 4 and not self._has_relevant_engineering_evidence(candidate):
                penalty += 0.10; flags.append('non_engineering_title_with_ai_keywords')

        last_active_days = days_since(sig.get('last_active_date'))
        if last_active_days is not None:
            if last_active_days > 365:
                penalty += 0.15; flags.append('inactive_over_one_year')
            elif last_active_days > 180:
                penalty += 0.10; flags.append('inactive_over_six_months')
            elif last_active_days > 90:
                penalty += 0.05; flags.append('inactive_over_three_months')

        open_to_work = bool(sig.get('open_to_work_flag', False))
        response_rate = safe_float(sig.get('recruiter_response_rate', 0.0), 0.0)
        response_time = safe_float(sig.get('avg_response_time_hours', 0.0), 0.0)
        notice_days = safe_int(sig.get('notice_period_days', 999), 999)
        if not open_to_work and (last_active_days is not None and last_active_days > 90):
            penalty += 0.08; flags.append('not_open_to_work_and_stale')
        if response_rate < 0.15:
            penalty += 0.08; flags.append('very_low_recruiter_response')
        elif response_rate < 0.30:
            penalty += 0.05; flags.append('low_recruiter_response')
        if response_time > 72:
            penalty += 0.04; flags.append('slow_recruiter_response')
        elif response_time > 24:
            penalty += 0.02; flags.append('moderate_recruiter_response')
        if notice_days > 90:
            penalty += 0.03; flags.append('long_notice_period')
        elif notice_days > 60:
            penalty += 0.02; flags.append('medium_notice_period')

        completeness = safe_float(sig.get('profile_completeness_score', 0.0), 0.0)
        if completeness < 40:
            penalty += 0.04; flags.append('very_low_profile_completeness')
        github = safe_float(sig.get('github_activity_score', -1.0), -1.0)
        if github != -1 and github < 10:
            penalty += 0.03; flags.append('weak_github_activity')
        interview_completion = safe_float(sig.get('interview_completion_rate', 0.0), 0.0)
        if interview_completion < 0.2:
            penalty += 0.05; flags.append('very_low_interview_completion')
        elif interview_completion < 0.5:
            penalty += 0.03; flags.append('low_interview_completion')
        offer_acceptance = safe_float(sig.get('offer_acceptance_rate', -1.0), -1.0)
        if 0.0 <= offer_acceptance < 0.15:
            penalty += 0.03; flags.append('low_offer_acceptance')

        return min(max(penalty, 0.0), PENALTY_CLAMP), flags

    def _years_of_experience(self, candidate: Any):
        profile = _get(candidate, 'profile', {}) or {}
        y = _get(profile, 'years_of_experience', None)
        if y is None:
            return None
        try:
            return float(y)
        except Exception:
            return None

    def _career_text(self, candidate: Any) -> str:
        parts = []
        for c in _get(candidate, 'career_history', []) or []:
            parts.extend([str(_get(c, 'title', '')), str(_get(c, 'company', '')), str(_get(c, 'industry', '')), str(_get(c, 'description', ''))])
        return _norm(' '.join(parts))

    def _has_relevant_engineering_evidence(self, candidate: Any) -> bool:
        text = self._career_text(candidate)
        hits = ['engineer','engineering','developer','software','backend','platform','ml','machine learning','ai','data','search','retrieval','recommendation','ranking','production','deployed','serving','inference','pipeline','api','python']
        return any(k in text for k in hits)

    def _is_consulting_only(self, career: List[Any]) -> bool:
        companies = [_norm(_get(c, 'company', '')) for c in career if _norm(_get(c, 'company', ''))]
        if not companies:
            return False
        consulting_hits = sum(1 for c in companies if any(cons in c for cons in self.consulting_companies))
        return consulting_hits >= max(2, math.ceil(0.8 * len(companies)))

    def _is_research_only(self, career: List[Any]) -> bool:
        text = ' '.join(_norm(_get(c, 'title', '')) + ' ' + _norm(_get(c, 'description', '')) + ' ' + _norm(_get(c, 'company', '')) for c in career)
        research_hits = sum(1 for kw in self.research_keywords if kw in text)
        product_hits = sum(1 for kw in self.product_keywords if kw in text)
        return research_hits >= 2 and product_hits == 0

    def _has_bad_career_dates(self, career: List[Any]) -> bool:
        for c in career:
            start = _safe_date(_get(c, 'start_date', None))
            end_raw = _get(c, 'end_date', None)
            end = _safe_date(end_raw) if end_raw else None
            if start is None:
                continue
            if end is not None and end < start:
                return True
            try:
                dm = int(_get(c, 'duration_months', 0) or 0)
            except Exception:
                return True
            if dm < 0 or dm > 480:
                return True
        return False

    def _severe_timeline_mismatch(self, candidate: Any) -> bool:
        years = self._years_of_experience(candidate)
        if years is None:
            return False
        total_months = 0
        for c in _get(candidate, 'career_history', []) or []:
            try:
                total_months += max(0, int(_get(c, 'duration_months', 0)))
            except Exception:
                pass
        total_years = total_months / 12.0 if total_months > 0 else 0.0
        return (years < 2 and total_years >= 6) or (years >= 12 and total_years < max(1.5, 0.35 * years))
