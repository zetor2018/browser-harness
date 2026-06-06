"""国务院政策 — 政府网 zhengceku.

Strategy: fetch the policy list page, extract all policy links, and filter
to medical-related ones by keyword match on title.

List URL: http://www.gov.cn/zhengce/zhengceku/
"""
from __future__ import annotations
import re
import hashlib
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import Source, Item
from config import ALL_KEYWORDS


class GovSource(Source):
    id = "gov_zhengce"
    label = "国务院政策 · 医疗相关"
    category = "policy"
    url = "http://www.gov.cn/zhengce/zhengceku/"
    max_items = 30
    filter_kw = True

    # 政策类型栏目 (each has its own list page; we'll grab the front page)
    DATE_RE = re.compile(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})")

    def parse(self, html: str) -> List[Item]:
        soup = BeautifulSoup(html, "lxml")
        items: List[Item] = []
        seen = set()
        # Look for any link to a content page (gov.cn/content/...)
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/content/" not in href and "zhengce/content" not in href:
                # also accept relative policy links
                if not href.startswith("20") and "/20" not in href:
                    continue
            full_url = urljoin(self.url, href)
            if full_url in seen:
                continue
            title = a.get_text(strip=True)
            if not title or len(title) < 6 or len(title) > 120:
                continue
            # Filter to medical-related
            if self.filter_kw and not self._is_medical(title):
                continue
            seen.add(full_url)
            date = self._extract_date(title) or ""
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
        return items

    def _is_medical(self, title: str) -> bool:
        for kw in ALL_KEYWORDS:
            if kw in title:
                return True
        # extra broad keywords for policy-level coverage
        for kw in ("医疗", "医保", "医院", "卫生", "药品", "医药",
                   "健康", "医师", "护士", "药监", "临床"):
            if kw in title:
                return True
        return False

    def _extract_date(self, title: str) -> str:
        # 标题里很少带日期，跳过
        return ""
