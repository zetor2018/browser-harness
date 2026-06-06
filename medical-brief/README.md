# medical-brief

医疗资讯日报生成器 — 每天自动从公开政府站抓取医疗政策 / 创新器械资讯，按类别整理成单页 HTML 简报，命中关键词的条目高亮显示。

- 仅抓公开信息，不登录、不碰医院内网、不抓医保结算明细
- 依赖最少：Python 3.10+ + BeautifulSoup4 + lxml
- 单文件 SQLite 做去重和历史，可累积为本地资料库
- 输出单页响应式 HTML，支持浅色 / 暗色、移动端

---

## 1. 项目结构

```
medical-brief/
├── run.py              # 入口 (CLI)
├── config.py           # 源 / 关键词 / UA / 节流配置
├── sources/
│   ├── base.py         # Source 基类 + Item 数据类
│   ├── nhsa.py         # 医保局列表解析器
│   └── gov.py          # 国务院解析器 (未启用, gov.cn WAF 拦截)
├── core/
│   ├── db.py           # SQLite 去重 + 查询
│   ├── parse.py        # 关键词匹配 / 文本清理
│   └── render.py       # HTML 简报模板 + 渲染
├── data/brief.db       # 历史库 (SQLite, .gitignore)
└── output/YYYY-MM-DD.html  # 每日简报 (按日期, .gitignore)
```

