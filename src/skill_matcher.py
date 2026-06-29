class SkillMatcher:
    
    def score(self,candidate,jd):

        total=0

        matched=0

        evidence=[]

        jdskills=set(jd.required_skills)

        skills={

            s.name.lower():s

            for s in candidate.skills

        }

        for skill in jdskills:

            total+=1

            if skill in skills:

                matched+=1

                evidence.append(skill)

        if total==0:

            return 0,evidence

        return matched/total,evidence