# 质谱专家知识库 · 参考资料索引

> 本目录为**质谱专家**的参考资料库，收录质谱仪器与电离、方法开发与验证、谱图解析与未知物鉴定的结构化知识。
> **仪器参数、标准方法编号、判定规则与限量一律以现行有效版本与仪器实测为准**（复核入口：国家标准全文公开系统 <https://openstd.samr.gov.cn>；CFSA <https://sppt.cfsa.net.cn>；EU SANTE 判定规则 <https://food.ec.europa.eu>）。

## 一、知识文件清单

| 文件 | 主题 | 主要内容 |
|---|---|---|
| `质谱仪器与电离方式.md` | 仪器与电离 | 电离方式机理与适用（ESI/APCI/APPI/EI/CI/MALDI/DART/DESI/ICP）、质量分析器对比（QqQ/Q-TOF/Orbitrap/IT/TOF/FT-ICR）、串联与联用、典型参数、同位素与加合物判读 |
| `质谱方法开发、定量与验证.md` | 方法学与定量 | 方法开发流程、采集模式选择、MRM 设计、同位素内标、基质效应评估与消除、校准曲线、LOD/LOQ、方法验证参数与接受标准、质控与仪器性能核查 |
| `谱图解析与未知物鉴定.md` | 解析与鉴定 | 碎裂规律与中性丢失、碎片归属、精确质量与分子式推算、谱库检索（NIST/mzCloud/MassBank/GNPS）、原位裂解工具（CFM-ID/MetFrag/SIRIUS/MS-FINDER）、可信度分级、组学数据处理要点 |
| **`证据条目与出处.md`** | **L3 原著证据底座（9 节 74 条）** | 把 `公共知识/书库/` 的 MDPI 分析专著、OA 全文与机构权威文本（**SANTE/11312/2021 v2026、ICH M7(R2)**）消化为可引用条目：验证/确证判据（M-，含 **M-16 现行 SANTE 鉴定判据全表**、**M-17 多类真菌毒素 LC-MS/MS 与法规回收窗口**）、仪器参数与采集（P-）、前处理与基质效应（S-）、ID-MS/CRM 不确定度（Q-）、HRMS 非靶向与回顾筛查（H-）、置信分级与数据标准（C-）、组学（O-）、与毒理/暴露接口（L-）；**逐条带页码或 PMCID** |
| **`书库索引.md`** | **本专家在 `公共知识/书库/` 里实际引用的书目 + 页码锚点 + 取证命令**（含"为何共用公共书库而不自建"的说明） | 公共知识/书库（41 条 / 7,407 页） |
| **`参考谱图-人参皂苷Rg1_Rg3/`** | **实测参考谱 + MRM 通道（2026-10-23）** | MassBank 反查的 Rg1（15 条）/ Rg3（44 条）参考谱：`README.md`（化合物信息、关键碎片归属）、`peaks_all.csv`（446 峰）、`Rg1/Rg3_mass_spectra.png`、`MRM通道建议.md`（离子对、同分异构干扰、CE 起点）、`讲解_怎么看质谱图.md`（带图入门讲解）、`讲解_怎么看质谱图.docx`（Word 版，图片内嵌）；`fetch.py`/`plot.py` 可复现 |
| **`谱库-人参/`** | **本地参考谱库：人参皂苷与活性成分（2026-10-23）** | 按 **99 项目标清单**构建的**可检索多库合并谱库**（MassBank RDF Portal SPARQL ＋ GNPS-LIBRARY/GNPS-NIH/MoNA 批量 MGF）：**1778 条谱 / 46 化合物 / 46 项目标收录（53 项缺失）**。含 `README.md`（数据来源、覆盖率、使用与局限）、`notes_extra.md`（皂苷碎裂与同分异构判读要点）、`targets.tsv`（99 目标）、`scripts/`（`mb_extract`→`fetch_peaks`→`gnps_scan`→`build_library`→`make_report`，可复现）、产物 `library.msp`/`library.mgf`/`index.csv`/`compounds.csv`/`coverage.csv`/`覆盖与稀有皂苷清单.md`、`user/`（**实验自测谱投放口**：放 `*.mgf`/`*.msp` 后重跑 `build_library.py` 即并入，source=`User(实验)`）；配合技能 `spectral-matching` 检索（自检 rank-1 通过） |
| **`谱库-合并/`** | **统一检索入口：人参 ＋ 金线莲 合并谱库（2026-10-23，自动生成）** | 由 `scripts/merge_libraries.py` 合并同级 `谱库-*`（当前 2 库）：**2954 条谱（跨库去重 1211）/ 59 化合物 / InChIKey 100%**。产物 `library.msp`、`library.mgf`（每条带 `library=`/`LIBRARY=` 归属）、`index.csv`（含 `library`、`inchikey_skeleton`）、`compounds.csv`、`coverage.csv`（保留 `library` 列），以及 **`search.sh` 一键检索**（`./search.sh <查询谱.msp|mgf>`，转发到 `spectral-matching`）。更新流程：先在分库重跑 `build_library.py`（可含 `user/` 自测谱）→ 再在本目录重跑 `merge_libraries.py` |
| **`谱库-金线莲/`** | **本地参考谱库：金线莲（Anoectochilus roxburghii）成分（2026-10-23）** | 按 37 项目标清单构建的**可检索多库合并谱库**（同「谱库-人参」管线，复用已下载的 GNPS/MoNA 镜像）：**2387 条谱（全部有峰）/ 35 化合物 / 34 项目标收录（3 项缺失：Kinsenoside、Gastrodin、Trifolin）**。覆盖黄酮苷（芦丁/异槲皮苷/槲皮苷/金丝桃苷/紫云英苷/烟花苷/水仙苷/异鼠李素-3-葡糖苷/牡荆素/异牡荆素）、苷元（槲皮素/山奈酚/异鼠李素/芹菜素/木犀草素）、酚酸、有机酸、核苷/氨基酸、甾醇；**标志成分金线莲苷（Kinsenoside）与天麻素（Gastrodin）在 MassBank/GNPS/MoNA 均无实测 MS²**，`notes_extra.md` 已给按分子式推算的母离子参考值（金线莲苷 `[M–H]⁻ 263.0772`、`[M+HCOO]⁻ 309.0822`、`[M+Na]⁺ 287.0743`），待 `user/` 自测补齐 |

