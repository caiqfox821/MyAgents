# 公共知识 · 书库建设 —— 进度记录（跨会话续作）

> 任务目标（用户）：从网上获取电子书/论文/技术指南，整理到 **L3 颗粒度（逐条含出处 + 页码/PMCID）**，完善公共技能 `risk-assessment`，知识入公共库，并增强**毒理专家**与**质谱专家**。

---

## 会话 2（2026-10-22）· 已完成

### 1. 取料通道（实测可用）
| 通道 | 端点 | 产出 |
|---|---|---|
| WHO 权威指南 | `cdn.who.int/media/docs/default-source/food-safety/publications/*.pdf` | **4 个 EHC 240（2020 更新）章节**：Ch5 116 页、Ch6 177 页、§4.5 122 页、§9.1.4.2 27 页 |
| MDPI Books | `api.crossref.org`（type:book, prefix:10.3390）→ `mdpi-res.com/bookfiles/{kind}/{id}/{slug}.pdf` | **19 册**（分析/质谱/毒理/风险评估/农残/真菌毒素/QMRA 等） |
| EuropePMC OA | `www.ebi.ac.uk/europepmc/webservices/rest/search?query=…+OPEN_ACCESS:Y` → `/PMCxxx/fullTextXML` | **73 篇**全文 → 会话 3 增 **3 篇＝76 篇**（**PMC12332500** MOE《Statement》、**PMC7500704/PMC7734868** ICH M7 (Q)SAR；主题计数 guides 35 / tox 16 / risk 14 / ms 14）→ 会话 3 增 **PMC12332500**＝**74 篇**（guides 33），JATS XML + txt |

### 2. 库结构（`公共知识/书库/`，454 MB）
`guides/ mdpi/ papers/{xml,txt} text/{guides,mdpi} toc/{guides,mdpi} tools/ catalog.json(25 条/4418 页) INDEX.md README.md sources_*.json seed_guides.json`

### 3. 工具（`tools/`）
- `discover_mdpi.py` / `curate_mdpi.py`（REQUIRE/BLOCK 两级 + 主题配额，20 册入选）
- `build_booklib.py`（下载→完整性校验→抽取→目录→编目；**已修正 MDPI slug 规则**）
- `search_books.py` / `read_page.py`（全库检索与按物理页取证，所有条目的页码由此产生）
- `fetch_papers.py`（4 主题 + 40 组 `TITLE:"…"` 精确检索；**增量落盘**、年份/INDEX 生成已加固）
- `discover_guides.py`（OpenAlex 路线，命中 0，**已放弃**）

### 4. 交付物（三份 L3 条目文件，会话 4 末共 **248 条**（78+98+72）→ 会话 5 末 **253 条**（78+102+73）；食品加工另有 **35 行**）
| 文件 | 节/条 | 覆盖 |
|---|---|---|
| `公共知识/技术指南/风险评估-证据条目与出处.md` | 8 节 / **78 条** | HBGV-POD-BMR、膳食暴露与 IESTI/VF/删失、TTC/MOE、EFSA 不确定性、风险表征工作例（含 **QMRA 分支 5-8～5-12**）、iTTC/LTL（**6-8 非致癌 LTL-TTC 112/111/41、6-9 SCT/QT→AET**）、使用纪律（**五条**）、复现清单（条目 1-x…8-x） |
| `毒理专家/references/证据条目与出处.md` | 9 节 / **98 条** | Ch5 UF/BMD、§4.5 遗传毒性与 TTC 树、§9.1.4.2 食用酶数据要求、UF 拆解与个案（cereulide/Hg/CBD/BFR/酶 MOE）、read-across/(Q)SAR/WoE、HTTr/PBPK/ADME、TTC-iTTC-LTL（**排除清单/混合物/QSAR 纪律/基准风险 10⁻⁶↔10⁻⁵/E&L SCT-QT-AET**）、**AOP 与 NAMs 监管接受度**（T-/G-/E-/R-/N-/C-/A-） |
| `质谱专家/references/证据条目与出处.md` | 9 节 / **72 条** | 验证/确证判据、仪器参数与采集（dwell/源参数/TOF 每峰点数）、前处理与基质效应、ID-MS/CRM 不确定度与 **LOD 三法**、HRMS 非靶向与回顾筛查（含 **exposomics 接口 H-9**）、鉴定置信与数据标准、组学、与毒理/暴露接口（**AET 基准纪律 L-5**）（M-/P-/S-/Q-/H-/C-/O-/L-） |

