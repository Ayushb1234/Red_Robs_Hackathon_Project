from dataclasses import dataclass

@dataclass
class CandidateFeatures:

    candidate_id:str

    years_experience:float

    skill_count:int

    expert_skill_count:int

    avg_endorsements:float

    avg_skill_duration:float

    github_score:float

    recruiter_response:float

    interview_completion:float

    profile_score:float

    education_score:float

    title:str

    industry:str
    
from statistics import mean

class FeatureExtractor:

    def build(self,candidate):

        expert = 0

        endorsements=[]

        duration=[]

        for s in candidate.skills:

            if s.proficiency=="expert":
                expert+=1

            endorsements.append(s.endorsements)

            duration.append(s.duration_months)

        education=self.education_score(candidate)

        sig=candidate.redrob_signals

        return CandidateFeatures(

            candidate_id=candidate.candidate_id,

            years_experience=candidate.profile["years_of_experience"],

            skill_count=len(candidate.skills),

            expert_skill_count=expert,

            avg_endorsements=mean(endorsements) if endorsements else 0,

            avg_skill_duration=mean(duration) if duration else 0,

            github_score=sig.github_activity_score,

            recruiter_response=sig.recruiter_response_rate,

            interview_completion=sig.interview_completion_rate,

            profile_score=sig.profile_completeness_score,

            education_score=education,

            title=candidate.profile["current_title"],

            industry=candidate.profile["current_industry"]

        )