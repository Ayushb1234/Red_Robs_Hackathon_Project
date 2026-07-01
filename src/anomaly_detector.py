# anomaly_detector.py
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime, date
from typing import Any, Iterable, List, Optional, Tuple


_CONSULTING_COMPANIES = {
    "tcs",
    "infosys",
    "wipro",
    "accenture",
    "cognizant",
    "capgemini",
    "deloitte",
    "pwc",
    "ey",
    "kpmg",
    "hcl",
    "tech mahindra",
    "ltimindtree",
    "mindtree",
    "ibm",
    "genpact",
    "hexaware",
    "persistent",
}

_LOW_FIT_TITLES = {
    "marketing manager",
    "hr manager",
    "human resources manager",
    "graphic designer",
    "accountant",
    "sales executive",
    "customer support",
    "operations manager",
    "content writer",
    "business analyst",
    "mechanical engineer",
    "civil engineer",
    "project manager",
}

_RESEARCH_KEYWORDS = {
    "research",
    "researcher",
    "research scientist",
    "scientist",
    "phd",
    "publication",
    "papers",
    "academic",
    "postdoc",
    "postdoctoral",
    "lab",
    "thesis",
}

_PRODUCT_KEYWORDS = {
    "production",
    "deployed",
    "serving",
    "shipped",
    "launched",
    "users",
    "customer",
    "revenue",
    "latency",
    "throughput",
    "scalable",
    "pipeline",
    "microservice",
    "api",
    "ranking",
    "retrieval",
    "recommendation",
    "search",
    "embedding",
    "vector",
}

_AI_BUZZWORDS = {
    "llm",
    "rag",
    "openai",
    "claude",
    "langchain",
    "crewai",
    "pinecone",
    "qdrant",
    "weaviate",
    "milvus",
    "faiss",
    "embedding",
    "embeddings",
    "sentence transformer",
    "sentence-transformer",
    "bge",
    "e5",
    "transformer",
    "bert",
    "t5",
    "gpt",
    "agent",
    "agents",
}


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _text(x: Any) -> str:
    if x is None:
        return ""
    return str(x)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", _text(s).strip().lower())


def _safe_date(value: Any) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except Exception:
        return None


def _days_since(value: Any) -> Optional[int]:
    d = _safe_date(value)
    if d is None:
        return None
    return (date.today() - d).days


def _iter_skills(candidate: Any) -> List[Any]:
    skills = _get(candidate, "skills", []) or []
    return list(skills)


def _iter_career(candidate: Any) -> List[Any]:
    career = _get(candidate, "career_history", []) or []
    return list(career)


def _profile(candidate: Any) -> dict:
    profile = _get(candidate, "profile", {}) or {}
    if isinstance(profile, dict):
        return profile
    return {}


def _signals(candidate: Any) -> dict:
    sig = _get(candidate, "redrob_signals", {}) or {}
    if isinstance(sig, dict):
        return sig
    raw = _get(sig, "raw", {})
    if isinstance(raw, dict):
        return raw
    return {}


