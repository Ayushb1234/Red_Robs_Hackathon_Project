from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Generator, List, Union

from models import Candidate, CareerHistory, Education, RedrobSignals, Skill
from utils import safe_float, safe_int, safe_text


def _open_text(path: Union[str, Path]):
    p = Path(path)
    return gzip.open(p, 'rt', encoding='utf-8') if p.suffix.lower() == '.gz' else open(p, 'rt', encoding='utf-8')


class CandidateLoader:
    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)

    def iter_candidates(self) -> Generator[Candidate, None, None]:
        with _open_text(self.path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield self.parse_candidate(json.loads(line))

    def load_all(self) -> List[Candidate]:
        return list(self.iter_candidates())

    def parse_candidate(self, obj: dict) -> Candidate:
        profile = obj.get('profile', {}) or {}

        skills = [
            Skill(
                name=safe_text(s.get('name', '')),
                proficiency=safe_text(s.get('proficiency', 'beginner')),
                endorsements=safe_int(s.get('endorsements', 0), 0),
                duration_months=safe_int(s.get('duration_months', 0), 0),
            )
            for s in (obj.get('skills', []) or [])
        ]

        education = [
            Education(
                institution=safe_text(e.get('institution', '')),
                degree=safe_text(e.get('degree', '')),
                field_of_study=safe_text(e.get('field_of_study', '')),
                start_year=safe_int(e.get('start_year', 0), 0),
                end_year=safe_int(e.get('end_year', 0), 0),
                grade=e.get('grade', None),
                tier=safe_text(e.get('tier', 'unknown')),
            )
            for e in (obj.get('education', []) or [])
        ]

        career_history = [
            CareerHistory(
                company=safe_text(c.get('company', '')),
                title=safe_text(c.get('title', '')),
                start_date=safe_text(c.get('start_date', '')),
                end_date=c.get('end_date', None),
                duration_months=safe_int(c.get('duration_months', 0), 0),
                is_current=bool(c.get('is_current', False)),
                industry=safe_text(c.get('industry', '')),
                company_size=safe_text(c.get('company_size', 'unknown')),
                description=safe_text(c.get('description', '')),
            )
            for c in (obj.get('career_history', []) or [])
        ]

        sig = obj.get('redrob_signals', {}) or {}
        signals = RedrobSignals(
            profile_completeness_score=safe_float(sig.get('profile_completeness_score', 0.0), 0.0),
            signup_date=safe_text(sig.get('signup_date', '')),
            last_active_date=safe_text(sig.get('last_active_date', '')),
            open_to_work_flag=bool(sig.get('open_to_work_flag', False)),
            profile_views_received_30d=safe_int(sig.get('profile_views_received_30d', 0), 0),
            applications_submitted_30d=safe_int(sig.get('applications_submitted_30d', 0), 0),
            recruiter_response_rate=safe_float(sig.get('recruiter_response_rate', 0.0), 0.0),
            avg_response_time_hours=safe_float(sig.get('avg_response_time_hours', 0.0), 0.0),
            skill_assessment_scores=dict(sig.get('skill_assessment_scores', {}) or {}),
            connection_count=safe_int(sig.get('connection_count', 0), 0),
            endorsements_received=safe_int(sig.get('endorsements_received', 0), 0),
            notice_period_days=safe_int(sig.get('notice_period_days', 180), 180),
            expected_salary_range_inr_lpa=dict(sig.get('expected_salary_range_inr_lpa', {}) or {}),
            preferred_work_mode=safe_text(sig.get('preferred_work_mode', 'flexible')),
            willing_to_relocate=bool(sig.get('willing_to_relocate', False)),
            github_activity_score=safe_float(sig.get('github_activity_score', -1.0), -1.0),
            search_appearance_30d=safe_int(sig.get('search_appearance_30d', 0), 0),
            saved_by_recruiters_30d=safe_int(sig.get('saved_by_recruiters_30d', 0), 0),
            interview_completion_rate=safe_float(sig.get('interview_completion_rate', 0.0), 0.0),
            offer_acceptance_rate=safe_float(sig.get('offer_acceptance_rate', -1.0), -1.0),
            verified_email=bool(sig.get('verified_email', False)),
            verified_phone=bool(sig.get('verified_phone', False)),
            linkedin_connected=bool(sig.get('linkedin_connected', False)),
            raw=sig,
        )

        return Candidate(
            candidate_id=safe_text(obj.get('candidate_id', '')),
            profile=profile,
            career_history=career_history,
            education=education,
            skills=skills,
            certifications=list(obj.get('certifications', []) or []),
            languages=list(obj.get('languages', []) or []),
            redrob_signals=signals,
        )
