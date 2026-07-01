from __future__ import annotations

import re
from typing import Any

from config import INDUSTRY_ALIASES, SKILL_ALIASES, TITLE_ALIASES


def normalize_text(value: Any) -> str:
    text = '' if value is None else str(value)
    text = text.strip().lower()
    text = re.sub(r'[\u2010-\u2015\-_/]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def normalize_skill(name: Any) -> str:
    text = normalize_text(name)
    return SKILL_ALIASES.get(text, text)


def normalize_title(title: Any) -> str:
    text = normalize_text(title)
    return TITLE_ALIASES.get(text, text)


def normalize_company(company: Any) -> str:
    return normalize_text(company)


def normalize_industry(industry: Any) -> str:
    text = normalize_text(industry)
    return INDUSTRY_ALIASES.get(text, text)


def normalize_degree(degree: Any) -> str:
    return normalize_text(degree)


def normalize_company_size(value: Any) -> str:
    return normalize_text(value)
