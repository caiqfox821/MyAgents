---
name: journal-submission
description: 外文学术期刊投稿技能。用于期刊识别与作者指南获取、投稿规则结构化抽取、稿件结构解析、合规诊断、按风险分级定向修订（摘要/关键词/参考文献/拼写/声明）、生成 Cover Letter/Highlights/Graphical Abstract 说明/Response to Reviewers 与投稿前检查。当投稿选刊、期刊格式合规、稿件修订、投稿材料生成、审稿意见回复时加载。
---

# 期刊投稿技能

## 何时使用
用户要投外文期刊，需要：获取/解析 Guide for Authors、检查稿件是否合规、按期刊规则修订稿件、生成 Cover Letter / Highlights / 各类声明、回复审稿意见、做投稿前检查。

## 工作流（7 层）
1. **用户输入层**：接收期刊名、稿件（Word/LaTeX/PDF）、投稿阶段。
2. **期刊知识层**：获取并缓存作者指南（文本、URL、版本、抓取时间）。
3. **规则解析层**：把非结构化指南转成可执行规则表（带置信度与来源）。
4. **稿件解析层**：解析论文结构（标题、摘要、参考文献、图表、声明）。
5. **合规诊断层**：逐条比对 → 合规报告与问题清单。
6. **修订生成层**：按风险分级修订稿件与材料。
7. **审核导出层**：留痕、确认、导出修订记录与 Word/LaTeX/PDF。

## 期刊规则获取
- **标准化期刊名**：`Food Control` → 全称、ISSN、出版商、官网域名。
- **定位作者指南优先级**：期刊官网 `Guide for Authors` → 出版商页面（Elsevier/Springer/Wiley/IEEE）→ 已缓存权威规则库。
- **抓取策略**：HTTP 获取 HTML → 提取正文（去导航/广告/页脚）→ 记录抓取时间、URL、版本号 → 同刊 TTL 缓存（如 7–30 天刷新）。
- **失败兜底**：提示用户粘贴作者指南链接或文本。
- **反爬与合规**：遵守 `robots.txt`、控制频率、不抓付费墙后内容、只存公开指南信息。

## 规则 Schema
```json
{
  "journal": "Food Control",
  "publisher": "Elsevier",
  "guide_url": "https://...",
  "crawl_time": "2026-10-02T10:00:00Z",
  "rules": [
    {
      "rule_id": "FC-ABS-01",
      "category": "abstract",
      "description": "摘要不超过250词",
      "check_type": "word_count",
      "field": "abstract",
      "max_value": 250,
      "severity": "must",
      "confidence": 0.92,
      "source_text": "You are required to provide a concise and factual abstract which does not exceed 250 words.",
      "source_url": "https://..."
    }
  ]
}
```

### 规则类别
`manuscript_structure`（Highlights/Keywords/Graphical Abstract 有无）· `abstract`（字数/结构）· `references`（编号制/作者-年份/DOI）· `figures_tables`（格式/分辨率/标题位置）· `ethics`（伦理/利益冲突/作者贡献）· `data_policy`（数据可用性声明）· `language`（英式/美式、拼写）· `submission_files`（盲审/图表分开上传）· `word_limit`（正文限制）· `supplementary`（补充材料格式）。

### 常见 check_type
`word_count` · `count`（关键词条数）· `exists`（是否存在该声明/章节）· `regex`（引用样式/编号）· `enum`（枚举值）· `file_format` · `language_style` · `manual`（需人工确认）。

## 稿件解析
| 格式 | 解析要点 |
|---|---|
| `.docx` | python-docx：标题、段落、表格、脚注 |
| `.tex` | section / abstract / bib |
| `.pdf` | 兜底，难度高，结果须人工复核 |
| `.bib` / `.ris` | 参考文献专用解析 |

内部对象：`title / abstract / keywords / sections[] / references[] / figures[] / tables[] / statements{data_availability, conflict_of_interest, ethics}`。

## 合规诊断
流程：读规则 → 读稿件结构 → 逐条检查 → 生成报告。

| 规则 | 状态 | 说明 |
|---|---|---|
| 摘要 ≤ 250 词 | 不合规 | 当前 312 词，需压缩 62 词 |
| 需要 Highlights | 缺失 | 稿件未提供 |
| 参考文献编号制 | 不合规 | 当前为作者-年份制 |
| 需要 Data Availability Statement | 缺失 | 未找到数据声明 |
| 图片分辨率 ≥ 300 dpi | 待确认 | 需用户上传原始图片 |

