# 公共知识 · 书库（开放获取全文库）

> 面向**所有领域专家**的原文底座：收录可合法全文获取的**权威指南章节、MDPI 开放获取专著、EuropePMC 开放获取文献**，并配套**检索与按页读取工具**。
> 目的只有一个：让领域结论**可回溯到原文页码/章节**，杜绝凭印象编数值。

**位置**：`公共知识/书库/`（经 `opencode.json` 的 `references` 注册为全局只读共享库）
**许可**：WHO/FAO 开放获取 · **ICH/EC 公开获取** · MDPI Books **CC BY 4.0** · EuropePMC OA（检索一律带 `OPEN_ACCESS:Y`）

---

## 一、目录结构

| 目录/文件 | 内容 | 说明 |
|---|---|---|
| `guides/` | 机构权威文本 PDF：**WHO/FAO EHC 240（2020 更新）** 章节（Ch5 剂量-反应、Ch6 膳食暴露、§4.5 遗传毒性含 TTC 决策树、§9.1.4.2 食品用酶）；**ICH M7(R2)（2023 Step 4 final）**；**SANTE/11312/2021 v2026（2025）**；**OECD 指南**（体外免疫毒性 DRP、DNT IVB 数据评价、职业生物监测、人造纳米材料风险、GLP-IT 安全、GLP-ISO/IEC 17025、组织病理内分泌/生殖）；**MDPI 丛书**（食品化学污染物分析、真菌毒素 LC-MS/MS、丙烯酰胺、纳米材料毒性） | WHO 来自 `cdn.who.int`、ICH 来自 `database.ich.org`、SANTE 来自 `food.ec.europa.eu`、OECD 来自 `one.oecd.org`、MDPI 来自 `mdpi-res.com` |
| `mdpi/` | MDPI Books 专著 PDF **24 册**（分析/质谱/毒理/风险评估/农残/真菌毒素/QMRA/纳米材料等主题） | 来自 `mdpi-res.com/bookfiles/{book\|reprint\|topic}/{id}/{slug}.pdf` |
| `papers/xml/`、`papers/txt/` | EuropePMC **OA 全文**（JATS XML + 纯文本）**176 篇**（主题可交叉：guides 60 / tox 41 / risk 39 / ms 39）。含 **PMC12332500＝EFSA SC 2025 MOE《Statement》（一级权威文本）**、**PMC7500704＋PMC7734868＝ICH M7 (Q)SAR 操作规程与模型版本漂移**、**PMC12175843＋PMC13593624＝医疗器械非致癌 LTL-TTC 与 E&L（SCT/QT→AET）** | `papers/INDEX.md`、`papers/index.json` 为索引 |
| `text/guides/`、`text/mdpi/` | 上述 PDF 的 `pdftotext -layout` 全文（**以 `\f` 分页**） | 页码检索的依据 |
| `toc/` | 每册自动提取的目录 | `toc/{sub}/{书}.md` |
| `catalog.json` | 合并书目（文件、题名、年、出版者、许可、页数、标签、全文路径） | 由 `tools/build_booklib.py` 生成 |
| `INDEX.md` | 人读索引：主题标签 + 分库清单 | 同上 |
| `sources_*.json`、`seed_guides.json` | **取料清单**（可复现） | 新增书目改这里 |
| `tools/` | 见下节 | — |

## 二、工具（各专家通用）

```bash
cd 公共知识/书库
python3 tools/search_books.py "benchmark dose" --context 1     # 全库检索：书 | 物理页码 | 原文
python3 tools/search_books.py "MRM" --books                    # 限定 MDPI 专著
python3 tools/read_page.py WHO_EHC240_Ch5 48                   # 按物理页读原文
grep -o '.\{0,140\}MOEs ≥ 1500.\{0,140\}' papers/txt/PMC13403159.txt
python3 tools/build_booklib.py . sources_mdpi.json seed_guides.json sources_guides.json
python3 tools/curate_mdpi.py --dry-run                         # MDPI 新书两级筛选（REQUIRE/BLOCK + 配额）
env -u http_proxy -u https_proxy -u all_proxy python3 tools/fetch_papers.py --theme guides --per-theme 20
```

