from __future__ import annotations

from typing import Any, List

from config import DEFAULT_MAX_EXPERIENCE, DEFAULT_MIN_EXPERIENCE
from normalizer import normalize_skill
from utils import clamp, safe_get, safe_int, safe_float


PROFICIENCY_WEIGHT = {
    'expert': 1.0,
    'advanced': 0.85,
    'intermediate': 0.65,
    'beginner': 0.40,
}


class SkillMatcher:
    def score(self, candidate: Any, jd: Any) -> tuple[float, List[str]]:
        required = [normalize_skill(x) for x in (safe_get(jd, 'required_skills', []) or [])]
        preferred = [normalize_skill(x) for x in (safe_get(jd, 'preferred_skills', []) or [])]
        skills = {}
        evidence: List[str] = []
        for s in safe_get(candidate, 'skills', []) or []:
            name = normalize_skill(safe_get(s, 'name', ''))
            if name:
                skills[name] = s
        if not required and not preferred:
            return 0.0, evidence

        req_matches = 0.0
        for skill in required:
            if skill in skills:
                s = skills[skill]
                prof_w = PROFICIENCY_WEIGHT.get(str(safe_get(s, 'proficiency', 'beginner')).lower(), 0.35)
                duration = safe_int(safe_get(s, 'duration_months', 0), 0)
                endorsements = safe_int(safe_get(s, 'endorsements', 0), 0)
                req_matches += 0.55 * prof_w + 0.25 * clamp(duration / 24.0) + 0.20 * clamp(endorsements / 50.0)
                evidence.append(skill)
        pref_matches = 0.0
        for skill in preferred:
            if skill in skills:
                s = skills[skill]
                prof_w = PROFICIENCY_WEIGHT.get(str(safe_get(s, 'proficiency', 'beginner')).lower(), 0.35)
                duration = safe_int(safe_get(s, 'duration_months', 0), 0)
                endorsements = safe_int(safe_get(s, 'endorsements', 0), 0)
                pref_matches += 0.55 * prof_w + 0.25 * clamp(duration / 24.0) + 0.20 * clamp(endorsements / 50.0)
                evidence.append(skill)

        required_score = req_matches / max(1, len(required))
        preferred_score = pref_matches / max(1, len(preferred)) if preferred else 0.0
        return clamp(0.75 * required_score + 0.25 * preferred_score), list(dict.fromkeys(evidence))

    def experience_score(self, candidate: Any, jd: Any) -> float:
        years = safe_float(safe_get(candidate, 'profile', {}).get('years_of_experience', 0), 0.0)
        lo = safe_int(safe_get(jd, 'experience_min', DEFAULT_MIN_EXPERIENCE), DEFAULT_MIN_EXPERIENCE)
        hi = safe_int(safe_get(jd, 'experience_max', DEFAULT_MAX_EXPERIENCE), DEFAULT_MAX_EXPERIENCE)
        if years < lo:
            return clamp(years / float(lo))
        if years <= hi:
            return 1.0
        if years <= hi + 3:
            return 0.92
        return 0.80
