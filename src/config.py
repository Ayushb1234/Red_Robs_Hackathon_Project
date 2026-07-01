from __future__ import annotations

TOP_K = 100
SHORTLIST_SIZE = 1000

HASHING_N_FEATURES = 2**18
HASHING_NGRAM_RANGE = (1, 2)

WEIGHTS = {
    'semantic': 0.30,
    'career': 0.18,
    'skills': 0.18,
    'behavior': 0.14,
    'experience': 0.08,
    'education': 0.05,
    'github': 0.05,
    'title': 0.02,
}

PENALTY_CLAMP = 0.95
DEFAULT_MIN_EXPERIENCE = 5
DEFAULT_MAX_EXPERIENCE = 9

CONSULTING_COMPANIES = {
    'tcs','infosys','wipro','accenture','cognizant','capgemini','deloitte','pwc','ey','kpmg','hcl','tech mahindra',
    'ltimindtree','mindtree','ibm','genpact','hexaware','persistent',
}

LOW_FIT_TITLES = {
    'marketing manager','hr manager','human resources manager','graphic designer','accountant','sales executive',
    'customer support','operations manager','content writer','mechanical engineer','civil engineer','project manager',
}

JD_CONCEPTS = {
    'retrieval': ['retrieval','semantic search','dense retrieval','vector search','faiss','pinecone','qdrant','weaviate','milvus'],
    'ranking': ['ranking','recommendation','recommender','relevance','matching','search'],
    'embeddings': ['embedding','embeddings','sentence transformer','sentence-transformer','bge','e5','openai embedding'],
    'production': ['production','deployed','serving','inference','latency','pipeline','microservice','scalable','shipped','launched'],
    'llm': ['llm','gpt','transformer','bert','t5','llama'],
}

SKILL_ALIASES = {
    'python3': 'python',
    'python programming': 'python',
    'py': 'python',
    'machine learning': 'ml',
    'machine-learning': 'ml',
    'artificial intelligence': 'ai',
    'llms': 'llm',
    'large language model': 'llm',
    'large language models': 'llm',
}

TITLE_ALIASES = {
    'machine learning engineer': 'ml engineer',
    'senior machine learning engineer': 'ml engineer',
    'ai engineer': 'ml engineer',
    'senior ai engineer': 'ml engineer',
    'search engineer': 'retrieval engineer',
    'recommendation engineer': 'retrieval engineer',
    'ranking engineer': 'retrieval engineer',
    'nlu engineer': 'nlp engineer',
}

INDUSTRY_ALIASES = {
    'hr-tech': 'hr tech',
    'human resources': 'hr tech',
    'talent intelligence': 'hr tech',
    'software development': 'software',
    'information technology': 'software',
}
