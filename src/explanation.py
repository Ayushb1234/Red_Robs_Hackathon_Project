class ExplanationGenerator:
    
    def build(

        self,

        candidate,

        result

    ):

        return (

f"{candidate.profile['current_title']} "

f"with "

f"{candidate.profile['years_of_experience']} years "

f"experience. "

f"Strong evidence of "

f"{', '.join(result['career'])}. "

f"Recruiter response "

f"{candidate.redrob_signals.recruiter_response_rate:.2f}."

        )