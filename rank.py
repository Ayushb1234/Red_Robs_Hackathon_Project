from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from loader import CandidateLoader
from ranker import HybridRanker
from reasoning import ExplanationGenerator
from submission import SubmissionWriter


def main():
    parser = argparse.ArgumentParser(description='Redrob Hackathon ranker')
    parser.add_argument('--candidates', required=True, help='Path to candidates.jsonl or candidates.jsonl.gz')
    parser.add_argument('--job-description', required=True, help='Path to job_description.md')
    parser.add_argument('--out', required=True, help='Output CSV path')
    args = parser.parse_args()

    loader = CandidateLoader(args.candidates)
    candidates = loader.load_all()
    candidate_by_id = {c.candidate_id: c for c in candidates}

    jd_text = Path(args.job_description).read_text(encoding='utf-8')
    ranker = HybridRanker()
    explainer = ExplanationGenerator()
    writer = SubmissionWriter()

    results = ranker.rank(candidates, jd_text, top_k=100)
    reason_map = {r.candidate_id: explainer.build(candidate_by_id[r.candidate_id], r.__dict__) for r in results}
    rows = writer.from_rank_results(results, reason_map)
    writer.write(rows, args.out)
    print(f'Wrote {len(rows)} rows to {args.out}')


if __name__ == '__main__':
    main()