### 5. 技能与规则挂接（注册完成）
- `risk-assessment/SKILL.md`：新增**硬规则 6「先查证据条目，再回原文」**；参考文件表加 **07 原著证据底座** + 书库行 + 三份条目文件分工说明。
- `references/03-剂量反应与健康指导值.md`：§6.1 TTC 表重写（5 层，µg/kg bw·d ↔ 60 kg 折合，含不适用清单/LTL/iTTC/原著页码）；速查表逐行加 `Ch5 p.N｜条目号`。
- `scripts/riskcalc.py`：TTC 阈值注释改为**已核实出处**、新增 `DNA` 层（0.15 µg/人·d）、`--class` 帮助与报错文案、note 指向条目 3-1~3-3；`demo` 与各子命令自测通过。
- `toxicology/SKILL.md`（硬规则 9 + 条目文件行）、`mass-spectrometry/SKILL.md`（新增 §十 证据条目与书库 + 联动段）。
- `毒理专家/references/README.md`、`质谱专家/references/README.md`、`毒理专家/agent.md`、`质谱专家/agent.md`：登记「原著证据条目优先」。
- 根 `README.md`：目录树新增 `书库/` 与 `技术指南/` 的 L3 说明。

### 6. 修复的问题
- **MDPI 6 册下载失败 → 全部修复**：根因是 slug 生成规则错误（MDPI **删除**连字符/破折号/斜杠而非替换为下划线，`kind` 可为 `topic`，斜体物种名残留 `em`）。已写入 `pdf_url` 显式直链并修正 `slug_variants`。
- **离题册剔除**：`Temporal Resolution, a Key Factor in Environmental Risk Assessment 2024`（实为遥感/地学）已从 `sources_mdpi.json` 与库中删除。
- **guides 抓取进程崩溃**（`year` 为 str 时排序 TypeError + tags 缺失 KeyError）→ 脚本加固 + 索引重建（73 条，无孤儿 XML）。

---

## 会话 3（2026-10-23）· 已完成

### 1. 冒烟测试（行为验证）——**双通过**
- `毒理专家`、`质谱专家` 在新会话中被要求"引用页码或 PMCID 作答，无据必须明说"：两份答卷**逐条给 p.N / PMCID**，并在 **4 个问题**上明确写"**书库无此证据**"（分级离子比容差表、QqQ 每峰最少点数、分时段跃迁切分数值、MOE 10 000 标尺）——即"不臆造"规则生效。

### 2. 专家反馈的复核（我先自证，再回写）
| 反馈 | 复核结论 |
|---|---|
| 质谱"p.152 无 TOF 每峰点数" | 原引 **书目错**（`Analytical_Methods…` 仅 135 页）→ 改引 **`Mass_Spectrometry_for_Biomedical…` p.152**：`Points per peak: 3`、`integration time 0.1 s/点`、反应气 H₂ 4 mL/min（**属 ICP-TOF 元素形态语境，不得外推 ESI-QqQ**） |
| 质谱"dwell 各页数值" | 核实 **50 ms（p.57）/ 20 ms（p.58）/ GC-SIM 最优 EE·ES·IS 20 ms 而 DP 100 ms（p.134）**；新书另有 **8 ms + 全套源参数（p.203）/ 150 ms（p.60）/ 50 ms + CAV 4 V（p.124）** |
| 质谱"(EU) 2023/2782 用法" | **适用范围更正**：该法规对象是**霉菌毒素等污染物的抽样与分析方法**（ML 引自 (EU) 915/2023），农残多残留判据归 **SANTE/欧盟农药手册**语境 → 已改写 M-3 |
| 毒理"Listeria p.133 RR 44.7、344 倍" | **页码与数值更正**：RR 44.7 与模型间比 **343.5** 在 **p.132**（表）＋ p.133（正文）；"344 倍"改为 **343.5** |
| PROGRESS 旧记"USEPA 手-口接触频率 室内 3 / 室外 7 次/h" | **书库无此证据**（`events per hour`/`mouth contact frequency` 0 命中）→ **已删除**，仅保留可核的 **SIR 中位数 中国 171.5 / 美国 100 / 加拿大 32.0 mg/d（p.67）** |
| "MOE ≥ 10 000" | **本库未核实**（`text/guides/` 全检 0 命中）→ 改为标注 + 用库内可核口径替代（见下） |
| ICH M7 LTL 五分档（50/15/5/1.5） | （会话 3 当时）**全库无据**；只采信 **PMC13593624 Table I（120/20/10/1.5，仅致突变杂质）** 并标"二手转载、须核 M7(R2) 原文" → **会话 5 已回一级文本结案**：ICH M7(R2) 仅**四档 120/20/10/1.5**（Table 2），"五分档"不存在（见「会话 5」） |

