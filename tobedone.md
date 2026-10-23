# 续作存档 · 公共书库 / 风险评估 / 毒理 / 质谱 证据建设

> **存档时间**：2026-10-23（**会话 6 末**；会话 3 中断点及会话 4/5/6 目标均已完成，见 §二、§二·补、§二·补·6）
> **用途**：下次直接从这里接手。所有已核事实带出处；**未核事项一律标"须核原文"，不得当证据引用**。
> **环境**：目录**非 git 仓库**（改动无提交状态）；Python **3.7**（禁 `:=`）；curl/urllib 须 `--noproxy '*'` 或 `env -u http_proxy -u https_proxy -u all_proxy`；只有 `pdftotext/pdfinfo`。

---

## 一、总目标（长期）

从网上取**电子书 / 论文 / 技术指南**，消化成 **L3 颗粒度条目**（结论一条 ＋ 出处 ＋ 页码或 PMCID/章节），完善公共技能 `risk-assessment`，知识入 `公共知识/`，并同步增强**毒理专家**与**质谱专家**（含冒烟测试反馈闭环）。

**体例要求（与既有各专家 `references/证据条目与出处.md` 同构）**
- 条目：结论 ＋ 关键数值 ＋ **适用条件/边界** ＋ 出处（`书库 p.N` 或 `PMCID §章节`）。
- **不臆造**：取不到原文就说"书库无此证据"，并给官方复核入口。
- **页码约定**：EHC 240 物理页 ＝ 印刷页 ＋ 1；MDPI 给 PDF 物理页；OA 文献只给 §章节（无页码）。
- **来源标注**：WHO CDN / MDPI Books（CC BY 4.0）/ EuropePMC OA，分别注明。
- 用户曾要求用 `webfetch` 取料：**实测 webfetch 全部 `Transport error`**，已改用 curl/urllib ＋ EuropePMC/OpenAlex/Crossref REST（交付说明已如实标注）。
- 默认**不建独立"风险评估"agent**（方法而非领域）；风险评估知识走公共库＋公共技能。

---

## 二、本轮（会话 3）**已完成**

### 1. 一级权威文本缺口 ① 已补齐（本会话最大成果）

**`MOE ≥ 10 000` 由"本库无据" → "已核实原文"**。

- 取到 **EFSA 科学委员会《Statement on the use and interpretation of the margin of exposure approach》** ＝ **PMC12332500**，*EFSA Journal* **2025;23(8):e9606**，DOI **10.2903/j.efsa.2025.9606**，PMID **40786114**，CC BY-ND 4.0，EFSA-2025-0409。
  入库：`公共知识/书库/papers/xml/PMC12332500.xml` ＋ `txt/PMC12332500.txt`（**343 段 / 7 999 词**）。
- **原文口径（写作时必须带条件）**：
  1. **"in general a margin of exposure of 10,000 or higher, *if it is based on the BMDL₁₀ from an animal study*, and considering overall uncertainties in the interpretation, would be of low concern from a public health point of view and might be reasonably considered as a low priority for risk management actions."**
  2. **判定最终属风险管理**；**如此量级的 MOE 不排除为减少人体暴露而采取措施**。
  3. **10 000 ＝ 100 × 100**：第一个 100 覆盖 **(i) 种间外推＋种内（人际）变异**（与非致突变物质同源）；第二个 100 覆盖 **(ii) 细胞周期调控与 DNA 修复的人间变异** ＋ **(iii) RP 类型（BMDL₁₀ 或 T25）与 RP 以下剂量-效应关系、无增加剂量阈值未知** ⇒ **换 T25/NOAEL/LOAEL 即不得套用 10 000**。
  4. **"the MOE does not directly equate to risk"**，用于**优先排序**与公众沟通；**< 10 000 关切更高、> 10 000 关切更低**（除非 RP 以下剂量-反应曲线的详细知识另有指示）。
  5. **措辞官方定义（§Conclusions 原文）**：MOE 用于**"不宜推导 HBGV"时**评估关切；**`'concern'`（人/动物）＝需要风险管理者采取行动**；人侧 **`'low concern'`** 限**具"直接 DNA 反应性致癌潜能"**的物质＝风险管理优先级较低；**其他物质**依 MOE 大小可结论"在估计暴露下不引起人体健康安全性关切"；动物侧 **`'no concern'`**；植物源饲料添加剂长寿命靶动物 `'low concern'` ＝ **`'very unlikely'`**。
  6. **MOE 与 MOS 不得混用**（MOS ＝ HBGV/暴露，化妆品/药品/兽药）；**定义自发布之日生效**；**ToR2（全面修订 2005 意见的指南）尚未出台** ⇒ 引用写 **"EFSA SC 2025 Statement"**，**不要**写"EFSA 2005"或笼统"现行 EFSA 意见"。
