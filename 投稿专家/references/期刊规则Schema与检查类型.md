# 期刊规则 Schema 与检查类型

> 用途：把非结构化的 Guide for Authors 转成可执行、可追溯、可复核的规则表。
> 约束：每条规则必须绑定原文片段与来源 URL；低置信度规则不自动执行。

## 一、规则对象字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `rule_id` | string | 规则唯一编号，建议 `期刊缩写-类别-序号`，如 `FC-ABS-01` |
| `category` | enum | 规则类别，见下节 |
| `description` | string | 面向用户的中文/英文说明，如"摘要不超过 250 词" |
| `check_type` | enum | 检查方式，见"检查类型" |
| `field` | string | 对应稿件字段，如 `abstract`、`keywords`、`references` |
| `min_value` / `max_value` | number | 数值阈值（字数、条数、分辨率等） |
| `allowed_values` | array | 枚举允许值（如引用样式） |
| `pattern` | string | 正则（如编号制引用 `\[\d+\]`） |
| `severity` | enum | `must` / `should` / `optional` / `uncertain` |
| `confidence` | 0–1 | 抽取置信度，低于阈值不自动执行（建议阈值 0.8） |
| `source_text` | string | 指南原文片段（证据） |
| `source_url` | string | 来源 URL |
| `crawl_time` | ISO8601 | 抓取时间 |
| `version` | string | 指南版本/更新时间（如可得） |

## 二、规则类别（category）

| 类别 | 关注点 | 典型规则 |
|---|---|---|
| `manuscript_structure` | 稿件组成 | 是否需要 Highlights / Keywords / Graphical Abstract / 结构化摘要 |
| `article_type` | 文章类型 | 仅限 Original Research / Review 等；不同类型字数与结构不同（如 Journal of Future Foods 仅收 Original Research Papers 与 Review Articles） |
| `abstract` | 摘要 | 字数上限、是否结构化、是否含关键词 |
| `references` | 参考文献 | 编号制 / 作者-年份制、DOI 要求、数量上限、格式样式 |
| `figures_tables` | 图表 | 图片格式（TIFF/EPS/PDF）、分辨率分档（如 Journal of Future Foods：半色调 ≥300 dpi、组合 ≥500 dpi、位图线图 ≥1000 dpi）、标题位置、单独上传 |
| `ethics` | 伦理与声明 | 伦理审批、利益冲突（官方模板要求）、作者贡献、知情同意 |
| `data_policy` | 数据 | Data Availability Statement、数据仓库要求（如 FAIR）；**注意：并非所有期刊都默认要求（如 Journal of Future Foods 官网清单未显式列出），须按规则驱动，不得默认生成** |
| `funding` | 资助 | 资助方名称及其在研究中的角色；无资助须声明 |
| `language` | 语言 | 英式/美式英语（有的刊禁止混用）、拼写与术语规范、包容性语言 |
| `submission_files` | 投稿文件 | 是否盲审（如 Journal of Future Foods 双盲，需匿名稿）、正文/图表/封面信是否分开上传、文件格式（如必须 Word）、文件命名 |
| `peer_review_model` | 审稿模式 | 单匿名 / 双匿名 / 开放评审；决定是否需要匿名版稿件 |
| `title_page` | 标题页 | 标题、作者与单位、通讯作者完整联系方式（email/邮址/电话/传真）、字数与图表数 |
| `word_limit` | 字数 | 正文/全文/各部分字数上限 |
| `supplementary` | 补充材料 | 补充文件格式、命名（S1/Fig. S1）、引用方式 |

## 三、检查类型（check_type）

| check_type | 含义 | 判定方式 |
|---|---|---|
| `word_count` | 字数检查 | 统计 `field` 字数与阈值比较 |
| `count` | 条数检查 | 关键词条数、参考文献数量 |
| `exists` | 存在性检查 | 声明/章节/元素是否存在 |
| `regex` | 样式匹配 | 引用格式、编号、单位符号 |
| `enum` | 枚举检查 | 取值为允许集合之一 |
| `file_format` | 文件格式 | 图表/附件格式 |
| `language_style` | 语言风格 | 英式/美式拼写一致性 |
| `manual` | 人工确认 | 无法自动判定，标记 `uncertain` 交作者 |

## 四、抽取流程

1. **定位指南正文**：去导航/广告/页脚，保留"Preparation / Submission / Ethics / References"等章节。
2. **分块**：按标题层级分块，便于 RAG 与逐块抽取。
3. **抽取**：按上表 Schema 生成候选规则，每条附 `source_text`。
4. **置信度打分**：明确陈述 → 高；模糊/多义/跨句推断 → 低，标记 `uncertain`。
5. **去重与合并**：同字段多来源冲突时保留更权威（官网）来源并标注差异。
6. **落库**：写入期刊规则库，记录 URL、抓取时间、版本。

## 五、缓存与版本管理

- 同一期刊设 TTL（如 7–30 天）自动刷新；手动可强制刷新。
- 指南变更时保留历史版本，诊断报告注明所用规则版本。
- 官网与第三方规则冲突时**以官网为准**，并保留冲突记录。

## 六、抽取示例

```json
{
  "rule_id": "FC-REF-01",
  "category": "references",
  "description": "正文引用与参考文献表采用 APA 第 7 版（作者-年份制）",
  "check_type": "regex",
  "field": "references",
  "severity": "must",
  "confidence": 0.95,
  "source_text": "Citations in the text should follow the referencing style used by the American Psychological Association. ... Seventh Edition (2020)",
  "source_url": "https://www.sciencedirect.com/journal/food-control/publish/guide-for-authors",
  "crawl_time": "2026-10-05T00:09:17+08:00"
}
```

## 七、待核实清单

- [x] 目标期刊指南的抓取入口与 TTL 策略（已建 `常用目标期刊规则缓存.md`；Journal of Future Foods、**Food Control** 已核实完整规则，后者据 2026-10-05 官方 Guide 完整快照）
- [ ] Future Foods、The Lancet Diabetes & Endocrinology 官网 Guide for Authors 因 403 待人工补录
- [ ] 低置信度规则的人工复核流程
- [ ] 版本变更的告知与回归机制
- [ ] 多源 APC / 影响因子数值不一致时的官网核实流程（如 Future Foods APC 2560/1990/1800 三源不一致）

> **注意**：本节示例已按 Food Control 官方 Guide for Authors（2026-10-05 完整快照）校正为 **APA 第 7 版作者-年份制**。Food Control **不是编号制**——早期占位的 "FC-REF-02 编号制" 系错误示例，已废止；现行规则以 `常用目标期刊规则缓存.md` 第三节 FC-REF-01/02 为准。