### 3. 回写与新增（三份 L3 + 技能 + 跨专家）
- **公共库**（61 → **72 条**）：`2-21`（TTC 暴露侧四条口径，PMC7009090 §4.2）、`2-22`（SIR 地区差异）、`3-9`（五层阈值＋第 5 百分位 NOAEL×UF100×60 kg＋OP 单列由来）、`3-10`（TTC 适用性两步核查/排除清单/混合物/≥2 独立 (Q)SAR）、`3-11`（**MOE 10 000 本库无据**）、`5-8～5-12`（**QMRA 分支**：模型生态与主导参数、MCSS 概率化、Weibull→Pert、DR 模型选择主导不确定性、概率×剂量同报）、`6-6`（LTL 基准不可互借）；§七 **三条纪律 → 五条**（+通行标尺先核库、+QMRA 不互套）；§八 增"新入库专著/关键 OA 文献"两行。
- **毒理**（79 → **93 条**）：`G-11～G-16`（DNA 反应性致癌物不建 HBGV 用 MOE·Ch5 p.74；步骤 18/19·p.19；致突变 BMD 用于 MOE 的共识条件·p.94；需审批 vs 不可避免·p.11；超 TTC 的不可避免污染物用**体内致突变剂量-反应**推 MOE·**p.93**）；`C-8` 加注"系子集"；`C-10～C-17`（两版排除清单/肼类移出与有机硅新增/混合物 0.0025 适用于总和/≥2 独立 (Q)SAR 与实测优先/法规数据要求互斥/短时限与 <16 周婴儿/**10⁻⁶↔10⁻⁵ 两条推导路径**/M7 LTL 不可照搬）。
- **质谱**（59 → **72 条**）：`M-3` 更正；`M-13`（37 种农药 GC-MS/MS 跃迁＋**每跃迁各配 CE**，Table 1 p.16–19）、`M-14`（**LOD 三法**）、`M-15`（**本库证据边界**：分级 IR 容差/每峰点数/分时段切分**均无据**）；`P-11～P-13`（dwell 逐化合物优化、8/50/100/150 ms 与 ICP-TOF 每峰 3 点、Q-OTFT 靶向 MS² res 15,000＋dMRM）；`S-8～S-10`（传统萃取四通病与通量权衡、绿色萃取/MIP 模板-单体、HS 降基质）；`Q-9`（**验证框架按用途选**：ICH M10 / SANTE / ICP-MS+CRM）、`Q-10`（七点 1/x 加权排除零点＋低中高三水平）；`H-9`（**exposomics→毒理接口**，非靶向不得止步特征峰）；`L-5`（**AET 三条口径纪律**）；§九 补 3 本新书与 PMC7009090/13379458/12175843。
- **食品加工**（+**9 行**，现 35 行）：§二 混合干燥（**超声 +13% / 微波 +112% / 微波＋超声 +140%，微波降能耗 30%**，p.79/p.11）；§三 HPP vs 热处理定量对照（**600 MPa/4 min：2.37/2.35 log vs 未处理 6.78/6.91**；**油含量只影响热处理侧**，p.98）、氧化指标与统计设计（**POV/p-AV < 10 meq/kg oil**、p-AV 公式、三重平行＋ANOVA/Duncan）、500 MPa 与 6000 bar 与**干酪冷藏回升**（p.103）、罗勒萜类干扰归因（p.103）；§六 **ASLT 判据 1000 cfu/mL＋各温度天数表**（4 ℃ 48.31 d … 40 ℃ 约 3 d，p.28–29）、**感官货架期的生存分析**（504 样/72 消费者/155 failures，KM：10 ℃ 11.9 d、20 ℃ 5.3 d；50–200 人下限；按拒绝率反算，p.38–50）、**双终点纪律**（感官早于微生物约 3 d；+10 ℃ 感官货架期约减半；4VG，p.11/47/51）。
- **技能与脚本**：`references/03` §五 MOE 段重写（10 000 标"本库未核实"＋**五条本库可核口径**）与速查行加注；`references/04` 判据表 MOE 行、§1.3 增"本库可核 MOE 依据"、§1.4 分级表下增 **QMRA 不与化学档位相加**；`scripts/riskcalc.py calc_moe` 三档文案加※标注，`moe`/`demo` 自测通过（Python 3.7）。
- **评估闭环**：`evals/质谱专家/MASS-001-mrm-method-validation.md` 录入首跑（**13/14 ≈ 92.9%，通过**，无红线；唯一扣分＝(EU) 2023/2782 适用范围误引 → 已固化进 M-3/M-15）；`evals/registry.md` 状态 未评 → **通过**。

---

### 7. 会话 3 追加（同日）· **一级权威文本缺口 ① 已补齐**