**诊断等级**：`must`（必须改，否则可能退回）· `should`（强烈建议）· `optional`（可选优化）· `uncertain`（规则不明，需作者确认）。

## 修订风险分级
- **低风险（自动）**：参考文献格式转换、摘要字数压缩、关键词数量调整、标题大小写、英式/美式统一、单位符号与 p 值格式、图表标题规范、声明段落补全模板。
- **中风险（半自动，需确认）**：摘要重写、Highlights 生成、Graphical Abstract 文字说明、Cover Letter 生成、段落顺序调整、引言逻辑压缩。
- **高风险（只给建议）**：方法部分改写、结果解释、结论强度、作者署名、伦理声明真实性、数据可用性描述。

**留痕示例**
```json
{
  "change_id": "C001",
  "type": "reference_format",
  "original": "[1]",
  "revised": "(Smith et al., 2023)",
  "reason": "Food Control 采用 APA 第 7 版作者-年份制引用（官方 Guide，2026-10-05）",
  "risk": "low",
  "accepted": false
}
```

## 投稿材料生成
- **Cover Letter**：研究贡献、与期刊匹配性、未一稿多投、所有作者同意、推荐/回避审稿人占位符。
- **Highlights**：3–5 条，每条遵守字符限制。
- **Graphical Abstract 说明**：期刊要求时给文字版设计建议。
- **Data Availability Statement**：按作者选择生成不同版本。
- **Conflict of Interest Statement**、**Author Contributions**。
- **Response to Reviewers**：逐条回复、标注修改位置。

**Prompt 约束**：语气正式简洁、不夸大结论、不编造数据/作者/DOI/页码/卷期、不虚构基金与伦理审批、不承诺录用、规则不确定须标来源、修改须保留原文对照。缺失信息用占位符 `[Corresponding Author]`、`[Funding Information]`。

## 交付前自检清单
- [ ] 每条规则绑定 `source_url` + `source_text` + 抓取时间/版本
- [ ] 低置信度（低于阈值）规则未自动执行，标注"待确认"
- [ ] 高风险修改只给建议，且经用户确认
- [ ] 所有改动有原文对照、理由、风险等级，可回滚
- [ ] 未编造数据、作者、基金、伦理、DOI、页码、卷期、审稿人
- [ ] 期刊规则冲突时以官网现行 Guide for Authors 为准
- [ ] 信息缺失处使用占位符，未擅自补全

## 参考资源（`references/`，详见 `references/README.md` 索引）
知识文件（位于 `/home/caiq/MyAgents/投稿专家/references/`，可直接读取）：
- `期刊规则Schema与检查类型.md`：规则字段、类别、check_type、抽取与置信度、缓存管理
- `稿件解析与格式转换.md`：docx/tex/pdf/bib 解析、结构对象、引用格式转换
- `合规诊断与修订风险分级.md`：诊断流程、等级、修订分级、留痕与回滚
- `投稿材料模板与写作指南.md`：Cover Letter/Highlights/声明/Response to Reviewers
- `学术伦理与投稿红线.md`：一稿多投、署名、利益冲突、数据完整性、AI 使用边界
- `主要出版商作者指南要点.md`：Elsevier/Springer/Wiley/IEEE 等共性要点与查询入口
> 字数限制、参考文献格式、伦理条款、模板要求以**目标期刊官网现行 Guide for Authors** 为准（复核入口见 `references/README.md`）。

## 工具选型（参考）
| 组件 | 方案 |
|---|---|
| 主模型 | 规则抽取、诊断解释、文本修订、材料生成 |
| 规则引擎/小模型 | 字数统计、引用格式检查、正则匹配 |
| 向量检索 | 期刊指南分块做 RAG，避免长上下文 |
| 文档解析 | python-docx、pandoc、LaTeX/PDF 解析器 |
| 参考文献 | Crossref API、DOI 解析、BibTeX |
| 抓取 | HTTP 客户端 + HTML 解析器 |
| 存储/队列 | PostgreSQL/SQLite + 对象存储；Celery 等 |

## 关联
- 上游：种植/育种/育苗/发酵/食品加工/食品安全/营养/检测专家（学科内容与数据）
- 下游：文档专家（排版、图表、按期刊模板导出 Word/LaTeX/PDF）
