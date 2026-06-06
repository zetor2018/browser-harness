"""HTML parsing helpers."""
import re
from typing import List


def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s


def match_keywords(text: str, keywords: List[str]) -> List[str]:
    """Return the subset of keywords that appear in text."""
    hits = []
    for kw in keywords:
        if kw and kw in text:
            hits.append(kw)
    return hits