- **EFSA 科学委员会《Statement on the use and interpretation of the margin of exposure approach》**（*EFSA Journal* **2025;23(8):e9606**，DOI 10.2903/j.efsa.2025.9606，PMID 40786114，CC BY-ND 4.0）经 **EuropePMC OA** 取得全文并入库：`papers/xml/PMC12332500.xml` + `papers/txt/PMC12332500.txt`（**343 段 / 7 999 词**），`papers/index.json` 与 `INDEX.md` 已登记（**74 篇**，guides 33；顺带修掉 `INDEX.md` 头部遗留的未替换 `%d`）。
- **结论：`MOE ≥ 10 000` 不再是"本库无据"**，且原文给出的是**有条件**的口径：①**RP 必须是动物研究 BMDL₁₀**；②10 000 ＝ **100（种间＋种内）× 100**（细胞周期调控与 DNA 修复的人间变异 ＋ RP 类型与 RP 以下剂量-效应关系未知）；③含义是 **low concern ＝ 风险管理优先级低**，**不是"无害"**，且**不排除为减少暴露而采取措施**；④**MOE 不直接等同风险**；⑤措辞体系 `concern`/`low concern`/`no concern` 由本文件正式定义，**定义自发布之日生效**，而 **ToR2（全面修订 2005 意见的指南）尚未出台** ⇒ 引用须写"EFSA SC 2025 Statement"，不得写"EFSA 2005"或笼统的"现行 EFSA 意见"。
- **回写完成**：公共库 **3-11 重写 + 新增 3-12/3-13**（72 → **74 条**）、§七 第 4 条纪律改为"引用必须带条件"、§八 加行（74 篇）；毒理 **新增 G-17/G-18**（93 → **95 条**）；`references/03` §五**整节重写**（官方判读表＋四条必带口径＋出处写法）、公式块加"⚠️ 仅 BMDL₁₀ 适用"、速查行改写；`references/04` 判据表 1.1、§1.3（三条新要点）、**§1.4 分级表新增"关切低（官方口径）"档**并改写两条注；`SKILL.md`、`templates/风险评估报告模板.md`、`riskcalc.py calc_moe` 三档文案、`毒理专家/references/02·03` 两处速查全部同步。脚本 `moe --pod 100 --exp 0.008/0.05/0.5` 三档自测通过（Python 3.7）。
- **环境要点（务必记住）**：EuropePMC REST **只走 https**——`http://` 请求返回非 JSON 而静默失败（本会话第一次尝试即因此报错）；`resultType=lite` 中 EFSA Journal 的 `journalTitle` 是 **"EFSA J"**，用 `JOURNAL:"EFSA Journal"` 会漏检。
- **可复用检索式**（已验证命中）：`"MOE of 10,000" AND OPEN_ACCESS:Y`（145 命中）、`"of 10,000" AND MOE AND JOURNAL:"EFSA J" AND OPEN_ACCESS:Y`（155 命中，`PMC12332500` 居首）。

### 8. 会话 3 追加②·ICH M7 (Q)SAR 两篇方法学论文入库并条目化

- **新入库**（`papers/xml·txt`，`index.json`/`INDEX.md` → **76 篇**）：**PMC7500704**（Amberg et al. 2019, *RTP* **102**:53-64, DOI 10.1016/j.yrtph.2018.12.007，**94 段/8 979 词**，NIHMS 作者稿）与 **PMC7734868**（2020, *RTP* **118**:104807, DOI 10.1016/j.yrtph.2020.104807，**76 段/12 123 词**）。
- **两处踩坑并修复**：①`index.json` 新条目**漏 `pmcid` 键**（重建 INDEX/去重依赖它）⇒ 已从 `xml` 路径回填；②DOI **不可按文章号猜**（原写 …104591，实为 **…104807**）⇒ 须用 `resultType=core` 回查；③JATS 段落抽取须用 `<p[^>]*>`/`<title[^>]*>`（只写 `<p>` 会只剩 219 词）。
- **成条**：公共库 **3-14**（双系统构成与"无结构警示"合并、**OOD/indeterminate** 定义、**expert review 两种适用情形**、规则型 indeterminate 组合 Ames 阳性率 **11.8%**／统计型 positive 组合 **27.7%**、两系统一致 clear negative **仍含实验阳性**）、公共库 **6-7**（**1.5 µg/day ＝ 1 in 100,000、慢性 >10 年档**第二出处）、毒理 **C-18**（版本漂移：8,556→11,461→13,514、GT_EXPERT 125→174→198、GT1_A7B→GT1_BMUT；**negative→positive 累计 <5%**；官方口径＝不必每次重跑，**但申报上市/确定商业化合成路线时须复核原始预测**）、毒理 **C-19**（**consensus 五条合并规则**，**OOD 绝不计为阴性**）。`references/03` 的 (Q)SAR 行同步补纪律。
- **未决**：PMC7500704 中 **"94%"（Dobo 2012 pre-expert review performance）的确切定义须回正式出版版核**（现据 NIHMS 作者稿）；**ICH M7(R2) 原文与现行 SANTE 文本仍在 EuropePMC 无命中**（检 `TITLE:"ICH M7"` 只中二次方法学论文，检 `"Analytical Quality Assessment…"`/`"SANTE" AND "12682"` 均 0 命中）⇒ 条目维持"须核原文"。
- **顺带**：`papers/INDEX.md` 头部遗留未替换的 `%d` 已修；`EVOLUTION.md` 日志表**中段空行**造成的无表头断表已接回。三份 L3 **241 → 245 条**（76/97/72）。

