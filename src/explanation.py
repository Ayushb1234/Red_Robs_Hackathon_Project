# explanation.py
from __future__ import annotations

from typing import Any, Dict, List


class ExplanationGenerator:
    """
    Builds short, truthful 1–2 sentence reasoning strings for ranked candidates.

    The explanation should only reference facts that exist in the candidate object
    or the computed result dictionary.
    """

    def _get(self, obj: Any, key: str, default: Any = "") -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def _get_signals(self, candidate: Any) -> Dict[str, Any]:
        sig = self._get(candidate, "redrob_signals", {})
        if isinstance(sig, dict):
            return sig
        raw = self._get(sig, "raw", {})
        return raw if isinstance(raw, dict) else {}

    def _fmt_float(self, value: Any, ndigits: int = 2, default: str = "0.00") -> str:
        try:
            return f"{float(value):.{ndigits}f}"
        except Exception:
            return default

    def _top_evidence(self, result: Dict[str, Any]) -> List[str]:
        """
        Collect evidence from the ranker result if available.
        Expected keys (any subset):
          - career_evidence
          - skill_evidence
          - behavior_evidence
          - penalty_flags
        """
        evidence: List[str] = []

        for key in ("career_evidence", "skill_evidence", "behavior_evidence", "penalty_flags"):
            items = result.get(key, [])
            if isinstance(items, list):
                for item in items:
                    s = str(item).strip()
                    if s:
                        evidence.append(s)

        # de-duplicate while preserving order
        seen = set()
        out = []
        for e in evidence:
            if e not in seen:
                seen.add(e)
                out.append(e)
        return out

    def build(self, candidate: Any, result: Dict[str, Any]) -> str:
        profile = self._get(candidate, "profile", {}) or {}
        signals = self._get_signals(candidate)

        title = str(profile.get("current_title", "")).strip() or "Candidate"
        years = profile.get("years_of_experience", None)

        # Core candidate facts
        parts: List[str] = []

        if years is not None:
            try:
                years_str = f"{float(years):.1f}"
            except Exception:
                years_str = str(years)
            parts.append(f"{title} with {years_str} years of experience")
        else:
            parts.append(f"{title}")

        # Use specific evidence only if the ranker gave it to us
        evidence = self._top_evidence(result)
        if evidence:
            # Keep it short and readable
            joined = ", ".join(evidence[:3])
            parts.append(f"with evidence of {joined}")

        # Add a grounded behavioral signal if present
        response_rate = signals.get("recruiter_response_rate", None)
        if response_rate is not None:
            parts.append(f"recruiter response rate {self._fmt_float(response_rate)}")

        # Optional JD-aligned facts if present in result
        semantic = result.get("semantic_score", None)
        if semantic is not None:
            parts.append(f"semantic match {self._fmt_float(semantic)}")

        # Soft caution if the ranker flagged penalties
        penalty_flags = result.get("penalty_flags", [])
        if isinstance(penalty_flags, list) and penalty_flags:
            flags = ", ".join(str(x) for x in penalty_flags[:2] if str(x).strip())
            if flags:
                parts.append(f"with caution around {flags}")

        # Make one clean sentence
        sentence = ". ".join(parts).strip()
        if not sentence.endswith("."):
            sentence += "."

        # Ensure this stays within the 1–2 sentence rule
        return sentence