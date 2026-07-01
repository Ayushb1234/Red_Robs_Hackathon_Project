from __future__ import annotations

import re
from typing import List

from models import JobDescription
from normalizer import normalize_text
from utils import dedupe_keep_order


class JDParser:
    def parse(self, text: str) -> JobDescription:
        raw = text or ''
        lines = [line.strip() for line in raw.splitlines() if line.strip()]

        return JobDescription(
            role=self._extract_role(lines, raw),
            company=self._extract_company(lines),
            location=self._extract_location(raw),
            employment_type=self._extract_employment_type(raw),
            experience_min=self._extract_experience(raw)[0],
            experience_max=self._extract_experience(raw)[1],
            required_skills=self._extract_skills(raw, must_have=True),
            preferred_skills=self._extract_skills(raw, must_have=False),
            preferred_titles=self._extract_titles(raw),
            preferred_industries=self._extract_industries(raw),
            disqualifiers=self._extract_disqualifiers(raw),
            notes=raw.strip(),
        )

    def _extract_role(self, lines: List[str], raw: str) -> str:
        for line in lines[:8]:
            low = line.lower()
            if 'role:' in low:
                return line.split(':', 1)[1].strip()
            if 'job title:' in low:
                return line.split(':', 1)[1].strip()
        m = re.search(r'(?i)(Senior AI Engineer[^|\n]*)', raw)
        return m.group(1).strip() if m else ''

    def _extract_company(self, lines: List[str]) -> str:
        for line in lines[:12]:
            if 'company:' in line.lower():
                return line.split(':', 1)[1].strip()
        return ''

    def _extract_location(self, raw: str) -> str:
        m = re.search(r'(?i)location:\s*([^\n|]+)', raw)
        return m.group(1).strip() if m else ''

    def _extract_employment_type(self, raw: str) -> str:
        m = re.search(r'(?i)employment type:\s*([^\n|]+)', raw)
        return m.group(1).strip() if m else ''

    def _extract_experience(self, raw: str) -> tuple[int, int]:
        m = re.search(r'(?i)(\d+)\s*[-–to]+\s*(\d+)\s*years', raw)
        if m:
            return int(m.group(1)), int(m.group(2))
        m = re.search(r'(?i)(\d+)\s*\+\s*years', raw)
        if m:
            lo = int(m.group(1))
            return lo, lo + 4
        return 5, 9

    def _extract_skills(self, raw: str, must_have: bool) -> List[str]:
        text = normalize_text(raw)
        skill_vocab = [
            'python','embeddings','embedding','retrieval','ranking','search','recommendation','semantic search','vector search',
            'vector database','faiss','pinecone','qdrant','weaviate','milvus','opensearch','elasticsearch','llm','fine tuning',
            'fine-tuning','lora','qlora','peft','xgboost','tensorflow','pytorch','bert','transformers','sentence transformers',
            'sentence-transformers','bge','e5','nlp','ir','information retrieval','evaluation','ndcg','mrr','map','ab testing',
            'a/b testing','feature store',
        ]
        found = [skill for skill in skill_vocab if skill in text]
        if must_have:
            for skill in ('python','embeddings','retrieval','ranking','evaluation'):
                if skill in text and skill not in found:
                    found.append(skill)
        else:
            for skill in ('lora','qlora','peft','xgboost','open-source'):
                if skill in text and skill not in found:
                    found.append(skill)
        return dedupe_keep_order(found)

    def _extract_titles(self, raw: str) -> List[str]:
        text = normalize_text(raw)
        titles = []
        for p in [
            r'ml engineer', r'machine learning engineer', r'ai engineer', r'search engineer',
            r'recommendation engineer', r'ranking engineer', r'nlp engineer', r'retrieval engineer', r'data scientist',
        ]:
            if re.search(p, text):
                titles.append(p)
        return dedupe_keep_order(titles)

    def _extract_industries(self, raw: str) -> List[str]:
        text = normalize_text(raw)
        industries = [ind for ind in ['product','hr tech','marketplace','saas','software','ai','talent intelligence'] if ind in text]
        return dedupe_keep_order(industries)

    def _extract_disqualifiers(self, raw: str) -> List[str]:
        text = normalize_text(raw)
        disqualifiers = []
        for phrase in ['research only','consulting only','framework enthusiasts','title-chasers','pure research','no production deployment','langchain to call openai']:
            if phrase in text:
                disqualifiers.append(phrase)
        return dedupe_keep_order(disqualifiers)