### 9. 会话 3 追加③·food-safety 侧的"欧盟法规语境"更正已同步（原待办 6）

`(EU) 2023/2782`（霉菌毒素/污染物**抽样与分析方法**）与农残多残留判据（**SANTE 语境**）的分工，除质谱 **M-3** 外，现另落三处：`食品安全专家/skills/food-safety/SKILL.md`（关键标准下的"涉外勿混引"条）、`references/化学危害-食品安全.md`（使用提示第 **4** 条："限量法规"vs"方法/抽样法规"两套文件）、`references/国际机构与数据库.md` §5.3（ML 取自 **(EU) 915/2023**；⚠️ 两部欧盟原文本库未取得，须核 EUR-Lex）。

---

## 会话 4（2026-10-23）· 已完成（接着会话 3 中断点）

### 1. 医疗器械/药品 E&L 两条阈值链入库并条目化（PMC12175843 / PMC13593624 的原文数值）

- **公共库新增 6-8（非致癌 LTL-TTC 三档）**：**112 µg/kg bw/d（≤1–30 d）、111（31–365 d）、41（≥366 d）**；推导＝**最低第 5 百分位 NOAEL ÷ MF 100**（种间 10×种内 10，对齐 **ISO 10993-17:2023** 时程框架）；**纳入 DART 研究（38%）** ⇒ 兼护发育/生殖终点；**三档不按 Cramer 分列**（Munro 30/9/1.5 仅对应 ≥366 d 档）；**不适用**高效力物质（<0.025 µg/kg bw/d 或 60 kg 1.5 µg/d）与遗传毒性/排除类别；与**因子外推**（Buist 2016 农药 ×3、Bercu & Dolan 2012 药品 ×10）的**区别**在"直接从亚急性/亚慢性实测推导"。
- **公共库新增 6-9（SCT/QT → AET 与给药量放大）＋ 毒理新增 C-20（同主题毒理接口）**：**SCT 0.15 µg/day / QT 5 µg/day**（PQRI 2006，OINDP）；AET 由 SCT 换算、作报告阈值（**USP 〈1664〉**）；**给药量放大**——同 SCT 5 µg/day 下 **1000 mL/day → AET 5 ng/mL vs 10 mL/day → 500 ng/mL**（LOQ 须低 100 倍）；药品语境可上调档 **120 µg/day（细胞毒抗癌药）**、**50 µg/day（1750 mL/day 实例）**；**ICH Q3E 草案在途**、ICH Q3B 阈值 5/50 µg/day。**纪律**：120/50 属 **SCT（患者日暴露）**，**≠ ICH M7 Class 1–5 的 LTL 分档**（50/15/5/1.5 全库无据，见 6-6/C-17）。
- **回写**：`公共知识/技术指南/风险评估-证据条目与出处.md`（§六 +2 条、§八 加 PMC13593624）、`毒理专家/references/证据条目与出处.md`（§七 +C-20、§九 书库登记）；计数 **公共库 76→78、毒理 97→98、质谱 72，三份合计 245→248**；`公共知识/README.md`、`毒理专家/references/README.md`、本文件均已同步。
- **原文核验要点**：三档数值与"是否按 Cramer 分列"的结论来自资料与方法节原文（`§Results`/`Table 4`），**已排除"按 Cramer 再分档"的误读**；PMC13593624 的 120/50 µg/day 原句为 **SCT 档位**（非五分档），已在条目内加⚠️禁止混用。

---

## 会话 5（2026-10-23）· 已完成（缺口 ②③ 补齐：ICH M7(R2) 与 SANTE 现行文本入库并条目化）

### 1. 取料（直连绕代理，命中"文档下载 URL"而非栏目页）

