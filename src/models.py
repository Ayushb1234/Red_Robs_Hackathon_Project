from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Skill:
    name: str
    proficiency: str
    endorsements: int
    duration_months: int = 0


@dataclass
class Education:
    institution: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: int
    tier: str = "unknown"


@dataclass
class CareerHistory:
    company: str
    title: str
    start_date: str
    end_date: Optional[str]
    duration_months: int
    is_current: bool
    industry: str
    company_size: str
    description: str


@dataclass
class RedrobSignals:
    profile_completeness_score: float
    recruiter_response_rate: float
    github_activity_score: float
    interview_completion_rate: float
    open_to_work_flag: bool
    last_active_date: str
    raw: Dict = field(default_factory=dict)


@dataclass
class Candidate:

    candidate_id: str

    profile: Dict

    career_history: List[CareerHistory]

    education: List[Education]

    skills: List[Skill]

    certifications: List[Dict]

    languages: List[Dict]

    redrob_signals: RedrobSignals