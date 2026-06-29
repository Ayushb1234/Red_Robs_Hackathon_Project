import gzip
import json

from src.models import *


class CandidateLoader:

    def __init__(self, filename):

        self.filename = filename

    def load(self):

        with gzip.open(self.filename, "rt", encoding="utf8") as f:

            for line in f:

                if not line.strip():
                    continue

                yield self.parse(json.loads(line))

    def parse(self, obj):

        skills = [

            Skill(

                s["name"],

                s["proficiency"],

                s["endorsements"],

                s.get("duration_months", 0),

            )

            for s in obj["skills"]

        ]

        education = [

            Education(

                e["institution"],

                e["degree"],

                e["field_of_study"],

                e["start_year"],

                e["end_year"],

                e.get("tier", "unknown"),

            )

            for e in obj["education"]

        ]

        career = [

            CareerHistory(

                c["company"],

                c["title"],

                c["start_date"],

                c["end_date"],

                c["duration_months"],

                c["is_current"],

                c["industry"],

                c["company_size"],

                c["description"],

            )

            for c in obj["career_history"]

        ]

        sig = obj["redrob_signals"]

        signals = RedrobSignals(

            profile_completeness_score=sig["profile_completeness_score"],

            recruiter_response_rate=sig["recruiter_response_rate"],

            github_activity_score=sig["github_activity_score"],

            interview_completion_rate=sig["interview_completion_rate"],

            open_to_work_flag=sig["open_to_work_flag"],

            last_active_date=sig["last_active_date"],

            raw=sig,

        )

        return Candidate(

            candidate_id=obj["candidate_id"],

            profile=obj["profile"],

            career_history=career,

            education=education,

            skills=skills,

            certifications=obj.get("certifications", []),

            languages=obj.get("languages", []),

            redrob_signals=signals,

        )