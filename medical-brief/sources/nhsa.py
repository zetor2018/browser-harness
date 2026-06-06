"""国家医保局 — 医保动态列表页.

List URL: http://www.nhsa.gov.cn/col/col14/index.html
Item URL pattern: /art/YYYY/M/D/art_N_ID.html (publish date encoded in path)
The list is rendered inside <record>...</record> CDATA-ish blocks which confuse
lxml; we use a regex extractor on the raw HTML and BS4 as a fallback.
"""
from __future__ import annotations
import re
import hashlib
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import Source, Item


class NhsaSource(Source):
    id = "nhsa_dongtai"
    label = "国家医保局 · 医保动态"
    category = "policy"
    url = "http://www.nhsa.gov.cn/col/col14/index.html"
    max_items = 20

    # /art/2026/4/14/art_14_20212.html  +  optional <span>2026-04-14</span>
    LINK_RE = re.compile(
        r'<a[^>]+href="(/art/(\d{4})/(\d{1,2})/(\d{1,2})/[^"]+)"[^>]*>([^<]+)</a>'
    )

    def parse(self, html: str) -> List[Item]:
        items: List[Item] = []
        seen = set()
        for m in self.LINK_RE.finditer(html):
            href, y, mo, d, title = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
            title = title.strip()
            if not title or len(title) < 4:
                continue
            full_url = urljoin(self.url, href)
            if full_url in seen:
                continue
            seen.add(full_url)
            date = f"{y}-{int(mo):02d}-{int(d):02d}"
            items.append(Item(
                id=hashlib.md5(full_url.encode()).hexdigest()[:12],
                title=title,
                url=full_url,
                source_id="",
                source_label="",
                category="",
                publish_date=date,
                summary="",
            ))
        # Fallback: try BS4 if regex got nothing
        if not items:
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                m2 = re.search(r"/art/(\d{4})/(\d{1,2})/(\d{1,2})/", href)
                if not m2:
                    continue
                title = a.get_text(strip=True)
                if not title or len(title) < 4:
                    continue
                full_url = urljoin(self.url, href)
                if full_url in seen:
                    continue
                seen.add(full_url)
                y, mo, d = m2.group(1), int(m2.group(2)), int(m2.group(3))
                items.append(Item(
                    id=hashlib.md5(full_url.encode()).hexdigest()[:12],
                    title=title,
                    url=full_url,
                    source_id="",
                    source_label="",
                    category="",
                    publish_date=f"{y:04d}-{mo:02d}-{d:02d}",
                    summary="",
                ))
        return items
