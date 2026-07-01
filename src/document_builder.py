class CandidateDocumentBuilder:
    def _safe_get(self, obj, key, default=""):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def build(self, candidate):
        parts = []

        profile = self._safe_get(candidate, "profile", {}) or {}

        # Core profile
        parts.append(str(profile.get("headline", "")))
        parts.append(str(profile.get("summary", "")))
        parts.append(str(profile.get("current_title", "")))
        parts.append(str(profile.get("current_industry", "")))
        parts.append(str(profile.get("location", "")))
        parts.append(str(profile.get("country", "")))

        # Career history
        for c in self._safe_get(candidate, "career_history", []) or []:
            parts.append(str(self._safe_get(c, "title", "")))
            parts.append(str(self._safe_get(c, "company", "")))
            parts.append(str(self._safe_get(c, "industry", "")))
            parts.append(str(self._safe_get(c, "description", "")))

        # Skills with proficiency and duration
        for s in self._safe_get(candidate, "skills", []) or []:
            parts.append(str(self._safe_get(s, "name", "")))
            parts.append(str(self._safe_get(s, "proficiency", "")))
            parts.append(str(self._safe_get(s, "duration_months", "")))

        # Education
        for e in self._safe_get(candidate, "education", []) or []:
            parts.append(str(self._safe_get(e, "degree", "")))
            parts.append(str(self._safe_get(e, "field_of_study", "")))
            parts.append(str(self._safe_get(e, "institution", "")))
            parts.append(str(self._safe_get(e, "tier", "")))

        # Certifications
        for cert in self._safe_get(candidate, "certifications", []) or []:
            parts.append(str(self._safe_get(cert, "name", "")))
            parts.append(str(self._safe_get(cert, "issuer", "")))

        # Languages
        for lang in self._safe_get(candidate, "languages", []) or []:
            parts.append(str(self._safe_get(lang, "language", "")))
            parts.append(str(self._safe_get(lang, "proficiency", "")))

        # Behavioral signals that help the embedding carry hiring context
        sig = self._safe_get(candidate, "redrob_signals", {}) or {}
        raw = self._safe_get(sig, "raw", sig if isinstance(sig, dict) else {}) or {}

        parts.append(str(raw.get("open_to_work_flag", "")))
        parts.append(str(raw.get("recruiter_response_rate", "")))
        parts.append(str(raw.get("avg_response_time_hours", "")))
        parts.append(str(raw.get("profile_completeness_score", "")))
        parts.append(str(raw.get("github_activity_score", "")))

        # Clean and join
        clean_parts = [p.strip() for p in parts if str(p).strip()]
        return "\n".join(clean_parts)