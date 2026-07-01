from __future__ import annotations


class CandidateDocumentBuilder:
    def _safe_get(self, obj, key, default=''):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def build(self, candidate):
        parts = []
        profile = self._safe_get(candidate, 'profile', {}) or {}

        parts.extend([
            str(profile.get('headline', '')),
            str(profile.get('summary', '')),
            str(profile.get('current_title', '')),
            str(profile.get('current_industry', '')),
            str(profile.get('location', '')),
            str(profile.get('country', '')),
        ])

        for c in self._safe_get(candidate, 'career_history', []) or []:
            parts.extend([
                str(self._safe_get(c, 'title', '')),
                str(self._safe_get(c, 'company', '')),
                str(self._safe_get(c, 'industry', '')),
                str(self._safe_get(c, 'description', '')),
            ])

        for s in self._safe_get(candidate, 'skills', []) or []:
            parts.extend([
                str(self._safe_get(s, 'name', '')),
                str(self._safe_get(s, 'proficiency', '')),
                str(self._safe_get(s, 'duration_months', '')),
            ])

        for e in self._safe_get(candidate, 'education', []) or []:
            parts.extend([
                str(self._safe_get(e, 'degree', '')),
                str(self._safe_get(e, 'field_of_study', '')),
                str(self._safe_get(e, 'institution', '')),
                str(self._safe_get(e, 'tier', '')),
            ])

        for cert in self._safe_get(candidate, 'certifications', []) or []:
            parts.extend([str(self._safe_get(cert, 'name', '')), str(self._safe_get(cert, 'issuer', ''))])

        for lang in self._safe_get(candidate, 'languages', []) or []:
            parts.extend([str(self._safe_get(lang, 'language', '')), str(self._safe_get(lang, 'proficiency', ''))])

        sig = self._safe_get(candidate, 'redrob_signals', {}) or {}
        raw = self._safe_get(sig, 'raw', sig if isinstance(sig, dict) else {}) or {}
        parts.extend([
            str(raw.get('open_to_work_flag', '')),
            str(raw.get('recruiter_response_rate', '')),
            str(raw.get('avg_response_time_hours', '')),
            str(raw.get('profile_completeness_score', '')),
            str(raw.get('github_activity_score', '')),
        ])

        return '\n'.join(p.strip() for p in parts if str(p).strip())