- **ICH M7(R2)**：`database.ich.org/sites/default/files/ICH_M7%28R2%29_Guideline_Step4_2023_0216.pdf`（**Step 4 final，2023-04-03 采纳**，32 页；FDA 镜像 `fda.gov/media/170461/download`）。**坑**：栏目页 `ich.org/page/mutagenic-impurities`、`ema.europa.eu/en/documents/...` 会返反爬页（`<title>Sorry - <id>`）。
- **SANTE**：现行版＝ **SANTE/11312/2021 v2026**（**2025-11-25 发布、2026-01-01 实施**，取代 **v2 与 12682/2019**，58 页）——`food.ec.europa.eu/document/download/d4786faf-c574-4222-a5c6-45086b3920b8_en?filename=pesticides_mrl_guidelines_wrkdoc_2021-11312.pdf`；EURL 镜像 `SANTE-11312_2021-V2.pdf` 系 **v2（非 v2026）**，勿混。
- **入库**：`书库/guides/{ICH_M7R2_Guideline_Step4_2023,SANTE_11312_2021_v2026}.pdf` ＋ `text/guides/…txt`；登记 `catalog.json`（**23→25 条 / 4,328→4,418 页**）、`seed_guides.json`（4→6）、`INDEX.md`、`README.md`。目录列给"—"（未生成 toc）。

### 2. 一级文本核出的关键数值（已写入条目）

- **ICH M7(R2)**：**§7.1**（p.11）TTC **1.5 µg/person/day** ↔ 理论超额终生癌症风险 **<1/100,000**；**Table 2**（p.13）单杂质 AI **四档 120/20/10/1.5 µg/day** ⇒ **证实"五分档 50/15/5/1.5"在一级文本中不存在**（此前的"误传"标注得到定性结论）；**Table 3**（p.13–14）多杂质（≥3 个 Class 2/3）总摄入量 **120/60/30/5 µg/day**；**§7.2.2**（p.12）化合物特异 AI 放宽取"Table 2 同比例"与"**≤最大日剂量 0.5%**"之低（15→100/200/1200；100 mg 则 <1 月取 500）；**§7.3.1**（p.13）临床期**双基准**（早期 10⁻⁶／后期 10⁻⁵）＋ Phase 1 ≤14 d 替代法；**§7.5**（p.14）cohort of concern（aflatoxin-like / N-nitroso / alkyl-azoxy）与个案放宽。
- **SANTE v2026**：**D2**（p.15）RT 容差 **±0.1 min**（GC/LC 同）；**Table 3**（p.16）鉴定最少离子数 **3（单 MS）/ 2 产物离子（单位分辨 MS/MS）/ 2 离子 ≤5 ppm（HRMS，m/z<200 时 <1 mDa）**；**D11**（p.17）单位分辨 MS/MS 离子比 **±30%（相对）**；**D12**（p.17）**HRMS 无通用离子比容差值**。⇒ 库内**否定性条目 M-15** 的结论被现行原文坐实（无"分级离子比容差表"、无"每峰点数"判据）。

### 3. 回写（条目与计数）

- **质谱（72→73）**：**新增 M-16**（SANTE v2026 鉴定判据全表）；重写 **M-1**（MRM 最小要求升级到一级文本 D11/Table 3）、**M-12**（补 v2026 版本与"版本号纪律"）、**M-15**（否定性核查改以现行原文坐实）；改 **L-2**（ICH M7(R2) Table 2/Table 3）、**L-5②**（五分档定性为"一级文本不存在"）；§九 登记两册。
- **毒理（98→102）**：**新增 C-21**（多杂质总量 Table 3）、**C-22**（化合物特异 AI 放宽 ＋ 0.5% 上限）、**C-23**（临床双基准与 Phase 1 替代）、**C-24**（cohort of concern 与个案放宽）；**C-17** 出处由"二手转载、须核原文"改为"**一级文本已核**（Table 2/§7.1）"；**C-20** 尾注"ICH M7(R2) 仍未取得"→"已取得"。
- **公共库（78，条数不变）**：**6-6** 出处升级为一级文本并把"五分档误传"写实；**6-9** 纪律句同步；§七 第 4 条补"分档表已核"；§八 登记两册、catalog 计数改 **25 条 / 4,418 页**。
- **计数**：三份 L3 **248 → 253 条**（公共库 78、毒理 102、质谱 73）。

---

## 会话 6（2026-10-23）· 已完成（**扩库**：论文 +100、机构指南 +11、MDPI 专著 +5；并补条目）

### 1. 扩库（三通道；扩的是**检索式**而非抬配额）