- **本库既有口径不被取代，须并列报告**：Ch5 **p.74**（MOE 系相对比较）；个案 **≥1500 / ≥300**（PMC13403159）；食品用酶 **≥385 / ≥633**（PMC13624930、PMC13352140）；§4.5 **p.93**（缺致癌数据→体内致突变剂量-反应推 MOE）。
- **1 000 / 100 两档明确为管理约定**（EFSA 只定义 10 000）。

**回写完成（全链路一致）**：公共库 **3-11 重写 ＋ 新增 3-12/3-13**、§七 第 4 条纪律改为"**引用必须带条件**"、§八 登记；毒理 **新增 G-17/G-18**；`references/03` §五**整节重写**（官方判读表＋四条必带口径＋出处写法）＋公式块 ⚠️＋速查行；`references/04` 1.1 判据表 / §1.3 三条新要点 / **§1.4 新增"关切低（官方口径）"档**＋两条注；`SKILL.md`；`templates/风险评估报告模板.md`；`riskcalc.py calc_moe` 三档文案（**自测通过**：`moe --pod 100 --exp 0.008/0.05/0.5`）；`毒理专家/references/02:225`、`03:83` 由"非本库核实"改为已核实。

### 2. ICH M7 (Q)SAR 两篇方法学论文入库并成条

| PMCID | 文献 | 段落/词数 |
|---|---|---|
| **PMC7500704** | Amberg et al. 2019, *Regul Toxicol Pharmacol* **102**:53-64, DOI 10.1016/j.yrtph.2018.12.007（**NIHMS 作者稿**） | 94 / 8 979 |
| **PMC7734868** | 2020, *RTP* **118**:104807, DOI **10.1016/j.yrtph.2020.104807** | 76 / 12 123 |

已成条：
- **公共库 3-14**：(Q)SAR **双系统构成**＝expert rule-based ＋ statistical-based，按**"absence of structural alerts"**合并，**两系统均无警示才判非致突变**；**OOD**＝结构落在训练/参考集之外（他称 not-in-domain）；**indeterminate**＝取代基对警示基团反应性影响未阐明→证据冲突（他称 equivocal）；**expert review 的两种法定情形**＝结果不确定（indeterminate/OOD）或有正当理由推翻/驳斥预测；量化：**规则型 indeterminate 组合 Ames 阳性率 11.8%**、**统计型 positive 组合 27.7%**；**两系统一致 clear negative 是最常见情形但仍含实验阳性**（作者与 Dobo 2012 的 **expert review 前 94%** 及 Ames 可重复性同量级 ⇒ **94% 的确切定义须回正式出版版核**）。
- **公共库 6-7**：**TTC ＝ 1.5 µg/day 的第二独立出处**——"分析已知致癌物强度、取**理论超额癌症风险 1 in 100,000（本底之上）**"（Kroes 2004；Muller 2006），**对应慢性（给药 >10 年）暴露**；引用须带"10⁻⁵ 基准"与">10 年档"，**与食品侧 10⁻⁶ 不可互借**，适用域是**药品杂质**。
- **毒理 C-18（模型版本漂移）**：PubChem 筛得 **3367** 化合物跨版本比对；**benchmarking set 8,556 → 11,461 → 13,514**；**GT_EXPERT 125 → 174 规则 → 198 警示**；统计模型 **GT1_A7B(3,979) → GT1_BMUT(13,514)**；新增警示（磺酸卤/酰卤/磺内酯/环状硫酸酯/oxetane/thietane/azetidine/芳基羟肟酸）；⇒ **negative→positive、negative→equivocal 翻转**，**训练集变大后 OOD 减少**（原 OOD 转有效预测）。**但幅度可控**：两模型合并后最大变化方向是 **positive/equivocal→negative 与 negative→equivocal**；**negative→positive 累计占比 <5%**，consensus 合并后更低。**官方结论口径**："此类更新**并不必然要求重跑** (Q)SAR 预测，除非有特定需要；但应在**确定商业化合成路线、提交上市许可时复核原始预测**"。
- **毒理 C-19（consensus 五条合并规则）**：任一 positive → **positive**；任一 equivocal 另一为 negative/OOD → **equivocal**；两负 → **negative**；**一负一 OOD → OOD**；两 OOD → **OOD** ⇒ **OOD 绝不计为阴性**。
- 同步：`references/03` 的 **(Q)SAR 行**补上"区分 OOD 与 indeterminate、两者不得计阴性、合并规则见 3-14/C-19、版本须记录并在申报节点复核（C-18）"。

### 3. food-safety 侧"欧盟法规语境"更正已同步（原待办 ④ **完成**）