| 脚本 | 用途 |
|---|---|
| `build_booklib.py` | 下载（多 slug/kind 变体 + `pdf_url` 显式直链）→ 抽文本 → 提目录 → 重建 `catalog.json`/`INDEX.md`/`toc/` |
| `discover_mdpi.py` / `curate_mdpi.py` | 从 Crossref 发现 MDPI 书目（`type:book`, `prefix:10.3390`）→ 按主题 REQUIRE/BLOCK 词与配额精选 |
| `discover_guides.py` | 指南发现（OpenAlex 候选 + `one.oecd.org`/机构直链可达性核实；**会话 6 起可用**，见 `sources_guides.json`） |
| `fetch_papers.py` | EuropePMC REST 取 OA 全文；支持 4 主题与 `TITLE:"…"` 精确检索，**增量落盘** |
| `search_books.py` / `read_page.py` | 取证入口（所有 L3 条目文件的页码均可用这两个脚本复现） |

## 三、由本库消化出的 L3 证据条目文件

| 条目文件 | 服务的专家/技能 | 条目体系 |
|---|---|---|
| `公共知识/技术指南/风险评估-证据条目与出处.md` | 公共技能 `risk-assessment`（全专家共用） | `1-x` HBGV/POD/BMR、`2-x` 暴露与 IESTI、`3-x` TTC/MOE、`4-x` 不确定性、`5-x` 工作例、`6-x` iTTC/LTL、`7-x` 使用纪律、`8-x` 复现清单 |
| `毒理专家/references/证据条目与出处.md` | 毒理专家 / 技能 `toxicology` | `T-` POD/UF/BMD、`G-` 遗传毒性、`E-` 数据要求（食品用酶）、`R-` read-across、`N-` 体外/组学 PoD、`C-` TTC/iTTC/LTL、`A-` AOP/NAMs |
| `质谱专家/references/证据条目与出处.md` | 质谱专家 / 技能 `mass-spectrometry` | `M-` 验证判据、`P-` 仪器参数、`S-` 前处理/基质效应、`Q-` 定量与不确定度、`H-` HRMS 非靶向、`C-` 置信分级、`O-` 组学、`L-` 与暴露/毒理接口 |

> 营养专家的对应文件（`营养专家/references/证据条目与出处.md`、`指南条目-WHO.md`）使用同一套取料与工具（`books/` 为其历史库路径）。

## 四、引用与页码约定

1. **指南章节**：`WHO/FAO. EHC 240（2020 更新）Ch5/§4.5/§9.1.4.2. 公共知识/书库 p.N.`
   —— EHC 240 各章的**物理页 = 书内印刷页 + 1**（物理 p.48 ＝ 书内 5-47）。
2. **MDPI 专著**：`书名. MDPI, 年份. 公共知识/书库 p.N.`（N 为 PDF 物理页码，`read_page.py` 可复现）。
3. **OA 文献**：`作者/机构. 题名. 期刊 年份. DOI / PMCID.`——**给 §章节而非页码**（OA 全文无统一页码，给页码等于伪造）。
4. 版本/限量类数值（GB、SANTE、(EU) 法规、OECD TG、ICH M7）**以官方现行文本为准**；**本库已收录 ICH M7(R2)（2023 Step 4 final）与 SANTE/11312/2021 v2026（2025）现行文本**（`guides/`），可直接按物理页取证；其余仍只提供方法学锚点与复核入口。

## 五、维护约定

- 新增书目：编辑 `sources_*.json`（离题条目须在构建前剔除，例：已剔除 *Temporal Resolution…*（实为遥感/地学））。
- 已知坑：
  - **MDPI slug 规则**：连字符/破折号/斜杠等标点**直接删除**，仅空白转 `_`（`Chromatography–Mass` → `ChromatographyMass`）；`kind` 可为 `book|reprint|topic`；斜体物种名会残留 `em`（如 `of_emListeria_monocytogenesem_in_Foods`）。失败时把实测 URL 写入该条目的 `pdf_url`。
  - **代理**：`curl`/`urllib` 须 `--noproxy '*'` 或 `env -u http_proxy -u https_proxy -u all_proxy`。
  - **webfetch 工具在本环境全量 `Transport error`**：取料一律走 shell + REST（Crossref / EuropePMC / OpenAlex / cdn.who.int / mdpi-res）。
  - 阻塞源：`mdpi.com`、`efsa.onlinelibrary.wiley.com`、`www.epa.gov` PDF、`iris.who.int`、`openknowledge.fao.org` API → 403/404，请改用上述可用端点。
  - 扫描件 PDF 抽不出文本（WHO 有 4 篇需 OCR）。
- 变更须记 `EVOLUTION.md` 一行（类型 `reference`）。
