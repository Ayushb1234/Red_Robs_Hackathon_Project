AI_TOPICS = {

"retrieval":[

"retrieval",

"semantic search",

"dense retrieval",

"vector search",

"faiss",

"pinecone",

"qdrant",

"weaviate",

"milvus"

],

"ranking":[

"ranking",

"recommendation",

"recommender",

"matching",

"relevance",

"search"

],

"embeddings":[

"embedding",

"sentence transformer",

"bge",

"e5",

"openai embedding"

],

"llm":[

"llm",

"gpt",

"transformer",

"bert",

"t5",

"llama"

],

"production":[

"production",

"deployed",

"serving",

"inference",

"latency",

"pipeline",

"microservice"

]

}

import re

class CareerReasoner:

    def analyze(self,candidate):

        score=0

        evidence=[]

        text=[]

        for c in candidate.career_history:

            text.append(c.title)

            text.append(c.description)

        text=" ".join(text).lower()

        for topic,keywords in AI_TOPICS.items():

            found=False

            for kw in keywords:

                if kw in text:

                    found=True

                    evidence.append(topic)

                    break

            if found:

                score+=1

        return {

            "career_score":score,

            "evidence":evidence

        }