- **(EU) 2023/2782 ＝ 霉菌毒素/污染物的抽样与分析方法法规**（其"最大水平 ML"取自 **(EU) 915/2023**）；**蔬果农药多残留**性能判据属 **SANTE 指南/欧盟农药手册**语境。数值近似（回收率 70–120%、RSD ≤ 20%、LOQ ≤ 0.5×限量）但**法规号不得混引**。
- 落三处：`食品安全专家/skills/food-safety/SKILL.md`（关键标准下新增"涉外勿混引"条）、`references/化学危害-食品安全.md`（**使用提示第 4 条**："限量法规" vs "方法/抽样法规"）、`references/国际机构与数据库.md` **§5.3**（含 ⚠️"两部欧盟法规原文本库未取得，对外须核 EUR-Lex"）。质谱侧此前已有 **M-3**。

### 4. 台账与缺陷修复

- **papers**：`index.json`/`INDEX.md` 重建至 **76 篇**（主题计数可交叉：**guides 35 / tox 16 / risk 14 / ms 14**）；顺带修 `INDEX.md` 头部遗留**未替换的 `%d`**；补 2 条**缺失的 `pmcid` 键**；**DOI 回查修正**（PMC7734868 原按文章号猜成 …104591，经 `resultType=core` 核实为 …**104807**）。
- **计数**：三份 L3 **241 → 245 条**（公共库 74→**76**、毒理 95→**97**、质谱 **72**）；`公共知识/README.md`、`书库/README.md`、`毒理专家/references/README.md`、`书库/PROGRESS.md`、`EVOLUTION.md` 均已同步。
- **表格**：`EVOLUTION.md` 日志表**中段空行**（原行 34）造成的无表头断表已接回。`书库/README.md` 行 16 的"竖线 6 ≠ 4"经核是**已转义 `\|`**，属检查脚本**误报**（非缺陷）。
- **书库规模**：`公共知识/书库/` catalog **23 条 / 4,328 页 / 454 MB**（MDPI 19 册 ＋ EHC 240 章节 4 篇）＋ EuropePMC OA **76 篇**。

### 5. 本会话新增的可复用要点（环境/工具）

- **EuropePMC 只走 `https`**：`http://` 返回非 JSON 而**静默失败**（本会话第一次尝试即因此报错）。
- `resultType=lite` 中 EFSA Journal 的 `journalTitle` 是 **"EFSA J"**（写全名 "EFSA Journal" 会漏检）。
- **已验证命中式**：`"MOE of 10,000" AND OPEN_ACCESS:Y`（145）、`"of 10,000" AND MOE AND JOURNAL:"EFSA J" AND OPEN_ACCESS:Y`（155，PMC12332500 居首）、`"MOE of 10,000"` 逗号变体（145）。
- **DOI 勿猜**：用 `search?query=PMCID:PMCxxx&format=json&resultType=core` 回查。
- **JATS 段落抽取**：正则须写 `<p[^>]*>` 与 `<title[^>]*>`（只写 `<p>` 会只剩 219 词）；`index.json` 每条**必须有 `pmcid` 键**。
- `riskcalc.py` 子命令参数是 **`--exp`**；`ttc --exp 0.0001 --class DNA` 与 `moe` 三档均自测通过（3.7 语法 OK）。

---

## 二·补、会话 5 **已完成**（一级权威文本缺口 ②③ 补齐：ICH M7(R2) 与 SANTE v2026）

> 这一步把"须核原文"的两处空档变成**一级文本已核**。

### 1. 取料（直连绕代理；命中的是"文档下载 URL"，不是栏目页）

| 文本 | 现行版本 | 直链 | 页 |
|---|---|---|---|
| **ICH M7(R2)** | **Step 4 final，2023-04-03 采纳** | `https://database.ich.org/sites/default/files/ICH_M7%28R2%29_Guideline_Step4_2023_0216.pdf`（FDA 镜像 `https://www.fda.gov/media/170461/download`） | 32 |
| **SANTE** | **SANTE/11312/2021 v2026**（2025-11-25 发布、**2026-01-01 实施**，取代 v2 与 12682/2019） | `https://food.ec.europa.eu/document/download/d4786faf-c574-4222-a5c6-45086b3920b8_en?filename=pesticides_mrl_guidelines_wrkdoc_2021-11312.pdf` | 58 |

- **坑**：`ich.org/page/mutagenic-impurities`、`ema.europa.eu/en/documents/...`、EURL 列表页会返反爬页（HTML `<title>Sorry - <id>`）；EURL 镜像 `SANTE-11312_2021-V2.pdf` 实为 **v2**，非 v2026。
- **入库**：`公共知识/书库/guides/{ICH_M7R2_Guideline_Step4_2023,SANTE_11312_2021_v2026}.pdf` ＋ `text/guides/…txt`；登记 `catalog.json`（**23→25 条 / 4,328→4,418 页**）、`seed_guides.json`（4→6）、`INDEX.md`、`README.md`（目录列给"—"，未生成 toc）。`search_books.py` 已验证可检索到新文本。

### 2. 一级文本核出的关键数值（已全部写入条目）