- **论文**：`fetch_papers.py` 新增 ~48 组检索式（PFAS/微塑料/MOSH-MOAH/食品接触材料/硝酸盐-亚硝酸盐/丙烯酰胺/HBM4EU/高氯酸盐/铝/甲基汞/镉；DNT/免疫毒性/IVIVE/毒理基因组学/EDC 低剂量/IARC/植物药/混合物；PFAS LC-MS/MS、Py-GC-MS、GC×GC、离子迁移、DIA、单细胞蛋白组、代谢组报告规范、形态分析、同位素、草甘膦、真菌毒素生物标志）→ `--per-theme 25`：**papers 76 → 176**（guides 60 / tox 41 / risk 39 / ms 39）。日志 `/tmp/opencode/fetch_papers_s6.log`。
- **MDPI 专著**：`discover_mdpi.py` 新增 ~48 组查询（含 URL 解码）→ 原始候选 **819 → 1359**；`pick_new_mdpi.py`（复用 `curate_mdpi.py` 两级过滤）仅 **7 本**通过，从中取 **5 册**：13096 微波/超声辅助萃取（2026）、9761 时间分辨率（2024）、9858 环境暴露/生物监测（2024）、9982 抗球虫药与新兴污染物（2024）、11364 天然产物生物活性与分子机制（2025）→ `sources_mdpi.json` **19 → 24**。
- **机构指南**：`discover_guides.py` 新增 16 组检索式（OpenAlex + `curl` 可达性核实）→ `sources_guides.json` **11 条**：4 册 MDPI（食品化学污染物分析 2020 / 真菌毒素 LC-MS/MS 2017 / 丙烯酰胺 2021 / 纳米材料毒性 2023）＋ 7 份 OECD（GLP-IT 安全 2024、GLP-ISO/IEC 17025 2016、DNT 数据评价 2023、体外免疫毒性 DRP 2022、职业生物监测 2022、人造纳米材料风险 2022、组织病理内分泌/生殖 2009）。
- **重建**：`build_booklib.py` 增量（**一次传全部三个 manifest**）→ guides **6 → 17**、mdpi **19 → 24**、**catalog 25 → 41 条 / 4,418 → 7,407 页**（**815 MB**）；11 份新指南 PDF + `text/guides/*.txt` 齐备，`search_books.py` 可检索；生成器机构标题补全为「WHO/FAO/EFSA/EPA/IPCS/ICH/EC/OECD」。

### 2. 新条目（三份 L3 **253 → 258 条**）

