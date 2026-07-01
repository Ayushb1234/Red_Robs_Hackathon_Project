from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ScoreSummary:
    candidate_id: str
    score: float
    semantic: float = 0.0
    career: float = 0.0
    skills: float = 0.0
    behavior: float = 0.0
    experience: float = 0.0
    education: float = 0.0
    penalty: float = 0.0


class Evaluator:
    def __init__(self, top_k: int = 100):
        self.top_k = top_k

    def validate_rank_output(self, rows: List[Dict[str, Any]]) -> List[str]:
        errors: List[str] = []
        if len(rows) != self.top_k:
            errors.append(f'Expected exactly {self.top_k} rows, got {len(rows)}.')
        seen_ids, seen_ranks = set(), set()
        prev_score = None
        for i, row in enumerate(rows, start=1):
            cid = str(row.get('candidate_id', '')).strip()
            rank = row.get('rank', None)
            score = row.get('score', None)
            if not cid:
                errors.append(f'Row {i}: missing candidate_id.')
            elif cid in seen_ids:
                errors.append(f'Row {i}: duplicate candidate_id {cid}.')
            else:
                seen_ids.add(cid)
            if not isinstance(rank, int):
                errors.append(f'Row {i}: rank must be int.')
            else:
                if rank < 1 or rank > self.top_k:
                    errors.append(f'Row {i}: rank must be in 1..{self.top_k}.')
                if rank in seen_ranks:
                    errors.append(f'Row {i}: duplicate rank {rank}.')
                seen_ranks.add(rank)
            if not isinstance(score, (int, float)):
                errors.append(f'Row {i}: score must be numeric.')
            else:
                score = float(score)
                if prev_score is not None and score > prev_score + 1e-12:
                    errors.append(f'Row {i}: scores must be non-increasing; {score} is greater than previous {prev_score}.')
                prev_score = score
        missing = [r for r in range(1, self.top_k + 1) if r not in seen_ranks]
        if missing:
            errors.append(f'Missing ranks: {missing}')
        return errors

    def summarize_scores(self, rows: List[Dict[str, Any]]) -> Dict[str, float]:
        if not rows:
            return {'count': 0, 'max_score': 0.0, 'min_score': 0.0, 'mean_score': 0.0}
        scores = [float(r['score']) for r in rows if 'score' in r]
        return {'count': float(len(scores)), 'max_score': float(max(scores)), 'min_score': float(min(scores)), 'mean_score': float(sum(scores) / len(scores))}

    def inspect_top_rows(self, rows: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
        return rows[:n]