**ICH M7(R2)**（`书库/guides/ICH_M7R2_Guideline_Step4_2023.pdf`）
- **§7.1（p.11）**：TTC **1.5 µg/person/day** ↔ **"theoretical excess cancer risk of <1 in 100,000 over a lifetime"**。
- **Table 2（p.13）**：单杂质 AI **四档 120 / 20 / 10 / 1.5 µg/day**（<1 月 / >1–12 月 / >1–10 年 / >10 年至终生）⇒ **证实常见"五分档 50/15/5/1.5"在一级文本中不存在**（此前仅为"检索无据/误传"，现已定性）。
- **Table 3（p.13–14）**：多杂质（**≥3 个 Class 2/3**）**总日摄入量 120 / 60 / 30 / 5 µg/day**；**Class 1 与制剂中降解产物不计入总量**；复方各活性成分分别管制。
- **§7.2.2（p.12）**：化合物特异 AI 的 LTL 放宽取"**Table 2 同比例**"与"**≤最大日剂量 0.5%**"之低；实例 lifetime **15 µg/day** → **100 / 200 / 1200**，若最大日剂量 **100 mg** 则 <1 月封顶 **500 µg/day**；累积终生剂量 **1.5 µg/day × 25,550 d = 38.3 mg**。
- **§7.3.1（p.13）**：临床开发期**双风险基准**（早期临床 **10⁻⁶**、后期开发 **10⁻⁵**）＋ **Phase 1 给药 ≤14 天**替代法（只控 Class 1/2 与 cohort of concern）。
- **§7.5（p.14）**：**cohort of concern**（aflatoxin-like / N-nitroso / alkyl-azoxy）AI 远低于通用值、须个案；可个案上调的理由（食品/内源暴露更高如甲醛；重症/预期寿命短/晚发慢病/治疗选择有限）；适用所有给药途径与人群。

**SANTE/11312/2021 v2026**（`书库/guides/SANTE_11312_2021_v2026.pdf`）
- **D2（p.15）**：最低 RT ≥ **2 × 死体积 RT**；样品与标准品 RT 差 **±0.1 min**（GC 与 LC 同）。
- **Table 3（p.16）**：鉴定最少离子数 **3（单 MS）/ 2 产物离子（单位分辨 MS/MS）/ 2 离子且质量准确度 ≤5 ppm（HRMS；(Q-)TOF、(Q-)Orbitrap；m/z<200 时 <1 mDa）**，均要求提取离子色谱峰完全重叠。
- **D11（p.17）**：单位分辨 MS/MS 离子比 **±30%（相对）**；**D12（p.17）**：**HRMS 无通用离子比容差值**（准确质量使离子比匹配非必需）。
- **性质（Table 3 前后文）**：Table 3 为 **guidance criteria**，非证明存在/不存在的绝对标准；不满足时应以第二套色谱分离/另一质谱技术/不同设置复核。

### 3. 回写与计数

- **质谱 72→73**：**新 M-16**（SANTE v2026 鉴定判据全表）；重写 **M-1**（MRM 最小要求→一级文本 D11/Table 3）、**M-12**（补 v2026 版本与"版本号纪律"）、**M-15**（否定性核查以现行原文坐实，含"每峰点数无判据"）；改 **L-2**（ICH M7(R2) Table 2/Table 3、38.3 mg）、**L-5②**（五分档定性）；§九 登记两册。
- **毒理 98→102**：**新 C-21**（多杂质总量 Table 3）、**C-22**（化合物特异放宽＋0.5% 上限）、**C-23**（临床双基准与 Phase 1 替代）、**C-24**（cohort of concern 与个案放宽）；**C-17** 出处由"二手转载、须核原文"→"**一级文本已核**"；**C-20** 尾注"ICH M7(R2) 未取得"→"已取得"；§九 登记两册。
- **公共库 78（条数不变）**：**6-6** 出处升级一级文本并写实"五分档误传"；**6-9** 纪律句同步；§七 第 4 条补"分档表已核"；§八 登记两册、catalog 计数改 **25 条 / 4,418 页**。
- **计数**：三份 L3 **248 → 253 条**（公共库 78、毒理 102、质谱 73）。

### 4. 新增可复用要点（环境/工具）

- **一级文本取料走"文档下载 URL"**：`database.ich.org/sites/default/files/…pdf`、`food.ec.europa.eu/document/download/<uuid>_en?filename=….pdf`；**栏目/列表页会被反爬拦截**。
- 同一机构有**版本混淆风险**：EC 的 SANTE 现行本靠"v2026"后缀区分（EURL 镜像仍是 v2）；ICH M7(R2) 的旧文件名 `M7_R2_Guideline.pdf` 已 404。
- 新 guides 无需跑 `build_booklib.py`（会重下全部书目）——手动登记 `catalog.json`/`seed_guides.json`/`INDEX.md`/`README.md` 即可；目录列留"—"。

---

