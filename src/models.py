from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Skill:
    name: str
    proficiency: str = 'beginner'
    endorsements: int = 0
    duration_months: int = 0


@dataclass
class Education:
    institution: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: int
    grade: Optional[str] = None
    tier: str = 'unknown'


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
    profile_completeness_score: float = 0.0
    signup_date: str = ''
    last_active_date: str = ''
    open_to_work_flag: bool = False
    profile_views_received_30d: int = 0
    applications_submitted_30d: int = 0
    recruiter_response_rate: float = 0.0
    avg_response_time_hours: float = 0.0
    skill_assessment_scores: Dict[str, float] = field(default_factory=dict)
    connection_count: int = 0
    endorsements_received: int = 0
    notice_period_days: int = 180
    expected_salary_range_inr_lpa: Dict[str, float] = field(default_factory=dict)
    preferred_work_mode: str = 'flexible'
    willing_to_relocate: bool = False
    github_activity_score: float = -1.0
    search_appearance_30d: int = 0
    saved_by_recruiters_30d: int = 0
    interview_completion_rate: float = 0.0
    offer_acceptance_rate: float = -1.0
    verified_email: bool = False
    verified_phone: bool = False
    linkedin_connected: bool = False
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Candidate:
    candidate_id: str
    profile: Dict[str, Any]
    career_history: List[CareerHistory]
    education: List[Education]
    skills: List[Skill]
    certifications: List[Dict[str, Any]]
    languages: List[Dict[str, Any]]
    redrob_signals: RedrobSignals


@dataclass
class JobDescription:
    role: str = ''
    company: str = ''
    location: str = ''
    employment_type: str = ''
    experience_min: int = 0
    experience_max: int = 50
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    preferred_titles: List[str] = field(default_factory=list)
    preferred_industries: List[str] = field(default_factory=list)
    disqualifiers: List[str] = field(default_factory=list)
    notes: str = ''


@dataclass
class CandidateFeatures:
    candidate_id: str
    years_experience: float = 0.0
    skill_count: int = 0
    expert_skill_count: int = 0
    avg_endorsements: float = 0.0
    avg_skill_duration: float = 0.0
    github_score: float = 0.0
    recruiter_response: float = 0.0
    interview_completion: float = 0.0
    profile_score: float = 0.0
    education_score: float = 0.0
    open_to_work: float = 0.0
    notice_period_days: int = 180
    title: str = ''
    industry: str = ''
    current_company: str = ''
    current_company_size: str = ''
    current_industry: str = ''
    location: str = ''


@dataclass
class RankResult:
    candidate_id: str
    score: float
    rank: int = 0
    semantic_score: float = 0.0
    career_score: float = 0.0
    skill_score: float = 0.0
    behavior_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    title_score: float = 0.0
    github_score: float = 0.0
    penalty_multiplier: float = 1.0
    penalty_flags: List[str] = field(default_factory=list)
    career_evidence: List[str] = field(default_factory=list)
    skill_evidence: List[str] = field(default_factory=list)
    behavior_evidence: List[str] = field(default_factory=list)
