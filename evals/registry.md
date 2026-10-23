# 评估用例总表

> 新增用例后请在此登记。状态取值：`未评` / `通过` / `部分` / `失败` / `停用`。

## 域代码对照

| 域代码 | 专家 | agent id |
|---|---|---|
| ORCH | 协调专家 | `orchestrator` |
| PLANT | 种植专家 | `planting-expert` |
| BREED | 育种专家 | `breeding-expert` |
| NURSERY | 育苗专家 | `nursery-expert` |
| FERM | 发酵专家 | `fermentation-expert` |
| FOODPROC | 食品加工专家 | `food-processing-expert` |
| FOODSAFE | 食品安全专家 | `food-safety-expert` |
| NUTRI | 营养专家 | `nutrition-expert` |
| DETECT | 检测专家 | `detection-expert` |
| MASS | 质谱专家 | `mass-spec-expert` |
| TOX | 毒理专家 | `toxicology-expert` |
| SUBMIT | 投稿专家 | `submission-expert` |
| DOC | 文档专家 | `document-expert` |

## 用例清单

| ID | 专家 | 标题 | 优先级 | 状态 | 最近评估 | 文件 |
|---|---|---|---|---|---|---|
| ORCH-001 | 协调专家 | 跨领域任务拆解与路由 | P0 | 通过 | 2026-10-23 | [链接](协调专家/ORCH-001-task-decomposition.md) |
| PLANT-001 | 种植专家 | 设施番茄测土配方施肥方案 | P0 | 通过 | 2026-10-23 | [链接](种植专家/PLANT-001-soil-fertigation.md) |
| BREED-001 | 育种专家 | 耐盐碱水稻育种方案 | P0 | 通过 | 2026-10-23 | [链接](育种专家/BREED-001-salt-tolerant-rice.md) |
| NURSERY-001 | 育苗专家 | 番茄嫁接苗工厂化育苗方案 | P0 | 通过 | 2026-10-23 | [链接](育苗专家/NURSERY-001-grafted-tomato.md) |
| FERM-001 | 发酵专家 | 枯草芽孢杆菌液态发酵产酶工艺 | P0 | 通过 | 2026-10-23 | [链接](发酵专家/FERM-001-bacillus-protease.md) |
| FOODPROC-001 | 食品加工专家 | 低糖蓝莓果汁饮料开发 | P0 | 通过 | 2026-10-23 | [链接](食品加工专家/FOODPROC-001-low-sugar-blueberry.md) |
| FOODSAFE-001 | 食品安全专家 | 农残限量判定与合规结论 | P0 | 通过 | 2026-10-23 | [链接](食品安全专家/FOODSAFE-001-mrl-compliance.md) |
| NUTRI-001 | 营养专家 | 减脂控脂一周膳食方案 | P0 | 通过 | 2026-10-23 | [链接](营养专家/NUTRI-001-weight-loss-diet.md) |
| DETECT-001 | 检测专家 | 叶菜多农残筛查检测方案 | P0 | 通过 | 2026-10-23 | [链接](检测专家/DETECT-001-pesticide-multiresidue.md) |
| TOX-001 | 毒理专家 | 农残 ADI 复核与 POD 论证 | P0 | 通过 | 2026-10-23 | [链接](毒理专家/TOX-001-adi-pod-justification.md) |
| MASS-001 | 质谱专家 | MRM 多残留方法验证与确证判据（须回原文取证） | P0 | **通过**（重跑 34/34） | 2026-10-23 | [链接](质谱专家/MASS-001-mrm-method-validation.md) |
| MASS-002 | 质谱专家 | 本地谱库自动匹配与置信度分级 | P0 | 通过 | 2026-10-23 | [链接](质谱专家/MASS-002-spectral-library-matching.md) |
| SUBMIT-001 | 投稿专家 | 期刊合规诊断与投稿材料生成 | P0 | 通过 | 2026-10-23 | [链接](投稿专家/SUBMIT-001-journal-compliance.md) |
| DOC-001 | 文档专家 | 中试总结报告与汇报 PPT 生成 | P0 | 通过 | 2026-10-23 | [链接](文档专家/DOC-001-report-and-slides.md) |

> **2026-10-23 首次全量评分（人工启动）**：上述 14 个专家用例 + 1 个公共技能用例**全部重跑/补跑**，共 **15/15 判「通过」**，**未见红线触发**。结论为**自动预评**（依据各专家返回的交付物），**最终裁定留人工**；逐项分数与备注见各用例「评估历史」。

## 公共技能用例

| ID | 技能 | 标题 | 优先级 | 状态 | 最近评估 | 文件 |
|---|---|---|---|---|---|---|
| RISK-001 | `risk-assessment` | 跨域风险评估方法与边界 | P0 | 通过 | 2026-10-23 | [链接](公共技能/RISK-001-risk-assessment-boundaries.md) |

## 覆盖度检查

- [x] 每位专家至少 1 个 P0 用例（**13/13**）＋质谱专家第 2 个用例（MASS-002）＋公共技能用例（RISK-001），共 **15 个 P0 用例**
- [x] 核心职责均有对应用例
- [x] 涉及限量/标准的用例均含红线检查

> 后续可按需为每位专家补充 P1/P2 的边界与对抗性（区分度更高）用例。