## 二·补·6、会话 6 **已完成**（**扩库**：论文 +100、机构指南 +11、MDPI 专著 +5；三份 L3 253→258）

1. **论文（+100 → 176）**：`fetch_papers.py` 扩 ~48 组检索式（PFAS/微塑料/MOSH-MOAH/食品接触材料/丙烯酰胺/HBM4EU/甲基汞/镉；DNT/免疫毒性/IVIVE/毒理基因组学/EDC 低剂量/IARC/植物药/混合物；PFAS LC-MS/MS、Py-GC-MS、GC×GC、离子迁移、DIA、单细胞蛋白组、形态分析、真菌毒素生物标志）→ `--per-theme 25` 后 **papers 76→176**（guides 60 / tox 41 / risk 39 / ms 39）。
2. **MDPI（19→24 册）**：`discover_mdpi.py` 扩 ~48 组查询 → raw **819→1359**；`pick_new_mdpi.py`（复用 `curate_mdpi.py` 两级过滤）**仅 7 本**合格 → 取 **5 册**（13096 微波/超声辅助萃取 2026、9761 时间分辨率 2024、9858 环境暴露/生物监测 2024、9982 抗球虫药与新兴污染物 2024、11364 天然产物生物活性 2025）。
3. **机构指南（6→17）**：`discover_guides.py` 扩 16 组查询 → `sources_guides.json` **11 条**（4 册 MDPI：食品化学污染物分析 2020 / 真菌毒素 LC-MS/MS 2017 / 丙烯酰胺 2021 / 纳米材料毒性 2023；7 份 OECD：GLP-IT 2024、GLP-ISO/IEC 17025 2016、DNT 数据评价 2023、体外免疫毒性 DRP 2022、职业生物监测 2022、人造纳米材料风险 2022、组织病理内分泌/生殖 2009）。
4. **重建**：`build_booklib.py . sources_mdpi.json seed_guides.json sources_guides.json`（**须一次传全部三 manifest**）→ **catalog 25→41 条 / 4,418→7,407 页 / 815 MB**；`INDEX.md` 生成器重建（机构标题补全 ICH/EC/OECD）。
5. **新条目**：毒理 **A-8/A-9**、质谱 **M-17**、公共库 **§七 6-10/6-11**（详见 `PROGRESS.md` 会话 6）。
6. **计数**：公共库 78→**80**、毒理 102→**104**、质谱 73→**74**，三份合计 **253→258**；7 个 ledger 文件已同步。

**可核锚点（会话 6）**：
- **OECD 体外免疫毒性 DRP**（ENV/CBC/MONO(2022)16）："absence of standardized in vitro methods"（**p.6**）、分层 **Tier1 骨髓→Tier2 白细胞→Tier3 功能试验**＋MITA（**p.9/p.12**）。
- **OECD DNT IVB**（ENV/CBC/MONO(2023)13）：**476 种**做过 ≥1 试验 / **81 种**做遍；**阴性 ≠ 无 DNT 危害**；**未按 GD 34 经典验证**；evergreen（**p.7**）。
- **OECD 职业生物监测**（ENV/CBC/MONO(2022)37，Series No.370）：德 **1060 种中 34% 有皮肤标识、仅 12% 有 BAT/BAR/BLW**；瑞 795 种中 **38%↔12%**；国际统一 OEL/OBL **<1%**（**p.78**）；OBL 四法 refined/ROBL/TOBL/POBL。
- **OECD 人造纳米材料风险**（ENV/CBC/MONO(2022)3）：四步 + NRC 2009 问题形成（p.11）；理化表征/dissolution kinetics/团聚/dosimetry/分组 read-across/nanoinformatics（§3.1 **p.57**）。
- **LC-MS/MS 真菌毒素**（MDPI 2017）：**EC 401/2006 Annex II 回收 60%–120%**（1–10 µg/kg）、AOAC **70%–125%**（**p.25**）；13 毒素谷物 **LOQ 0.4–54.8 ng/g**（**p.26**）。

---

## 三、上次中断点（✅ 会话 4 已完成：条目 6-8 / 6-9 / C-20 已落）

原中断处：核 **PMC13593624**（医疗器械/药品 E&L）与 **PMC12175843**（MD 非致癌 LTL-TTC）里的**新可用数值**。**会话 4 已完成**：两条原文逐句取证完毕 → 写 **公共库 6-8（非致癌 LTL-TTC 三档 112/111/41 µg/kg bw/d）**、**公共库 6-9 ＋ 毒理 C-20（SCT/QT→AET 与给药量放大、120/50 µg/day 药物语境、Q3E 在途）**；计数 **公共库 76→78、毒理 97→98、合计 245→248**，并同步 `公共知识/README.md`、`毒理专家/references/README.md`、`书库/README.md`、`PROGRESS.md`（会话 4 节）、`EVOLUTION.md`。**注：本节原写的"合计 247"系加总笔误，正确为 248（78+98+72）。**

