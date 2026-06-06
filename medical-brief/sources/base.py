"""Source base class. Each source fetches a list page and parses it into Items."""
from __future__ import annotations
import gzip, time
import urllib.request
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from bs4 import BeautifulSoup

from config import UA, HTTP_TIMEOUT, FETCH_DELAY


@dataclass
class Item:
    id: str            # URL hash
    title: str
    url: str
    source_id: str
    source_label: str
    category: str
    publish_date: str  # YYYY-MM-DD or ""
    summary: str       # short snippet
    matched_kw: List[str] = field(default_factory=list)
    fetched_at: str = ""

    def to_dict(self):
        return asdict(self)


class Source:
    """Base class for all data sources."""
    id: str = ""
    label: str = ""
    category: str = "policy"
    url: str = ""
    max_items: int = 20
    filter_kw: bool = False

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._last_fetch = 0.0

    # ---- HTTP ----
    def fetch(self, url: str = None) -> str:
        """Fetch a URL with the configured UA. Throttled."""
        url = url or self.url
        elapsed = time.time() - self._last_fetch
        if elapsed < FETCH_DELAY:
            time.sleep(FETCH_DELAY - elapsed)
        h = {
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip",
            "Referer": url,
        }
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            data = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                data = gzip.decompress(data)
            self._last_fetch = time.time()
            return data.decode("utf-8", errors="ignore")

    # ---- Override in subclass ----
    def parse(self, html: str) -> List[Item]:
        raise NotImplementedError

    # ---- Convenience ----
    def run(self) -> List[Item]:
        html = self.fetch()
        items = self.parse(html)
        # mark fetched_at
        now = datetime.now().isoformat(timespec="seconds")
        for it in items:
            it.source_id = self.id
            it.source_label = self.label
            it.category = self.category
            it.fetched_at = now
        # truncate
        return items[: self.max_items]
