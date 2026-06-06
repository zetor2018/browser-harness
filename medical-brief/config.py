"""Medical brief — configuration.

Edit SOURCES to add/remove news sources.
Edit KEYWORDS to tune what gets highlighted as "matched".
"""
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "brief.db"

# Sources to fetch. Each entry: id, label, category, url, parser name, max items.
# Categories: 'policy' (医保/政策), 'ai' (医疗 AI / 创新器械)
SOURCES = [
    {
        "id": "nhsa_dongtai",
        "label": "国家医保局 · 医保动态",
        "category": "policy",
        "url": "http://www.nhsa.gov.cn/col/col14/index.html",
        "parser": "nhsa_list",
        "max_items": 20,
        "needs_browser": False,
    },
    {
        "id": "nhsa_tanpan",
        "label": "国家医保局 · 医保谈判与支付方式改革",
        "category": "policy",
        "url": "http://www.nhsa.gov.cn/col/col19/index.html",
        "parser": "nhsa_list",
        "max_items": 15,
        "needs_browser": False,
    },
    # 国务院政策 — gov.cn WAF returns 403 to default urllib. Re-enable
    # once browser-harness is wired in.
    # {
    #     "id": "gov_zhengce",
    #     "label": "国务院政策 · 医疗相关",
    #     "category": "policy",
    #     "url": "http://www.gov.cn/zhengce/",
    #     "parser": "gov_list",
    #     "max_items": 30,
    #     "needs_browser": True,
    # },
    # Browser-needed sources (require JS rendering or have WAF).
    # Uncomment when you have browser-harness connected.
    # {
    #     "id": "nhc_zwjk",
    #     "label": "国家卫健委 · 政策文件",
    #     "category": "policy",
    #     "url": "http://www.nhc.gov.cn/yzygj/s3593/wszl.shtml",
    #     "parser": "nhc_list",
    #     "max_items": 20,
    #     "needs_browser": True,
    # },
    # {
    #     "id": "cmde_zdyz",
    #     "label": "CMDE · 指导原则与公示",
    #     "category": "ai",
    #     "url": "https://www.cmde.org.cn/flfg/zdyz/index.html",
    #     "parser": "cmde_list",
    #     "max_items": 20,
    #     "needs_browser": True,
    # },
    # {
    #     "id": "nmpa_gzwj",
    #     "label": "国家药监局 · 政策法规",
    #     "category": "ai",
    #     "url": "https://www.nmpa.gov.cn/xxgk/fgwj/gzwj/gzwjyp/",
    #     "parser": "nmpa_list",
    #     "max_items": 20,
    #     "needs_browser": True,
    # },
]

# Keywords for highlighting. Matched items are visually marked in the brief
# and counted in the summary header.
KEYWORDS_POLICY = [
    "DRG", "DIP", "医保支付", "医保结算", "集采", "医保目录",
    "电子病历", "互联网医院", "医共体", "紧密型", "分级诊疗",
    "三医联动", "医保飞检", "DIP改革", "医保基金", "医保局",
    "国家医保", "医保谈判", "医疗服务价格", "医保支付方式",
]

KEYWORDS_AI = [
    "医疗AI", "辅助诊断", "AI医疗器械", "大模型医疗", "医疗大模型",
    "创新医疗器械", "三类证", "二类证", "数字疗法", "DTx",
    "医学影像AI", "病理AI", "智能问诊", "AI制药",
    "智能医疗器械", "人工智能医疗器械", "深度学习医疗器械",
]

# All keywords merged (used for highlight lookup)
ALL_KEYWORDS = sorted(set(KEYWORDS_POLICY + KEYWORDS_AI))

# HTTP request settings
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
HTTP_TIMEOUT = 20  # seconds
FETCH_DELAY = 1.0  # seconds between requests to same host