以下原文句仍为可核锚点：

1. **PMC13593624**（SCT/QT/AET，含剂量放大效应）：
   - SCT **0.15 µg/day**（PQRI 2006，**OINDP**）；QT **5 µg/day**。
   - "**The AET concept was introduced to translate the SCT into an analytical limit which will be used as the reporting threshold**…the calculation of the AET described in **USP <1664>** will be used…"
   - 换算实例："a product with a dosing volume of **1000 mL/day** versus a product with a dosing volume of **10 mL/day** will result in **AETs of 5 ng/mL versus 500 ng/mL**, respectively, **for an SCT of 5 µg/day**" ⇒ **同一 SCT 下，大剂量体积产品要求的 LOQ 低 100 倍**。
   - 案例：**细胞毒类抗癌药**依 ICH M7 原则（风险-获益）**把 SCT 提高到 120 µg/day**（"Employing ICH M7 principles supported an SCT to 120 µg/day for cytotoxic cancer drugs"）。
   - 案例：**1750 mL/day** 产品 AET 技术上不可达 ⇒ 经**广泛目标物评估**论证**更高 SCT 50 µg/day**。
   - **ICH Q3E（现行 draft）**拟统一 E&L 框架并细化各剂型/途径/疗程的 SCT、QT 定义；**ICH S9/Q3B 不处理 SCT**（严重疾病的替代研究讨论另见原文）。
   - 另：原句提示"**120 / 50 µg/day 这两个数值是 SCT（患者日暴露总量）档位，不是 ICH M7 致癌物 Class 1–5 的 LTL 分档**"⇒ **不得把它们与"五分档 50/15/5/1.5"混为一谈**（**会话 5 已回一级文本证实：ICH M7(R2) 只有四档 120/20/10/1.5，"五分档"不存在**，见 §二·补；条目 6-6/C-17 已改为"一级文本已核"）。
2. **PMC12175843**（**非致癌 LTL-TTC 三档**）：
   - 原句："…proposing **non-cancer TTC values derived for LTL exposures. The derived TTC values were 112 (≤1–30 days), 111 (31–365 days), and 41 μg/kg/day (≥366 days)**."
   - 配套："**Buist et al.（农药）与 Bercu & Dolan（药品）系对长期阈值分别施加 ×3 与 ×10 因子**推导短期阈值；**本文（Kenyon 等）是直接从亚急性/亚慢性实测数据推导**"。
   - **已解决（会话 4）**：该三档**不按 Cramer 分类分列**（每档单值；Munro **30/9/1.5** 仅对应 **≥366 d** 档）；判据句已读完——POD 选择"inclusive of DART studies"（DART NOAEL 占总体 **38%**）⇒ 三档**兼护发育与生殖毒性终点**。

**下次动作**：会话 5 已完成 **②③**（ICH M7(R2) 与 SANTE v2026 入库并条目化，见 §二·补）；**会话 6 已完成扩库**（论文 +100、指南 +11、MDPI +5，见 §二·补·6）→ **接手 §四 待办**（首选：给**毒理专家**跑 P0 评测用例，验证 A-8/A-9、C-18/C-19 是否被实际引用；次选：把会话 6 新入库的指南继续消化为条目，如 OECD 组织病理内分泌/生殖、GLP-IT；另可核 PMC7500704 的 **94%** 定义）。

---

## 四、剩余待办（按优先级）

1. ~~**（上面）6-8/6-9 成条** ＋ 计数同步 ＋ **表格完整性复检**~~ → **已完成（会话 4）**；表格完整性复检通过（四份文件表格行竖线计数无异常）。
2. ~~**一级权威文本剩余 ② ③**~~ → **已完成（会话 5）**：**ICH M7(R2)** 经 `database.ich.org` 直链取得 **Step 4 final** 原文（**五分档证实不存在**：Table 2＝**120/20/10/1.5**、Table 3＝**120/60/30/5**）；**SANTE** 经 `food.ec.europa.eu` 的**文档下载 URL** 取得现行 **v2026**（RT **±0.1 min**、离子比 **±30%**、鉴定 **3/2/2 离子**、HRMS **≤5 ppm**）；均入库并条目化（见 §二·补）。**教训**：栏目页（`ich.org`/`ema.europa.eu`/EURL 列表）会反爬，须用**文档下载 URL**。
3. **PMC7500704 里的 "94%"（Dobo 2012 pre-expert review performance）确切定义** → 回 *Regul Toxicol Pharmacol* 正式出版版核（现据 NIHMS 作者稿，条目已标）。
4. **新书配额外扩消化**：`Sample Preparation Quo Vadis`（189 页，仅取 4 处）、`Chromatography–Mass Spectrometry…`（307 页，8 处）、`QMRA of L. monocytogenes in Foods`（219 页，取 5 处）——**每册 10–15 条**。
5. **`公共知识/README.md` 增"分区书库对照表"**（营养/食品加工等专家仍用私有 `references/books/`，与 `公共知识/书库/` 并存）。
6. **复核 `references/01`/`05`/`06` 头部条目区间**（是否与实际条目号一致）；`references/06-跨域适用与边界.md` 补 **QMRA 分支**一行（指条目 5-8～5-12 与 §七 第 5 条纪律）。
7. WHO 扫描件 **4 篇需 OCR**（营养库历史遗留）。
8. **评测闭环**：`evals/质谱专家/MASS-001` 首跑 **13/14（92.9%）通过**；下次可给**毒理专家**跑 P0 用例（验证 G-17/G-18、C-18/C-19 是否被实际引用），并把 `evals/registry.md` 状态更新。

