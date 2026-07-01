from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Iterable, List, Optional, Sequence


def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def safe_text(value: Any) -> str:
    return '' if value is None else str(value)


def normalize_spaces(text: Any) -> str:
    return re.sub(r'\s+', ' ', safe_text(text).strip())


def normalize_lower(text: Any) -> str:
    return normalize_spaces(text).lower()


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return default if value is None else float(value)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return default if value is None else int(value)
    except Exception:
        return default


def parse_date(value: Any) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(str(value), '%Y-%m-%d').date()
    except Exception:
        return None


def days_since(value: Any) -> Optional[int]:
    d = parse_date(value)
    return None if d is None else (date.today() - d).days


def dedupe_keep_order(items: Iterable[str]) -> List[str]:
    seen, out = set(), []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def token_set(text: Any) -> set[str]:
    return set(re.findall(r"[a-z0-9\+\#]+", normalize_lower(text)))


def mean(values: Sequence[float], default: float = 0.0) -> float:
    return default if not values else sum(values) / len(values)


def ensure_float01(x: Any) -> float:
    return clamp(safe_float(x, 0.0), 0.0, 1.0)