- **毒理 102 → 104**：**A-8**（OECD 体外免疫毒性 DRP 2022：无 OECD TG，分层 **Tier1 骨髓毒性 → Tier2 白细胞毒性 → Tier3 功能试验**，MITA；p.6/p.9）、**A-9**（OECD DNT IVB 2023：**476 种**做过 ≥1 试验/**81 种**做遍，**阴性 ≠ 无 DNT 危害**、未按 GD 34 经典验证、文件 evergreen；p.7）。
- **质谱 73 → 74**：**M-17**（多类真菌毒素 LC-MS/MS：免疫化学筛查 vs 质谱确证；**EC 401/2006 回收 60%–120%**、AOAC 70%–125%；LOD/LOQ = S/N 3/10、ISO 11843-2；13 毒素谷物 LOQ **0.4–54.8 ng/g**；QuEChERS 与净化差异）。
- **公共库 78 → 80**：新增 **§七 职业暴露生物监测与纳米材料风险评估**——**6-10**（OECD 职业生物监测 2022，ENV/CBC/MONO(2022)37 / Series No.370：德 34%↔12%、瑞 38%↔12%、国际 **<1%**；OBL 四法 refined/ROBL/TOBL/POBL；暴露/效应 BM 分层）、**6-11**（OECD 人造纳米材料 2022，ENV/CBC/MONO(2022)3：四步 + NRC2009 问题形成；理化表征/溶解动力学/团聚/dosimetry/分组 read-across/nanoinformatics；参考材料库与统一报告标准）；原 §七/§八 顺延为 §八/§九。

### 3. 计数同步

- 三份 L3 **253 → 258**（公共库 78→**80**、毒理 102→**104**、质谱 73→**74**）；papers **176**；书库 **41 条 / 7,407 页 / 815 MB**（24 MDPI + 17 guides）。
- 已同步：`公共知识/README.md`、`书库/README.md`、`书库/INDEX.md`（生成器重建）、三份 `references/README.md`、本文件、`EVOLUTION.md`、`tobedone.md`。

### 4. 坑与纪律

- `discover_mdpi.py` **忽略 argv**（曾用 `--help` 将 raw 清 0，重跑复原）；`pick_new_mdpi.py` 复用 `curate_mdpi.py` 的 OBJ/METHOD/BLOCK。
- `build_booklib.py` 由**传入 manifest 的并集**重建 `catalog.json`/`INDEX.md`/`toc/`——**必须一次传全部三个 manifest**，否则丢书目；生成器重跑会覆盖 `INDEX.md` 的手工改动，定制须改生成器。

---

## 待办（下一会话）

1. ~~**一级权威文本剩余两处**~~ → **全部补齐**（会话 5：② **ICH M7(R2)** Step 4 final 原文；③ **SANTE/11312/2021 v2026** 现行本；均已入库并条目化，见「会话 5」）。至此三处一级文本缺口 ①②③ 全部回原文。
2. **新书配额外扩消化**：`Sample Preparation Quo Vadis`（189 页，仅取 4 处）、`Chromatography–Mass Spectrometry…`（307 页，8 处）、`QMRA of L. monocytogenes in Foods`（219 页，5 处）→ 目标每册 10–15 条，优先**可执行参数**（回收率/净化组合/池温/DR 模型参数）。
3. **跨库索引统一**：`食品加工/营养/发酵…` 各自仍用私有 `references/books/`，与 `公共知识/书库/` 并存 → 在 `公共知识/README.md` 增"分区书库对照表"（哪个主题在哪库、检索命令各是什么）。
4. `公共技能/skills/risk-assessment/references/06-跨域适用与边界.md` 补 **QMRA 分支**一行（指向条目 5-8～5-12 与 §七 第 5 条纪律）；`references/02` 可补 `2-21`（TTC 暴露口径）与 `2-22`（暴露参数来源）。
5. WHO 扫描件 4 篇需 OCR（营养库历史问题）。
6. ~~**食品安全侧**：`(EU) 2782/2023` 更正后的农残—污染物**双语境**尚未同步~~ → **已完成**（见 §9：`food-safety/SKILL.md`、`化学危害-食品安全.md` 使用提示 4、`国际机构与数据库.md` §5.3）。
7. **回原文再核两处**：①PMC7500704 里 **Dobo 2012 的"94%"确切定义**（现据 NIHMS 作者稿，须核 *Regul Toxicol Pharmacol* 正式出版版）；②条目 3-14/6-7/C-18/C-19 中的**卷页与 DOI 已核 EuropePMC core 记录**，但两文均属作者稿/出版版差异须留意（PMC7500704 带 `pmc-prop-manuscript yes`）。
8. ~~**换入口试一级文本**~~ → **已达成**（会话 5）。**实测入口**：**ICH M7(R2)** = `database.ich.org/sites/default/files/ICH_M7%28R2%29_Guideline_Step4_2023_0216.pdf`（栏目页 `ich.org`/`ema.europa.eu` 会返反爬页）；**SANTE** = `food.ec.europa.eu/document/download/…_en?filename=pesticides_mrl_guidelines_wrkdoc_2021-11312.pdf`（须用**文档下载 URL**，栏目页会被拦）。

## 会话 2 遗留待办的处置结果

1. ~~新书未消化条目待写入~~ → **已全部写入**（见会话 3 §3），并修正其中 **4 处页码/数值误标**（Listeria p.132–133 与 343.5；TOF p.152 书目；(EU) 2782/2023 适用范围；手-口接触频率**书库无据已删除**）。
2. ~~WHO 扫描件 OCR~~ 未做（待办 5）。
3. ~~`公共知识/README.md` 索引~~ 已建；**条目计数已按 72/93/72 校正**。
4. ~~冒烟测试~~ **已发起并完成**（会话 3 §1）。

## 命令备忘

```bash
cd 公共知识/书库
env -u http_proxy -u https_proxy -u all_proxy python3 tools/build_booklib.py . \
    sources_mdpi.json seed_guides.json sources_guides.json            # 合并重建 catalog/INDEX/toc
env -u http_proxy -u https_proxy -u all_proxy python3 tools/fetch_papers.py --theme guides --per-theme 20
python3 tools/search_books.py "dwell time" --context 1                # 取证：书|物理页|原文
python3 tools/read_page.py WHO_EHC240_Ch5 48
```
- **本环境 `webfetch` 工具全量 `Transport error`**，取料一律 shell + REST（须 `--noproxy '*'` 或 `env -u *_proxy`）。
- 阻塞源（403/404）：`mdpi.com`（含 `/books/pdfview/`）、`efsa.onlinelibrary.wiley.com`、`www.epa.gov` PDF、`iris.who.int`、`openknowledge.fao.org` API。
- 可用：`api.crossref.org`、`www.ebi.ac.uk/europepmc/...`、`cdn.who.int`、`mdpi-res.com`、`api.openalex.org`（须 `filter=is_oa:true`）。
- Python 3.7（禁 `:=`）；长任务用 `background:true`。

## 已知问题

- `sources_guides.json`（指南发现）**会话 6 起已启用**（11 条：4 册 MDPI + 7 份 OECD）；`seed_guides.json` 仍以显式 `pdf_url` 直接入库。
- `catalog.json` 不保留 `themes`（仅 `tags`）；主题级检索请用 `papers/index.json` 与三份条目文件。