---

## 五、当前计数（务必与此一致，改后回写台账）

| 对象 | 数值 |
|---|---|
| 公共库 L3 | 9 节 **80** 条（`公共知识/技术指南/风险评估-证据条目与出处.md`；会话 6 新增 §七 **6-10/6-11**） |
| 毒理 L3 | 9 节 **104** 条（`毒理专家/references/证据条目与出处.md`；会话 5 新增 **C-21～C-24**、会话 6 新增 **A-8/A-9**） |
| 质谱 L3 | 9 节 **74** 条（会话 5 新增 **M-16**、会话 6 新增 **M-17**） |
| 三份合计 | **258** 条 |
| 食品加工 L3 | **35** 行 |
| OA 全文 | **176** 篇（guides 60 / tox 41 / risk 39 / ms 39，主题可交叉） |
| 书库 | catalog **41** 条 / **7 407** 页 / **815 MB**（MDPI **24** 册 ＋ guides **17** 篇：EHC 240 章节 4 ＋ **ICH M7(R2)** ＋ **SANTE/11312/2021 v2026** ＋ OECD 7 份 ＋ MDPI 4 册） |

**编号规则**：公共库 `N-x`；毒理 `T-/G-/E-/R-/N-/C-/A-`；质谱 `M-/P-/S-/Q-/H-/C-/O-/L-`。三份间交叉引用（写"公共库 **3-14**、毒理 **C-19**"这类成对号）。

---

## 六、关键文件

| 文件 | 作用 |
|---|---|
| `公共知识/技术指南/风险评估-证据条目与出处.md` | 公共 L3 底座（§三 TTC/MOE；§六 iTTC/LTL；**§七 职业生物监测/纳米材料**；§八 **五条纪律**；§九 复现清单） |
| `毒理专家/references/证据条目与出处.md` | 毒理 L3（§二 G-；§七 C-TTC/QSAR/LTL；§八 **A-8/A-9 NAMs**；§九 书库登记） |
| `质谱专家/references/证据条目与出处.md` | 质谱 L3（**M-3** 法规语境更正、**M-15** 否定性条目、**M-16** SANTE v2026 鉴定判据、**M-17** 真菌毒素 LC-MS/MS、**L-2** ICH M7(R2)） |
| `公共技能/skills/risk-assessment/references/03-剂量反应与健康指导值.md` | **§五 MOE 整节已按 EFSA SC 2025 重写**；§6.1 TTC；(Q)SAR 纪律行 |
| `公共技能/skills/risk-assessment/references/04-风险表征与排序.md` | 1.1 判据 / 1.3 MOE 三条新要点 / 1.4 **新增"关切低（官方口径）"档** |
| `公共技能/skills/risk-assessment/scripts/riskcalc.py` | `calc_moe` 三档文案已引 e9606；参数 `--exp` |
| `公共知识/书库/papers/` | `index.json`（须有 `pmcid`）、`INDEX.md`、`xml/`、`txt/` |
| `公共知识/书库/PROGRESS.md` | 会话 2–6 台账、§7–§9、**待办 1–8** |
| `公共知识/书库/guides/ICH_M7R2_Guideline_Step4_2023.pdf`、`…/SANTE_11312_2021_v2026.pdf` | 会话 5 入库的两个**一级权威文本**（含 `text/guides/…txt`） |
| `公共知识/书库/guides/Detailed_Review_Paper_on_In_Vitro_Test_Addressing_Immunotoxicity_With.pdf`、`…/Initial_Recommendations_…_Developmental_N.pdf`、`…/Occupational_Biomonitoring_Guidance_Document.pdf`、`…/Important_Issues_on_Risk_Assessment_of_Manufactured_Nanomaterials.pdf` | 会话 6 入库的 **4 份 OECD 关键指南**（体外免疫毒性 / DNT IVB / 职业生物监测 / 人造纳米材料风险） |
| `公共知识/README.md`、`书库/README.md`、`毒理专家/references/README.md` | 分区索引与计数 |
| `EVOLUTION.md` | 演进日志（2026-10-23 六行：199→237→241→245→248→253→**258**、MOE 定性反转、(Q)SAR 入库、E&L 两条阈值链、**ICH M7(R2)+SANTE v2026 入库**、**会话 6 扩库**） |
| `食品安全专家/skills/food-safety/SKILL.md` 等三处 | 欧盟法规语境更正（本轮新增） |
| `/tmp/opencode/fix_tables.py`、`/tmp/opencode/bak/` | 表格修复脚本与修复前备份（注意：**转义 `\|` 会误报**） |

