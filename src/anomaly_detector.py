class AnomalyDetector:
    
    def penalty(self,candidate):

        penalty=0

        if len(candidate.skills)>120:

            penalty+=0.2

        if candidate.profile["years_of_experience"]>40:

            penalty+=0.4

        expert=sum(

            1

            for s in candidate.skills

            if s.proficiency=="expert"

        )

        if expert>40:

            penalty+=0.3

        return penalty