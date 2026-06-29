class CandidateDocumentBuilder:
    
    def build(self,candidate):

        parts=[]

        profile=candidate.profile

        parts.append(profile["headline"])

        parts.append(profile["summary"])

        parts.append(profile["current_title"])

        parts.append(profile["current_industry"])

        for c in candidate.career_history:

            parts.append(c.title)

            parts.append(c.company)

            parts.append(c.description)

        for s in candidate.skills:

            parts.append(s.name)

        for e in candidate.education:

            parts.append(e.degree)

            parts.append(e.field_of_study)

        for cert in candidate.certifications:

            parts.append(cert["name"])

        return "\n".join(parts)