---

## 七、复现命令

```bash
cd /home/caiq/MyAgents
# 检索书库（含全文）
python3 公共知识/书库/tools/search_books.py "MOE" --context 1
python3 公共知识/书库/tools/read_page.py <书名> <页码>
# OA 全文取原句（注意行内换行会致字面检索 MISS，用 .{0,N} 宽松式）
grep -o '.\{0,140\}10,000.\{0,200\}' 公共知识/书库/papers/txt/PMC12332500.txt
grep -o '.\{0,200\}Considering the criteria.\{0,600\}' 公共知识/书库/papers/txt/PMC12175843.txt
# EuropePMC（须 https）
curl -s --noproxy '*' "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%22MOE%20of%2010,000%22%20AND%20OPEN_ACCESS:Y&format=json&pageSize=8&resultType=lite"
curl -s --noproxy '*' "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMCID:PMC7734868&format=json&resultType=core"   # 取 DOI
curl -s --noproxy '*' -o x.xml "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7500704/fullTextXML"
# 脚本自测
python3 公共技能/skills/risk-assessment/scripts/riskcalc.py moe --pod 100 --exp 0.008
python3 公共技能/skills/risk-assessment/scripts/riskcalc.py ttc --exp 0.0001 --class DNA
```

**表格自检要点**：`|` 计数时须把 **转义 `\|` 视为非分隔符**（否则误报）；另要查"**无表头续表块**"（表中段空行会截断表格）。

---

## 八、可核锚点（已验证，可直接引用）

- Ch5 **p.74**（MOE 系相对比较；不建 HBGV；BMDL₁₀ 作 POD）；EHC 240 §4.5 **p.11/19/79/83/93/94**（TTC 决策树 p.78、十二项排除步骤 6 p.79、体内致突变剂量-反应推 MOE p.93、HTTr p.83）。
- **PMC7009090**（EFSA 2019 TTC 指南）§3/Table 2、§3.4/3.5/3.6、§4.1~4.3；**PMC13593624** Table I（**120/20/10/1.5**）＋ SCT **0.15**/QT **5** µg/day；**PMC12175843**（10⁻⁶ 与 10⁻⁵ 两条推导路径；**非致癌 LTL 三档 112/111/41 μg/kg/day**）；**PMC13379458**（1.5 µg/day ＝ one in a hundred-thousand）；**PMC12332500**（MOE 一级文本）；**PMC7500704/PMC7734868**（(Q)SAR 规程与版本漂移）。
- 质谱：dwell **50/20/100/150/8 ms** 与 ICP-TOF 每峰 **3 点**（`Mass_Spectrometry_for_Biomedical…` **p.152**）；LOD 三法（Chrom **p.50**/**p.126**/S/N 3–10）；GC-MS/MS Table 1 **p.16–19**。
- **一级文本锚点（会话 5）**：**ICH M7(R2)** §7.1 **p.11**（TTC 1.5 / <1/100,000）、Table 2 **p.13**（**120/20/10/1.5**）、Table 3 **p.13–14**（**120/60/30/5**）、§7.2.2 **p.12**（**0.5% 上限**、38.3 mg）、§7.3.1 **p.13**（**10⁻⁶/10⁻⁵**、Phase 1 ≤14 d）、§7.5 **p.14**（cohort of concern）；**SANTE v2026** D2 **p.15**（RT **±0.1 min**）、Table 3 **p.16**（**3/2/2 离子**、≤5 ppm）、D11/D12 **p.17**（**±30%**、HRMS 无通用值）。
- QMRA Listeria 书 **p.9/21/33/49/64/132–133**（RR 44.7、模型差 343.5）。
- 热加工 Novel_Thermal **p.11/26–29/38/40/47–51/79/93/98/103**（HPP 侧油含量无显著影响＝**p.98**；热处理侧油含量**有**显著影响）。

**否定性结论（已入库，不得再当事实用）**：儿童手-口接触频率 3/7 次/h；**"每峰最少点数"不是 SANTE 判据**（SANTE 用**最少离子数 3/2/2**）；**无"分级 IR 容差表"**（SANTE 只给单一 **±30%**，且 **HRMS 无通用值**）；**分时段（acquisition window）切分数值无权威出处**；**ICH M7"五分档 50/15/5/1.5"在一级文本中不存在**（见质谱 **M-15/L-5**、毒理 **C-17**、公共库 **6-6**）。
