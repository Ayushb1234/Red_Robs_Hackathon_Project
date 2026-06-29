class BehaviorScorer:
    
    def score(self,candidate):

        sig=candidate.redrob_signals.raw

        score=0

        score+=0.15*sig["profile_completeness_score"]/100

        score+=0.20*sig["recruiter_response_rate"]

        score+=0.20*sig["interview_completion_rate"]

        score+=0.15*max(0,sig["github_activity_score"])/100

        score+=0.15*int(sig["open_to_work_flag"])

        score+=0.15*int(sig["verified_email"])

        return score