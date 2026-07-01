from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from models import RankResult

REQUIRED_HEADER = ['candidate_id', 'rank', 'score', 'reasoning']


class SubmissionWriter:
    def write(self, rows: List[dict], out_path: str | Path) -> None:
        out_path = Path(out_path)
        with out_path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(REQUIRED_HEADER)
            for row in rows:
                writer.writerow([row['candidate_id'], int(row['rank']), f"{float(row['score']):.6f}", row['reasoning']])

    def from_rank_results(self, results: List[RankResult], reason_map: dict[str, str]) -> List[dict]:
        rows = []
        prev = 1.0
        for i, r in enumerate(results[:100], start=1):
            score = round(float(r.score), 6)
            if score > prev:
                score = prev
            prev = score
            rows.append({'candidate_id': r.candidate_id, 'rank': i, 'score': score, 'reasoning': reason_map.get(r.candidate_id, '')})
        return rows
