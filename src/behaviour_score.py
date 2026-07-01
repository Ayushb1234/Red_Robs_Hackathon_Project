from __future__ import annotations

from utils import clamp


class BehaviorScorer:
    def _get_sig(self, candidate):
        sig = getattr(candidate, 'redrob_signals', None)
        if sig is None:
            return {}
        return getattr(sig, 'raw', sig if isinstance(sig, dict) else {}) or {}

    def score(self, candidate):
        sig = self._get_sig(candidate)
        profile_completeness = float(sig.get('profile_completeness_score', 0.0)) / 100.0
        recruiter_response_rate = clamp(float(sig.get('recruiter_response_rate', 0.0)))
        interview_completion_rate = clamp(float(sig.get('interview_completion_rate', 0.0)))
        github_activity = float(sig.get('github_activity_score', -1.0))
        github_score = 0.0 if github_activity < 0 else clamp(github_activity / 100.0)
        open_to_work = 1.0 if bool(sig.get('open_to_work_flag', False)) else 0.0
        verified_email = 1.0 if bool(sig.get('verified_email', False)) else 0.0
        verified_phone = 1.0 if bool(sig.get('verified_phone', False)) else 0.0
        linkedin_connected = 1.0 if bool(sig.get('linkedin_connected', False)) else 0.0
        notice_days = float(sig.get('notice_period_days', 180.0))
        notice_score = clamp(1.0 - (notice_days / 180.0))
        response_time = float(sig.get('avg_response_time_hours', 72.0))
        response_speed_score = clamp(1.0 - (response_time / 72.0))
        saved_by_recruiters = float(sig.get('saved_by_recruiters_30d', 0.0))
        profile_views = float(sig.get('profile_views_received_30d', 0.0))
        search_appearance = float(sig.get('search_appearance_30d', 0.0))
        market_interest_score = 0.45 * clamp(saved_by_recruiters / 10.0) + 0.30 * clamp(profile_views / 50.0) + 0.25 * clamp(search_appearance / 100.0)
        score = (
            0.14 * profile_completeness + 0.18 * recruiter_response_rate + 0.14 * interview_completion_rate +
            0.12 * github_score + 0.10 * open_to_work + 0.08 * verified_email + 0.06 * verified_phone +
            0.05 * linkedin_connected + 0.07 * notice_score + 0.06 * response_speed_score + 0.10 * market_interest_score
        )
        return clamp(score)
