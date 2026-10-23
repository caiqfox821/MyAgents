# 营养知识库建设 · 进度记录（会话续作）

> 用于**跨会话续作**：每次会话结束前更新「已完成 / 待办 / 命令备忘 / 已知问题」。
> 任务目标（用户）：从网上查询下载 ebook、调用 PAPERS MCP 查询「营养干预疾病」文献、从 WHO 等网站下载 guideline，存入本地；梳理成**条目**，颗粒度到 **L3**，与其他专家一致。**干一小时，停止，保存进度，明日继续。**

---

## 会话 1（2026-10-20）· 已完成

### 1. 基础设施（`references/books/`）
- 目录：`mdpi/ who/ text/{mdpi,who}/ toc/{mdpi,who}/ tools/`
- 工具：
  - `tools/discover_mdpi.py` —— Crossref REST（prefix 10.3390, type:book）发现 MDPI 书目，解析 reprint id。
  - `tools/curate_mdpi.py` —— 人类营养主题筛选 + 自动打标（→ `sources_mdpi.json`，108 册候选）。
  - `tools/discover_who.py` —— WHO IRIS **DSpace 7 REST** 发现指南并解析 PDF 直链（→ `sources_who.json`，123 篇）。
  - `tools/fetch_fao.py`、`tools/fetch_papers.py`、`tools/build_booklib.py`（下载+完整性校验+断点续传+抽取+编目）、`tools/search_books.py`、`tools/read_page.py`。

### 2. 资源下载（`references/books/`，约 1.8 GB）
| 分区 | 来源 | 数量 | 许可 |
|---|---|---|---|
| `mdpi/` | MDPI Books（Crossref→mdpi-res CDN） | **99 册** | CC BY 4.0 |
| `who/` | WHO IRIS（DSpace 7 REST bitstream） | **117 篇**（PDF 122） | CC BY-NC-SA 3.0 IGO |
| 文本 | `text/<分区>/`（pdftotext -layout） | **221 份** | — |
| 目录 | `toc/<分区>/` | **216 份** | — |

- 编目：`catalog.json`（216 条，无重复）、`INDEX.md`（主题标签 + 分区书目表）。

### 3. 文献（`references/papers/`，PAPERS MCP → EuropePMC）
- 检索式：`(<20 类疾病/人群主题>) AND OPEN_ACCESS:Y`，按被引降序，**123 篇开放获取文献**。
- 产出：`papers/papers.json`、`papers/文献清单-营养.md`、`papers/fulltext/*.xml`（**62 篇** JATS 全文）。

### 4. L3 条目（与其他专家同构）
- `references/证据条目与出处.md` —— 六节：① WHO 膳食/慢病核心推荐（含页码）② 膳食模式与心血管代谢 ③ 微量营养素补充与强化 ④ 婴幼儿与临床营养 ⑤ 文献证据（OA，含 DOI/PMCID）⑥ 待补。
- `references/指南条目-WHO.md` —— 123 篇 WHO 指南/报告条目索引（年份/IRIS 来源/全文/许可），按主题分组。

---

## 待办（会话 2 起）

1. **MDPI 逐册消化**：对 99 册按主题抽取定量条目（当前仅覆盖高命中书），补 2025–2026 新书。
2. **文献定量抽取**：解析 `papers/fulltext/*.xml`（62 篇）批量生成「结论/效应量/人群」条目，并入 `证据条目与出处.md` 第五节。
3. **补两条未达成的下载**（MDPI 10 册 slug 失配）：
   - 失败书目见 `/tmp/nut_mdpi_dl.log` 的 `[fail]`（2026 新书 reprint id 与 bookfiles id 可能不一致）。
   - 对策：改用 MDPI 官方页面/DOAB 反查真实 slug，或经 `sources_mdpi_raw.json` 换其他来源。
4. **扩充来源**：FAO/UNICEF/WFP 营养出版物；中国 DRIs/膳食指南要点（**需用户提供或联网核验后收录，不得臆造**）。
5. **可选**：为 `papers/` 增加 PDF 版全文（EuropePMC `?pdf=render`，当前 PMC 直链 403，建议改用 EuropePMC 渲染或仅保留 XML）。
6. **对齐**：与种植/发酵/食品加工/食品安全/质谱专家的证据条目深度与命名保持同构（本轮已用同模板）。

---

## 命令备忘

```bash
cd 营养专家/references/books
# 续下载（跳过已存在）
python3 tools/build_booklib.py . sources_mdpi.json sources_who.json --jobs 4
# 仅编目（不下载）
python3 tools/build_booklib.py . sources_mdpi.json sources_who.json --no-download
# 检索 / 读页
python3 tools/search_books.py "sodium intake" --books
python3 tools/read_page.py Guideline_sodium_intake_for_adults_and_children 10
# 文献
python3 tools/fetch_papers.py --max 12
```

## 已知问题
- MDPI：10 册 slug 失配（`[fail]`）；`curate_mdpi.py` 的 KEEP/BLOCK 可用关键词继续微调。
- WHO：4 篇为扫描件，`pdftotext` 抽取失败（`抽取失败`），需 OCR 或另找文本版。
- `papers/pdf/` 为空（MCP `download_with_fallback` 对 PMC 返回 403），全文以 XML 形式保存于 `papers/fulltext/`。

---
*更新于 2026-10-20（会话 1 结束）。*