## 二、关联技能与外部资源

| 资源 | 用途 |
|---|---|
| 技能 `mass-spectrometry`（本专家） | 方法学速查：选型决策、采集模式、解析流程、常见坑 |
| **技能 `spectral-matching`（本专家）** | **本地谱库自动比对**：MSP/MGF/JSON/CSV 读入、8 种打分器（熵/余弦/匹配因子/修饰余弦）、候选过滤（前体 ppm/加合物/极性/CE）、Schymanski 分级、谱相似度网络；自带纯 Python 引擎（仅 numpy），装 `matchms/ms_entropy/pyteomics` 自动增强 |
| 公共技能 `togomcp-sparql` | 查 MassBank 参考谱图、ChEBI/PubChem 结构、LIPID MAPS/SwissLipids 脂质等 RDF 数据库 |
| 检测专家 `references/方法学与仪器分析.md` | 质谱在整体检测方案中的位置、前处理与验证的总览 |
| MassBank（RDF） | 真实参考质谱图（InChIKey 反查、SPLASH 哈希） |
| NIST / mzCloud / GNPS | EI 与 ESI 谱库检索 |

## 三、来源与可靠性说明

- **一级（权威）**：仪器厂商官方技术文档、权威方法学教材、标准正文、官方谱库说明。
- **二级（参考）**：综述、应用文献、社区库；仅作检索线索，参数与结论须回归仪器实测或一级来源。
- 涉及标准编号、判定规则、限量值、仪器参数不得臆造；数值型结论须标注**测试条件**（仪器型号、CE/NCE、色谱条件）。

## 四、收录原则与核验约定

- 标准类只收"**要点 + 标准号 + 版本状态 + 查询入口**"，不整篇下载。
- 数据库/工具类记录**能力边界**（覆盖率、适用电离方式、是否免费），避免把"查不到"当成"不存在"。

## 五、待完善清单（建议后续补充）

1. 补入本实验室实际仪器的型号与已验证参数（源参数、CE、柱条件）。
2. 补充目标物（农残/毒素/添加剂/功效成分）的 MRM 通道与保留时间表。
3. 补充方法验证报告实例与不确定度评定（含真实数据）。
4. 补充组学数据处理的参数化流程（峰检测/对齐/注释阈值）。

---
*本索引由质谱专家维护。新增文件请在此登记。*