**核心模块链接**：
- [run.py](file:///d:/workproj/AI/browser-harness/medical-brief/run.py) — CLI 入口
- [config.py](file:///d:/workproj/AI/browser-harness/medical-brief/config.py) — 全部配置
- [sources/base.py](file:///d:/workproj/AI/browser-harness/medical-brief/sources/base.py) — `Source` 基类与 `Item` 数据类
- [sources/nhsa.py](file:///d:/workproj/AI/browser-harness/medical-brief/sources/nhsa.py) — 医保局解析器（含 CDATA 兼容方案）
- [core/db.py](file:///d:/workproj/AI/browser-harness/medical-brief/core/db.py) — SQLite 封装
- [core/render.py](file:///d:/workproj/AI/browser-harness/medical-brief/core/render.py) — HTML 模板 + CSS（暗色自适应）

---

## 2. 安装

```powershell
cd medical-brief
pip install beautifulsoup4 lxml
```

只用到了两个第三方包，sqlite3 是 Python 内置。

**Windows 控制台编码修复**：[run.py](file:///d:/workproj/AI/browser-harness/medical-brief/run.py) 启动时把 `sys.stdout` 重配为 `utf-8`，避免 GBK 控制台打印中文报错。

---

## 3. 使用方法

### 3.1 跑一次（抓取 + 生成简报）

```powershell
python run.py
```

输出示例：

```
=== medical-brief · 2026-06-06 ===

  [fetch] nhsa_dongtai  -> http://www.nhsa.gov.cn/col/col14/index.html
    -> 20 items (20 new, 0 dup)
  [fetch] nhsa_tanpan   -> http://www.nhsa.gov.cn/col/col19/index.html
    -> 10 items (10 new, 0 dup)

汇总: 2 源 · 抓取 30 条 · 新增 30 · 重复 0

[OK] 简报已生成: D:\...\output\2026-06-06.html
     30 条 · 打开方式: explorer D:\...\output\2026-06-06.html
```

### 3.2 看近 7 天

```powershell
python run.py --days 7
```

### 3.3 不抓取，只重渲染

DB 已有数据但模板 / 关键词改了，只想重出 HTML：

```powershell
python run.py --render-only
```

### 3.4 单源调试

```powershell
python run.py --source nhsa_dongtai
```

### 3.5 定时任务

在 Windows 任务计划程序里添加一个每日 08:00 触发的任务：

```
程序: python
参数: D:\...\medical-brief\run.py
起始位置: D:\...\medical-brief
```

---

## 4. 数据源

### 4.1 当前启用

| ID | 来源 | 类别 | URL | 抓取方式 |
|---|---|---|---|---|
| `nhsa_dongtai` | 国家医保局 · 医保动态 | policy | [nhsa/col/col14](http://www.nhsa.gov.cn/col/col14/index.html) | http_get |
| `nhsa_tanpan` | 国家医保局 · 医保谈判与支付方式改革 | policy | [nhsa/col/col19](http://www.nhsa.gov.cn/col/col19/index.html) | http_get |

### 4.2 已 stub，等 browser-harness 接上

| ID | 来源 | 障碍 |
|---|---|---|
| `gov_zhengce` | 国务院政策 | WAF 拦截 urllib（403） |
| `nhc_zwjk` | 国家卫健委 · 政策文件 | WAF 拦截（412） |
| `nmpa_gzwj` | 国家药监局 · 政策法规 | WAF 拦截（412） |
| `cmde_zdyz` | CMDE 器审中心 · 指导原则 | JS SPA（返回 202 + 占位） |
| `nhsa_jijian` | 国家医保局 · 集采 | 列表页为空，文章在子页里 |

把它们在 [config.py](file:///d:/workproj/AI/browser-harness/medical-brief/config.py) 里取消注释，对应 `parser` 写进 [sources/__init__.py](file:///d:/workproj/AI/browser-harness/medical-brief/sources/__init__.py) 的 `REGISTRY`，再写一个 `parse()` 即可。

### 4.3 加新源的步骤

1. 在 [sources/](file:///d:/workproj/AI/browser-harness/medical-brief/sources) 新建 `xxx.py`，继承 `Source`：

   ```python
   from .base import Source, Item
   from typing import List

   class XxxSource(Source):
       id = "xxx"
       label = "某网站"
       category = "policy"
       url = "https://xxx.com/list"
       max_items = 20

       def parse(self, html: str) -> List[Item]:
           # 用 BS4 / 正则提取 (title, url, date)
           # 返回 List[Item]
           ...
   ```

2. 在 [sources/__init__.py](file:///d:/workproj/AI/browser-harness/medical-brief/sources/__init__.py) 注册：

   ```python
   from .xxx import XxxSource
   REGISTRY["xxx_list"] = XxxSource
   ```

3. 在 [config.py](file:///d:/workproj/AI/browser-harness/medical-brief/config.py) 加一条 `SOURCES` 字典，`parser` 字段对应 `REGISTRY` 的 key。

---

## 5. 关键词

在 [config.py](file:///d:/workproj/AI/browser-harness/medical-brief/config.py)：

- `KEYWORDS_POLICY` — 政策类（DRG / DIP / 集采 / 互联网医院…）
- `KEYWORDS_AI` — 医疗 AI / 创新器械类（三类证 / 数字疗法 / 病理 AI…）
- `ALL_KEYWORDS` — 上面两份合并去重，运行时匹配用

匹配方式（[core/parse.py](file:///d:/workproj/AI/browser-harness/medical-brief/core/parse.py#L17-L24)）：对 `title + summary` 做子串匹配，命中的关键词作为 badge 渲染在简报条目上，并在顶部统计「命中关键词 X 条」。

**调优**：

- 想看更细的方向 → 往对应列表里加词
- 想去掉一类内容 → 从列表里删
- 不区分政策/AI 类别 → 直接改 `ALL_KEYWORDS` 即可

---

## 6. 数据模型

SQLite 单表 [items](file:///d:/workproj/AI/browser-harness/medical-brief/core/db.py#L18-L28)：

```sql
CREATE TABLE items (
    id           TEXT PRIMARY KEY,   -- URL md5 前 12 位
    title        TEXT NOT NULL,
    url          TEXT NOT NULL,
    source_id    TEXT,
    source_label TEXT,
    category     TEXT,                -- 'policy' | 'ai'
    publish_date TEXT,                -- YYYY-MM-DD
    summary      TEXT,
    matched_kw   TEXT,                -- JSON 数组
    fetched_at   TEXT                 -- ISO timestamp
);
```

- 主键是 URL 的 md5 前 12 位 → 天然去重
- 索引：`fetched_at`、`category`
- 查询入口（[core/db.py](file:///d:/workproj/AI/browser-harness/medical-brief/core/db.py)）：
  - `query_today(today)` — 当天抓的全部
  - `query_recent(days)` — 近 N 天

---

## 7. 输出 HTML

每个 `python run.py` 生成 `output/YYYY-MM-DD.html`。模板见 [core/render.py](file:///d:/workproj/AI/browser-harness/medical-brief/core/render.py)。

结构：

```
医疗资讯日报
  2026-06-06 · 共 30 条 · 命中关键词 10 条
  政策类: 30 · AI/器械类: 0 · 数据源: 2 · 生成时间: HH:MM:SS

  ── 医保 / 政策 ─────────────────
    [title]  [link]
    来源 · 日期 · [关键词1] [关键词2]

  ── 医疗 AI / 创新器械 ─────────
    （无数据时显示"今日无新增"）

  ── footer ──
```

CSS 关键点：

- 响应式：`max-width: 960px;` + `meta viewport`
- 暗色自适应：`@media (prefers-color-scheme: dark)`
- 关键词 badge：浅色 `#fff3bf` 底 + 深色 `#5a4a00` 底
- hover 高亮

---

## 8. 技术实现要点

### 8.1 解析策略：正则优先，BS4 兜底

医保局页面的文章列表是嵌在 `<record>...</record>` CDATA 风格块里（[sources/nhsa.py](file:///d:/workproj/AI/browser-harness/medical-brief/sources/nhsa.py#L27-L29)）：

```html
<record>
  <li>
    <a href="/art/2026/6/6/art_14_20877.html" title="..." target="_blank">2026年第二批医保参照药预沟通论证顺利实施</a>
    <span>2026-06-06</span>
  </li>
</record>
```

`lxml` 解析器遇到 `<record>` 会把内部当 XML 处理，跳过。`html.parser` 能用但慢。

**方案**：

1. 主路径用正则提取 `href` 和 `title`
2. 正则没拿到（结构变化）→ fallback 到 `BS4(html.parser)`
3. 都拿不到 → 该源当 0 条处理，stderr 报 `[ERR]`

这样政府站改版小调整都不会让整套挂掉。

### 8.2 节流

[sources/base.py](file:///d:/workproj/AI/browser-harness/medical-brief/sources/base.py#L46-L66) 的 `fetch()` 记录 `_last_fetch` 时间戳，间隔不足 `FETCH_DELAY`（默认 1s）就 `sleep`。政府站普遍有轻量反爬，1 秒足够不触发。

### 8.3 去重

两层去重：

- **同次抓取内**：[sources/nhsa.py](file:///d:/workproj/AI/browser-harness/medical-brief/sources/nhsa.py#L37-L42) `seen` set 防 URL 重复
- **跨次抓取**：[core/db.py](file:///d:/workproj/AI/browser-harness/medical-brief/core/db.py#L33-L39) `is_new()` 在 insert 前查主键

第二次跑同一天的所有条目都会标 `dup`，不进 DB，不影响简报数量（query_today 还是返回全部条目，但 SQL 时间窗口只看 `fetched_at LIKE 'today%'`，所以历史数据不会混进来）。

### 8.4 关键词匹配

```python
def match_keywords(text, keywords):
    return [kw for kw in keywords if kw in text]
```

线性扫，对每天几十条数据足够。命中后：

- 简报 HTML 上显示 badge
- 顶部统计 `命中关键词 N 条`
- DB 里存 `matched_kw` 数组，便于后续做统计 / 趋势分析

### 8.5 HTML 渲染

用 `string.Template`（[core/render.py](file:///d:/workproj/AI/browser-harness/medical-brief/core/render.py#L11-L42)），不引 Jinja2 减少依赖。`substitute()` 替换 8 个变量，body 由两个 section 拼接。

CSS 内嵌在 `<style>` 里，文件开箱可离线打开。

### 8.6 跨平台 stdout 编码

[run.py](file:///d:/workproj/AI/browser-harness/medical-brief/run.py#L16-L21) 启动时 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` —— Windows 默认 GBK 控制台打中文会 `UnicodeEncodeError`，这步让它在 PowerShell 旧版也能跑。

---

## 9. 已知限制

1. **WAF / JS 渲染的源**：gov.cn / nhc / nmpa / cmde 都不行，等接上 browser-harness 用 `http_get` 走 fetch-use 代理或浏览器渲染
2. **集采子页（nhsa col21）**：列表页只显示框架，文章链接在子页里 — 需遍历分页
3. **关键词只是子串匹配**：可能误中（如「医保」会中「医保改革」和「医保乱象」），可改成正则或加停用词
4. **没有去重摘要**：标题近似但 URL 不同的两条都会进库（不常见，但发生过）
5. **没有正文**：只抓标题 + URL，点开才看正文 — 抓正文涉及反爬和解析复杂度
6. **没有时区感知**：`fetched_at` 用本地时间，跨时区跑会错位

---

## 10. 扩展方向

按 ROI 排序：

| 方向 | 价值 | 难度 |
|---|---|---|
| 接 browser-harness 解锁 nhc / nmpa / cmde | 覆盖 +50% 政策 / 器械 | 低（用 `http_get` 替换 Source.fetch） |
| 抓正文做 1-2 句 AI 摘要 | 不用点开就能判断价值 | 中（需 LLM 调用） |
| Bark / 微信推送 | 不开电脑也能看 | 低 |
| 招标采购（ccgp.gov.cn） | 加一类 | 中（需节流 + 关键词过滤） |
| 内容备份到 wayback | 政策原文消失时仍能查 | 中 |
| 多账号并行抓取 | 每天节省抓取时间 | 高 |

---

## 11. 与 browser-harness 的关系

medical-brief 是 browser-harness 的下游应用（不是其插件）：

- 没用到 browser-harness 的 daemon / CDP / 截图
- 只用 `http_get` 的能力，本项目自己用 `urllib` 实现了等价版本
- 等需要抓 nhc / nmpa / cmde 时，可以改 `Source.fetch()` 调用 `browser-harness` 提供的 `http_get`（带 fetch-use 代理绕过 WAF）
- 完全可以在没装 browser-harness 的机器上独立运行

如果要把它做成 browser-harness 的官方 domain-skill，路径是：

1. 把 [run.py](file:///d:/workproj/AI/browser-harness/medical-brief/run.py) 的逻辑改写成可被 `browser-harness -c` 调用的脚本
2. 在 `domain-skills/medical-brief/` 写 SKILL.md
3. helpers 用 `new_tab` / `js` 替换 `urllib` 调用，复用用户 Chrome 的登录态