class AnomalyDetector:
    """
    Fast, deterministic candidate risk detector.

    Returns an additive penalty in [0.0, 0.95].
    Use multiplier = max(0.05, 1.0 - penalty) in the ranker if you prefer multiplicative scoring.
    """

    def __init__(
        self,
        consulting_companies: Optional[Iterable[str]] = None,
        low_fit_titles: Optional[Iterable[str]] = None,
        research_keywords: Optional[Iterable[str]] = None,
        product_keywords: Optional[Iterable[str]] = None,
        ai_buzzwords: Optional[Iterable[str]] = None,
    ) -> None:
        self.consulting_companies = { _norm(x) for x in (consulting_companies or _CONSULTING_COMPANIES) }
        self.low_fit_titles = { _norm(x) for x in (low_fit_titles or _LOW_FIT_TITLES) }
        self.research_keywords = { _norm(x) for x in (research_keywords or _RESEARCH_KEYWORDS) }
        self.product_keywords = { _norm(x) for x in (product_keywords or _PRODUCT_KEYWORDS) }
        self.ai_buzzwords = { _norm(x) for x in (ai_buzzwords or _AI_BUZZWORDS) }

    def penalty(self, candidate: Any) -> float:
        """
        Additive anomaly penalty in [0.0, 0.95].
        """
        penalty, _ = self.analyze(candidate)
        return penalty

    def multiplier(self, candidate: Any) -> float:
        """
        Multiplicative trust multiplier in [0.05, 1.0].
        """
        p = self.penalty(candidate)
        return max(0.05, 1.0 - p)

    def analyze(self, candidate: Any) -> Tuple[float, List[str]]:
        """
        Returns:
            (penalty_score, flags)
        """
        flags: List[str] = []
        penalty = 0.0

        profile = _profile(candidate)
        sig = _signals(candidate)
        career = _iter_career(candidate)
        skills = _iter_skills(candidate)

        # -----------------------------
        # 1) Skill stuffing / unnatural skill profiles
        # -----------------------------
        skill_names = []
        expert_count = 0
        duplicate_count = 0
        seen_skill_names = set()
        low_duration_count = 0

        for s in skills:
            name = _norm(_get(s, "name", ""))
            if not name:
                continue
            skill_names.append(name)
            if name in seen_skill_names:
                duplicate_count += 1
            else:
                seen_skill_names.add(name)

            if _norm(_get(s, "proficiency", "")) == "expert":
                expert_count += 1

            dur = _get(s, "duration_months", 0) or 0
            try:
                dur = int(dur)
            except Exception:
                dur = 0
            if dur <= 6:
                low_duration_count += 1

        skill_count = len(skill_names)
        if skill_count > 120:
            penalty += 0.18
            flags.append("excessive_skill_count")
        if expert_count > 40:
            penalty += 0.18
            flags.append("too_many_expert_skills")
        if skill_count >= 20 and duplicate_count / max(1, skill_count) > 0.20:
            penalty += 0.08
            flags.append("duplicate_skill_stuffing")
        if skill_count >= 25 and low_duration_count / max(1, skill_count) > 0.75:
            penalty += 0.06
            flags.append("skills_with_too_little_usage")

        # AI buzzword stuffing with weak career support
        buzz_count = 0
        for name in skill_names:
            for kw in self.ai_buzzwords:
                if kw and kw in name:
                    buzz_count += 1
                    break

        career_text = self._career_text(candidate)
        career_ai_hits = 0
        for kw in self.ai_buzzwords:
            if kw in career_text:
                career_ai_hits += 1

        if buzz_count >= 6 and career_ai_hits <= 1:
            penalty += 0.14
            flags.append("ai_keyword_stuffing")
        elif buzz_count >= 4 and career_ai_hits == 0:
            penalty += 0.10
            flags.append("ai_keywords_without_career_evidence")

        # -----------------------------
        # 2) Experience / timeline anomalies
        # -----------------------------
        years = self._years_of_experience(candidate)
        if years is not None:
            if years < 0:
                penalty += 0.40
                flags.append("negative_experience")
            elif years > 40:
                penalty += 0.25
                flags.append("implausibly_high_experience")

        if self._has_bad_career_dates(career):
            penalty += 0.14
            flags.append("invalid_career_dates")

        if self._severe_timeline_mismatch(candidate):
            penalty += 0.12
            flags.append("timeline_mismatch")

        # -----------------------------
        # 3) Consulting-only / research-only / wrong-title fit
        # -----------------------------
        if career and self._is_consulting_only(career):
            penalty += 0.12
            flags.append("consulting_only_career")

        if self._is_research_only(career):
            penalty += 0.14
            flags.append("research_only_career")

        current_title = _norm(_get(profile, "current_title", ""))
        if current_title in self.low_fit_titles and not self._has_relevant_engineering_evidence(candidate):
            penalty += 0.12
            flags.append("low_fit_title_without_support")

        # Very weak engineering evidence with strong AI keyword presence
        if current_title and any(t in current_title for t in ("manager", "writer", "designer", "support", "sales", "hr", "accountant")):
            if buzz_count >= 4 and not self._has_relevant_engineering_evidence(candidate):
                penalty += 0.10
                flags.append("non_engineering_title_with_ai_keywords")

        # -----------------------------
        # 4) Staleness / availability / recruitability
        # -----------------------------
        last_active_days = _days_since(sig.get("last_active_date"))
        if last_active_days is not None:
            if last_active_days > 365:
                penalty += 0.15
                flags.append("inactive_over_one_year")
            elif last_active_days > 180:
                penalty += 0.10
                flags.append("inactive_over_six_months")
            elif last_active_days > 90:
                penalty += 0.05
                flags.append("inactive_over_three_months")

        open_to_work = bool(sig.get("open_to_work_flag", False))
        response_rate = self._float(sig.get("recruiter_response_rate", 0.0), 0.0)
        response_time = self._float(sig.get("avg_response_time_hours", 0.0), 0.0)
        notice_days = self._int(sig.get("notice_period_days", 999), 999)

        if not open_to_work and (last_active_days is not None and last_active_days > 90):
            penalty += 0.08
            flags.append("not_open_to_work_and_stale")

        if response_rate < 0.15:
            penalty += 0.08
            flags.append("very_low_recruiter_response")
        elif response_rate < 0.30:
            penalty += 0.05
            flags.append("low_recruiter_response")

        if response_time > 72:
            penalty += 0.04
            flags.append("slow_recruiter_response")
        elif response_time > 24:
            penalty += 0.02
            flags.append("moderate_recruiter_response")

        if notice_days > 90:
            penalty += 0.03
            flags.append("long_notice_period")
        elif notice_days > 60:
            penalty += 0.02
            flags.append("medium_notice_period")

        # -----------------------------
        # 5) Profile quality contradictions
        # -----------------------------
        completeness = self._float(sig.get("profile_completeness_score", 0.0), 0.0)
        if completeness < 40:
            penalty += 0.04
            flags.append("very_low_profile_completeness")

        github = self._float(sig.get("github_activity_score", -1.0), -1.0)
        if github == -1:
            # no GitHub isn't a hard penalty
            pass
        elif github < 10:
            penalty += 0.03
            flags.append("weak_github_activity")

        interview_completion = self._float(sig.get("interview_completion_rate", 0.0), 0.0)
        if interview_completion < 0.2:
            penalty += 0.05
            flags.append("very_low_interview_completion")
        elif interview_completion < 0.5:
            penalty += 0.03
            flags.append("low_interview_completion")

        offer_acceptance = self._float(sig.get("offer_acceptance_rate", -1.0), -1.0)
        if 0.0 <= offer_acceptance < 0.15:
            penalty += 0.03
            flags.append("low_offer_acceptance")

        # -----------------------------
        # Clamp and return
        # -----------------------------
        penalty = min(max(penalty, 0.0), 0.95)
        return penalty, flags

    # -----------------------------
    # Helpers
    # -----------------------------
    def _float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except Exception:
            return default

    def _int(self, value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except Exception:
            return default

    def _years_of_experience(self, candidate: Any) -> Optional[float]:
        profile = _profile(candidate)
        y = _get(profile, "years_of_experience", None)
        if y is None:
            return None
        try:
            return float(y)
        except Exception:
            return None

    def _career_text(self, candidate: Any) -> str:
        parts: List[str] = []
        for c in _iter_career(candidate):
            parts.append(_text(_get(c, "title", "")))
            parts.append(_text(_get(c, "company", "")))
            parts.append(_text(_get(c, "industry", "")))
            parts.append(_text(_get(c, "description", "")))
        return _norm(" ".join(parts))

    def _has_relevant_engineering_evidence(self, candidate: Any) -> bool:
        text = self._career_text(candidate)
        # keep this cheap and conservative
        engineering_hits = [
            "engineer",
            "engineering",
            "developer",
            "software",
            "backend",
            "platform",
            "ml",
            "machine learning",
            "ai",
            "data",
            "search",
            "retrieval",
            "recommendation",
            "ranking",
            "production",
            "deployed",
            "serving",
            "inference",
            "pipeline",
            "api",
            "python",
        ]
        return any(k in text for k in engineering_hits)

    def _is_consulting_only(self, career: List[Any]) -> bool:
        if not career:
            return False
        companies = []
        for c in career:
            companies.append(_norm(_get(c, "company", "")))
        companies = [c for c in companies if c]
        if not companies:
            return False

        consulting_hits = sum(
            1 for c in companies if any(cons in c for cons in self.consulting_companies)
        )
        # Consulting-only if almost all roles are at consulting firms
        return consulting_hits >= max(2, math.ceil(0.8 * len(companies)))

    def _is_research_only(self, career: List[Any]) -> bool:
        if not career:
            return False
        text = " ".join(
            [
                _norm(_get(c, "title", "")) + " " +
                _norm(_get(c, "description", "")) + " " +
                _norm(_get(c, "company", ""))
                for c in career
            ]
        )
        research_hits = sum(1 for kw in self.research_keywords if kw in text)
        product_hits = sum(1 for kw in self.product_keywords if kw in text)
        # Research-only if clearly research leaning and little evidence of production/product work
        return research_hits >= 2 and product_hits == 0

    def _has_bad_career_dates(self, career: List[Any]) -> bool:
        # Fast sanity checks: invalid date order or impossible durations
        for c in career:
            start = _safe_date(_get(c, "start_date", None))
            end_raw = _get(c, "end_date", None)
            end = _safe_date(end_raw) if end_raw else None

            if start is None:
                continue

            if end is not None and end < start:
                return True

            duration_months = _get(c, "duration_months", None)
            if duration_months is not None:
                try:
                    dm = int(duration_months)
                except Exception:
                    return True
                if dm < 0 or dm > 480:
                    return True

        return False

    def _severe_timeline_mismatch(self, candidate: Any) -> bool:
        """
        Conservative mismatch check:
        if the claimed years of experience are very low/high relative to total career duration.
        """
        years = self._years_of_experience(candidate)
        if years is None:
            return False

        total_months = 0
        for c in _iter_career(candidate):
            dm = _get(c, "duration_months", 0)
            try:
                total_months += max(0, int(dm))
            except Exception:
                pass

        # total career duration in years
        total_years = total_months / 12.0 if total_months > 0 else 0.0

        # If profile says 1 year but career history spans 8+ years, suspicious.
        if years < 2 and total_years >= 6:
            return True

        # If profile says 15 years but career history has almost nothing, suspicious.
        if years >= 12 and total_years < max(1.5, 0.35 * years):
            return True

        return False