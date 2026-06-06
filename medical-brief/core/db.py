"""SQLite-backed dedup + history store."""
from __future__ import annotations
import sqlite3
import json
from datetime import datetime, date
from pathlib import Path
from typing import Iterable, List, Dict

from sources.base import Item


class DB:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self):
        with self._conn() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source_id TEXT,
                    source_label TEXT,
                    category TEXT,
                    publish_date TEXT,
                    summary TEXT,
                    matched_kw TEXT,
                    fetched_at TEXT
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_fetched ON items(fetched_at)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_cat ON items(category)")

    def _conn(self):
        return sqlite3.connect(self.path)

    def is_new(self, item_id: str) -> bool:
        with self._conn() as c:
            r = c.execute("SELECT 1 FROM items WHERE id=?", (item_id,)).fetchone()
            return r is None

    def save(self, item: Item) -> bool:
        """Insert if new. Returns True if inserted (new), False if duplicate."""
        if not self.is_new(item.id):
            return False
        with self._conn() as c:
            c.execute("""
                INSERT OR IGNORE INTO items
                (id, title, url, source_id, source_label, category,
                 publish_date, summary, matched_kw, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item.id, item.title, item.url, item.source_id,
                  item.source_label, item.category, item.publish_date,
                  item.summary, json.dumps(item.matched_kw, ensure_ascii=False),
                  item.fetched_at))
        return True

    def save_many(self, items: Iterable[Item]) -> Dict[str, int]:
        new_count = 0
        dup_count = 0
        for it in items:
            if self.save(it):
                new_count += 1
            else:
                dup_count += 1
        return {"new": new_count, "dup": dup_count}

    def query_today(self, today: str = None) -> List[Dict]:
        """Return all items fetched today (default: actual today)."""
        if today is None:
            today = date.today().isoformat()
        with self._conn() as c:
            rows = c.execute("""
                SELECT id, title, url, source_id, source_label, category,
                       publish_date, summary, matched_kw, fetched_at
                FROM items
                WHERE fetched_at LIKE ? || '%'
                ORDER BY
                  CASE WHEN publish_date != '' THEN publish_date ELSE fetched_at END DESC,
                  fetched_at DESC
            """, (today,)).fetchall()
        out = []
        for r in rows:
            d = {
                "id": r[0], "title": r[1], "url": r[2],
                "source_id": r[3], "source_label": r[4], "category": r[5],
                "publish_date": r[6], "summary": r[7],
                "matched_kw": json.loads(r[8]) if r[8] else [],
                "fetched_at": r[9],
            }
            out.append(d)
        return out

    def query_recent(self, days: int = 7) -> List[Dict]:
        """Return all items from the last N days, newest first."""
        with self._conn() as c:
            rows = c.execute("""
                SELECT id, title, url, source_id, source_label, category,
                       publish_date, summary, matched_kw, fetched_at
                FROM items
                WHERE date(fetched_at) >= date('now', ?)
                ORDER BY fetched_at DESC
                LIMIT 500
            """, (f"-{days} day",)).fetchall()
        out = []
        for r in rows:
            out.append({
                "id": r[0], "title": r[1], "url": r[2],
                "source_id": r[3], "source_label": r[4], "category": r[5],
                "publish_date": r[6], "summary": r[7],
                "matched_kw": json.loads(r[8]) if r[8] else [],
                "fetched_at": r[9],
            })
        return out
