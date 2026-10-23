# 参考文献索引（毒理专家私有知识库）

> 本目录为**毒理/危害表征**专用知识。跨域风险评估方法（暴露、HQ/MOE、概率评估）见公共技能 `公共技能/skills/risk-assessment/`，本目录不重复。

| 文件 | 内容 | 主要来源 |
|---|---|---|
| `01-毒理学基础与危害识别.md` | ADME/TK、剂量-反应形态、关键效应与适应性区分、易感人群、证据权重（WoE）、生物标志物 | IPCS/WHO 毒理学原则、EHC 240 Ch.5、EFSA 危害评估指南 |
| `02-剂量反应建模与健康指导值.md` | NOAEL/LOAEL 局限、BMD/BMDS/PROAST 四步与模型平均、BMR 选择、HBGV 类型与推导、UF/CSAF、ARfD、数据不足处理 | CFSA《食品中化学物健康指导值制定指南》(2023)、EHC 240 Ch.5、US EPA BMDS、RIVM PROAST |
| `03-毒性终点专题.md` | 遗传毒性测试组合、致癌性与 IARC 分类、DART、靶器官、局部毒性与致敏、微生物与生物毒素 | OECD TG、IARC Monographs 前言、EFSA 各终点指南、GB 15193 |
| `04-计算毒理与替代方法.md` | TTC/Cramer 与排除条件、(Q)SAR 五原则与适用域、read-across 论证、NAMs/AOP、IVIVE/PBPK | EFSA TTC 意见、OECD (Q)SAR 原则、EChA RAAF、OECD AOP |
| `05-试验规范与数据质量.md` | GLP 十要素、OECD TG 编号归类、Klimisch 分级、剂量设计与统计、GB 15193 框架、3R | OECD GLP/TG、Klimisch et al. (1997)、GB 15193 系列 |
| **`证据条目与出处.md`** | **L3 原著证据底座（9 节 104 条）**：EHC 240 Ch5/§4.5/§9.1.4.2 逐条结论（物理页码）、**ICH M7(R2) 一级文本**（LTL Table 2/3、化合物特异放宽、临床双基准、cohort of concern）、EFSA OA 意见与指南（PMCID+§）、MDPI 毒理专著（页码）、UF 拆解与个案、TTC/iTTC/LTL（含**排除清单两版、混合物规则、(Q)SAR ≥2 独立模型、10⁻⁶↔10⁻⁵ 基准纪律、医疗器械非致癌 LTL-TTC 与 SCT/QT→AET**）、AOP-NAMs 接受度（含 **A-8 体外免疫毒性分层、A-9 DNT IVB**）；条目号 T-/G-/E-/R-/N-/C-/A- | 公共知识/书库（WHO cdn.who.int、ICH database.ich.org、MDPI CC BY 4.0、OECD 开放获取、EuropePMC OPEN_ACCESS:Y） |
| **`书库索引.md`** | **本专家在 `公共知识/书库/` 里实际引用的书目 + 页码锚点 + 取证命令**（含"为何共用公共书库而不自建"的说明） | 公共知识/书库（41 条 / 7,407 页） |
| 模板 | `templates/毒理危害表征表.md` | 本专家整理 |

## 与其他知识库的分工

| 问题 | 去哪 |
|---|---|
| 暴露量、HQ/MOE/ILCR、概率评估、风险排序 | 公共技能 `risk-assessment` |
| GB 限量、合规判定、HACCP、风险管理 | 食品安全专家 `references/` |
| 实测浓度、代谢物鉴定、方法学 | 检测专家 / 质谱专家 `references/` |
| 政策法规、标准规范原文 | 全局「公共知识」 |

## 原文获取与核验（约定）

1. **数值类结论**（ADI、TTC 阈值、TG 编号、IARC 分组）必须核对**现行版本**，注明机构与年份。
2. 优先引**权威评估报告原文**（JECFA/JMPR 毒理专著、EFSA Scientific Opinion、IRIS），其次原始研究。
3. 二手综述仅作线索，关键判断回原文。
4. 无法核实的数值，标注「待核实」，**不得**以经验值替代。
5. 中国法规与标准以 `openstd.samr.gov.cn` / `cfsa.net.cn` 现行文本为准。

## 维护约定

- 新增知识文件须在本表登记，并在 `toxicity` 技能 `SKILL.md` 的「参考文件」表中同步。
- 阈值/编号类更新后，在 `EVOLUTION.md` 记一行（类型 `reference`）。
