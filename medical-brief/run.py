"""medical-brief — daily medical news & policy aggregator.

Usage:
    python run.py                # fetch all sources, generate today's brief
    python run.py --days 7       # show brief for last 7 days
    python run.py --render-only  # re-render HTML from DB (no fetch)
    python run.py --source ID    # only fetch one source
"""
from __future__ import annotations
import argparse
import sys
import traceback
from datetime import date
from pathlib import Path

# ensure stdout works with UTF-8 on Windows consoles (GBK default)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ensure relative imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from core.db import DB
from core.parse import match_keywords
from core.render import write_brief, render_html
from sources import REGISTRY


def make_source(spec: dict):
    cls = REGISTRY.get(spec["parser"])
    if not cls:
        raise ValueError(f"Unknown parser: {spec['parser']}")
    return cls(**{k: v for k, v in spec.items() if k != "parser"})


def fetch_all(db: DB, only_source: str = None) -> dict:
    stats = {"sources": 0, "fetched": 0, "new": 0, "dup": 0, "errors": []}
    for spec in config.SOURCES:
        if only_source and spec["id"] != only_source:
            continue
        if spec.get("needs_browser"):
            print(f"  [skip] {spec['id']}  (needs browser-harness, not yet wired)")
            continue
        print(f"  [fetch] {spec['id']}  -> {spec['url']}")
        try:
            src = make_source(spec)
            items = src.run()
            # match keywords
            for it in items:
                it.matched_kw = match_keywords(it.title + " " + it.summary, config.ALL_KEYWORDS)
            result = db.save_many(items)
            stats["sources"] += 1
            stats["fetched"] += len(items)
            stats["new"] += result["new"]
            stats["dup"] += result["dup"]
            print(f"    -> {len(items)} items ({result['new']} new, {result['dup']} dup)")
        except Exception as e:
            err = f"{spec['id']}: {type(e).__name__}: {e}"
            stats["errors"].append(err)
            print(f"    [ERR] {err}")
    return stats


def main():
    ap = argparse.ArgumentParser(description="医疗资讯日报生成器")
    ap.add_argument("--days", type=int, default=1, help="简报覆盖天数 (1=今天, 7=近 7 天)")
    ap.add_argument("--render-only", action="store_true", help="不抓取，只重新生成 HTML")
    ap.add_argument("--source", type=str, default=None, help="只跑指定 source id")
    ap.add_argument("--out", type=str, default=None, help="输出 HTML 路径 (默认 output/YYYY-MM-DD.html)")
    args = ap.parse_args()

    db = DB(config.DB_PATH)
    today = date.today().isoformat()

    if not args.render_only:
        print(f"\n=== medical-brief · {today} ===\n")
        stats = fetch_all(db, args.source)
        print(f"\n汇总: {stats['sources']} 源 · 抓取 {stats['fetched']} 条 · 新增 {stats['new']} · 重复 {stats['dup']}")
        if stats["errors"]:
            print(f"错误 {len(stats['errors'])} 个:")
            for e in stats["errors"]:
                print(f"  - {e}")

    # query
    if args.days == 1:
        items = db.query_today(today)
    else:
        items = db.query_recent(args.days)

    if not items:
        print("\n没有数据 — 跑一次完整 fetch，或者检查 DB。")
        return

    out_path = Path(args.out) if args.out else (config.OUTPUT_DIR / f"{today}.html")
    write_brief(items, out_path, today)
    print(f"\n[OK] 简报已生成: {out_path}")
    print(f"     {len(items)} 条 · 打开方式: explorer {out_path}")


if __name__ == "__main__":
    main()
