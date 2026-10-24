# MyAgents 专家 Agent 体系图

> 对象：`/home/caiq/MyAgents` —— 面向「健康食品与现代农业」的 opencode 领域专家 Agent 库
> 基线：`2026-10-23`（git tag `baseline-2026-10-23`）｜模型：继承全局默认 `paratera/DeepSeek-V4-Flash`
> 事实来源：各专家 `agent.md`、`skills/*/SKILL.md`、`install.sh`、`opencode.json`、`EVOLUTION.md`、`evals/registry.md`

本目录含 5 张图（PNG / SVG 双份，矢量可放任意大）与源文件 `mmd/*.mmd`：

| 图 | 内容 | 文件 |
|---|---|---|
| ① 体系总览 | 入口层 → 领域专家层 → 支撑层 → 交付物 + 进化闭环 | `01-总览.png / .svg` |
| ② 分层与边界 | 私有事实来源 / 公共只读层 / 全局内置 / 边界纪律 | `02-分层.png / .svg` |
| ③ 业务协作流 | 生产端 → 加工端 → 评价端 → 交付端的真实依赖链 | `03-协作流.png / .svg` |
| ④ 进化闭环 | 评估 → 复盘 → 固化 → 登记 → 版本化 → 回归 | `04-进化闭环.png / .svg` |
| ⑤ 部署加载机制 | `install.sh` 三种模式与启动加载 | `05-部署机制.png / .svg` |

**另外两件成品**

| 成品 | 说明 | 文件 |
|---|---|---|
| 全集 PNG | 5 张图纵向拼合（含页头 / 小标题 / 说明 / 页脚），单张查看或贴文档用 | `MyAgents-体系图-全集.png`（1776×10467） |
| 演示 PPT | **长三院简洁模板样式**（深蓝 #1A3C6E 标题带 + 蓝色强调线，封面/分隔页满版深蓝，页脚「浙江清华长三角研究院」+ 页码），16:9、**19 页**：封面 · 目录 · 体系速览 · 5 组［分隔页 + 图页］· 专家清单 2 页 · 公共层与边界 · 关键统计与维护 · 结尾 | `MyAgents-体系图.pptx` |

生成脚本：`compose_all.py`（拼全集 PNG，依赖 Pillow）、`make_ppt.py`（生成 PPT，依赖 python-pptx + Pillow）。

**PPT 版式来源**：样式取自文档专家 `文档专家/templates/ppt-长三院简洁模板-template.md` 与同目录 `generate_pptx.py`（原 `.pot` 为 WPS 创建的 97-2003 格式，`python-pptx` 无法直接打开，故按其视觉规范重绘）：

| 元素 | 规范 |
|---|---|
| 主色 | 深蓝 `#1A3C6E`（标题带 / 封面 / 分隔页 / 表头） |
| 强调色 | 蓝 `#2E75B6`（色条、项目符、页码装饰） |
| 正文 / 底纹 | `#333333` / `#F2F5FA` |
| 字体 | 中文 微软雅黑，西文 Arial（已同时写入 `a:latin` `a:ea` `a:cs`） |
| 版式 | 封面满版深蓝；分隔页大号色块序号；内容页顶部标题带 + 页脚研究院名 + `n/N` 页码；表格 No-Style-No-Grid + 深蓝表头 |

---

## ① 体系总览

![体系总览](01-总览.png)

```mermaid
flowchart TB
  U(["用户需求 / 复合任务"])
  ORCH["<b>协调专家 orchestrator</b>　mode = primary · 默认入口<br/>澄清目标 · 任务拆解 · 专家路由 · 交接协议 · 汇总校验 · 交付验收"]
  U --> ORCH
  ORCH ==> E
  subgraph E["领域专家层 · 12 个 · mode = all（可作主 agent，也可被 orchestrator 调用）"]
    P1["种植专家<br/>planting-expert"]
    P2["育种专家<br/>breeding-expert"]
    P3["育苗专家<br/>nursery-expert"]
    P4["发酵专家<br/>fermentation-expert"]
    P5["食品加工专家<br/>food-processing-expert"]
    P6["食品安全专家<br/>food-safety-expert"]
    P7["营养专家<br/>nutrition-expert"]
    P8["毒理专家<br/>toxicology-expert"]
    P9["检测专家<br/>detection-expert"]
    P10["质谱专家<br/>mass-spec-expert"]
    P11["文档专家<br/>document-expert"]
    P12["投稿专家<br/>submission-expert"]
    P1 ~~~ P2 ~~~ P3 ~~~ P4
    P5 ~~~ P6 ~~~ P7 ~~~ P8
    P9 ~~~ P10 ~~~ P11 ~~~ P12
    P1 ~~~ P5 ~~~ P9
  end
  E ==> OUT(["交付物：方案 / 报告 / 数据 / PPT / 投稿材料包"])
  subgraph S["支撑层（所有专家共用）"]
    direction LR
    SK["<b>技能 19</b>　公共 2 + 私有 17<br/>公共：risk-assessment · togomcp-sparql<br/>私有：orchestration/plant-lstm/microbial-growth/nutritionist/spectral-matching 等"]
    KN["<b>知识</b><br/>公共知识（只读）：政策法规 · 标准规范 · 技术指南 · 案例库 · 知识图谱 · 书库<br/>私有：各专家 references/ + templates/"]
    TL["<b>工具</b><br/>内置技能 pptx · docx · official-document · scientific-report · xlsx · mindmap<br/>脚本 riskcalc.py · plant_lstm.py · MicrobialGrowth.py · nutritionist.py · spectral-matching"]
  end
  E -. 调用 .-> S
  S -. 支撑 .-> E
  subgraph EV["进化闭环（评分人工启动 · 演化人工裁定）"]
    direction LR
    V1["评估<br/>evals/"] --> V2["复盘<br/>retrospectives/"] --> V3["固化<br/>agent.md · SKILL.md · references/"] --> V4["登记<br/>EVOLUTION.md"] --> V5["版本化<br/>git · 可回滚"]
  end
  OUT -. 反馈 .-> EV
  V3 -. 回写 .-> E
```

**读法**：13 个 agent 中只有 `orchestrator` 是 `primary`（默认入口）；其余 12 个是 `mode: all`，既可被手动选为主 agent 单干，也可被 orchestrator 当子 agent 调用。专家不直接互相读对方私有库，跨域资料统一上移到公共层。

---

## ② 分层与边界

![分层与边界](02-分层.png)

```mermaid
flowchart TB
  subgraph L1["① 入口 / 编排"]
    OR["协调专家 orchestrator<br/>13 个 agent 中唯一的 primary"]
  end
  subgraph L2["② 私有事实来源（各专家目录，可写）"]
    direction LR
    A1["agent.md<br/>角色 · 能力 · 工作方法 · 输出规范 · 协作关系"]
    A2["skills/&lt;name&gt;/SKILL.md<br/>私有技能"]
    A3["references/<br/>私有知识库 · 证据条目 · 书库"]
    A4["templates/<br/>记录表 · 报告模板"]
  end
  subgraph L3["③ 公共层（所有专家共用，只读）"]
    direction LR
    C1["公共技能/skills/<br/>risk-assessment · togomcp-sparql"]
    C2["公共知识/<br/>政策法规与规划 · 标准规范 · 技术指南 · 案例库 · 知识图谱 · 书库"]
  end
  subgraph L4["④ 全局内置（opencode 自带，跨项目可用）"]
    direction LR
    G1["pptx · docx · official-document"]
    G2["scientific-report · xlsx · mindmap"]
    G3["MCP：freecad · papers · togomcp"]
  end
  OR --> L2
  L2 -- 引用 --> L3
  L2 -- 调用 --> L4
  subgraph L5["边界纪律"]
    direction LR
    R1["三问分界<br/>风险多大 → risk-assessment<br/>毒性凭什么 → 毒理专家<br/>是否超标 → 食品安全专家"]
    R2["公共库只读<br/>变更须登记 EVOLUTION.md"]
    R3["私有库隔离<br/>agent.md 只索引本目录 references/"]
    R4["跨界资料上移<br/>公共知识/案例库/ 软链共享"]
  end
  L3 --- L5
```

---

## ③ 业务协作流（跨专家真实依赖链）

![业务协作流](03-协作流.png)

```mermaid
flowchart LR
  REQ(["需求 / 样品 / 数据 / 稿件"])
  subgraph CHAIN["业务链路：从原料到交付"]
    direction LR
    subgraph UP["生产端"]
      direction TB
      BR["育种专家"]
      NU["育苗专家"]
      PL["种植专家"]
    end
    subgraph MID["加工端"]
      direction TB
      FE["发酵专家"]
      FP["食品加工专家"]
    end
    subgraph ASSESS["评价端"]
      direction TB
      DT["检测专家"]
      MS["质谱专家"]
      TX["毒理专家"]
      FS["食品安全专家"]
      NT["营养专家"]
    end
    subgraph DELIV["交付端"]
      direction TB
      DC["文档专家"]
      SB["投稿专家"]
    end
  end
  REQ --> UP
  BR --> NU --> PL
  PL --> FE
  PL --> FP
  FE --> FP
  FP --> FS
  FP --> NT
  DT --> FS
  DT --> NT
  MS -. 深度环节 .-> DT
  TX -. POD / HBGV .-> FS
  FS --> NT
  UP --> DC
  MID --> DC
  ASSESS --> DC
  DC --> SB
  OR["协调专家 orchestrator<br/>（跨域任务的总入口，负责编排以上链路）"]
  OR -. 路由 / 汇总 .-> CHAIN
```

**三条支撑线**（易混，图里用虚线标出）：

- **质谱专家 → 检测专家**：检测专家管全局标准/前处理/质量体系；质谱专家管质谱深度环节（电离与分析器选型、碎裂规律、MRM/HRMS、未知物鉴定）。
- **毒理专家 → 食品安全专家**：毒理专家产出**毒性凭什么**（POD / HBGV / 证据权重）；食品安全专家做**是否超标**（限量比对、合规判定、HACCP）。
- **风险评估（公共技能）** 贯穿两者：只做**风险多大**（暴露、HQ/MOE/ILCR、概率评估、排序），三者互不替代。

---

## ④ 进化闭环

![进化闭环](04-进化闭环.png)

```mermaid
flowchart LR
  T1["① 挑用例运行<br/>evals/（13 专家 + 公共技能，15 个 P0 用例）"]
  T2["② 按 rubric 打分<br/>0 / 1 / 2 加权 · 红线检查"]
  T3["③ 复盘定位根因<br/>retrospectives/ → 产物＝文件变更清单"]
  T4["④ 固化<br/>改 agent.md · SKILL.md · references/"]
  T5["⑤ 登记<br/>EVOLUTION.md 追加一行"]
  T6["⑥ 版本化<br/>git 提交 · 可 revert 回滚"]
  T7["⑦ 回归<br/>重跑用例验证"]
  T1 --> T2 --> T3 --> T4 --> T5 --> T6 --> T7 --> T1
  G1["治理原则<br/>评分由人工启动 · 演化决策由人工最终裁定<br/>系统只记录与可回滚，不自行改文件"]
  B1["当前基线<br/>tag baseline-2026-10-23"]
  G1 -.约束.-> T1
  B1 -.起点.-> T6
```

规则：**失败一个用例，就应产出一条固化动作**。首次全量评分为 15/15 通过（自动预评，最终裁定留人工）。

---

## ⑤ 部署与加载机制

![部署机制](05-部署机制.png)

```mermaid
flowchart TB
  SRC["<b>唯一事实来源</b><br/>MyAgents/&lt;专家目录&gt;/agent.md<br/>skills/*/SKILL.md · references/ · templates/"]
  INS["install.sh<br/>AGENTS 13 项 · SKILLS 19 项"]
  SRC --> INS
  INS -->|默认 link| G["~/.config/opencode/<br/>agents/ + skills/ 软链<br/>任何目录可用"]
  INS -->|--project| P["MyAgents/.opencode/<br/>agent/ + skills/ 软链<br/>项目模式自动加载"]
  INS -->|--copy| C["复制快照<br/>源更新后需重跑"]
  CFG["MyAgents/opencode.json<br/>default_agent = orchestrator<br/>skills.paths · references = 公共知识"]
  CFG --> G
  CFG --> P
  G --> RUN["opencode 启动时加载<br/>（配置与 agent 不热更新，改动后需重启）"]
  P --> RUN
```

改 `agent.md` / `SKILL.md` 即改行为——项目与全局软链自动生效，**但要重启 opencode**。

---

## 附录 A　专家 ↔ 技能 ↔ 知识 映射

`★` = 可执行技能（带脚本，可直接跑）。

| # | 专家 | agent id | mode | temp | 私有技能 | 私有知识库 `references/` |
|---|---|---|---|---|---|---|
| 1 | 协调专家 | `orchestrator` | **primary** | 0.2 | `orchestration` | 编排模式与路由、跨专家工作流与场景（6 个端到端）、汇总质检与输出规范 |
| 2 | 种植专家 | `planting-expert` | all | 0.3 | `planting-knowledge`、`plant-lstm` ★ | 栽培/粮油/园艺/药用食用菌/水稻/标准 ＋ 证据条目 61+47 条 ＋ 书库 48 册 |
| 3 | 育种专家 | `breeding-expert` | all | 0.25 | `breeding-knowledge` | 种质/途径/分子/抗性品质/审定制种/标准 ＋ 证据条目 64 条 ＋ 书库 16 册 ＋ 文献清单 |
| 4 | 育苗专家 | `nursery-expert` | all | 0.3 | `nursery-knowledge` | 种子/基质/嫁接扦插/组培/工厂化/质量标准 ＋ 证据条目 60 条 ＋ 书库 14 册 |
| 5 | 发酵专家 | `fermentation-expert` | all | 0.3 | `fermentation-knowledge`、`microbial-growth` ★ | 工艺与参数/菌种/培养基/动力学/下游/标准 ＋ 证据条目 46 条 ＋ 书库 34 册 |
| 6 | 食品加工专家 | `food-processing-expert` | all | 0.3 | `food-processing` | 单元操作/配方/货架期/中试/标准 ＋ 证据条目 51 条 ＋ 书库 118 册/篇 |
| 7 | 食品安全专家 | `food-safety-expert` | all | 0.2 | `food-safety` | 标准法规/化学危害/生物危害/评估方法/检测监测与 HACCP/国际机构 ＋ 风险排序案例 |
| 8 | 营养专家 | `nutrition-expert` | all | 0.3 | `nutrition`、`nutritionist` ★ | DRIs/膳食成分/配餐/标签/人群运动/标准 ＋ 证据条目 47 条 ＋ WHO 指南条目 ＋ 书库 221 册 |
| 9 | 检测专家 | `detection-expert` | all | 0.2 | `detection-analysis` | 方法学与仪器分析/前处理/方法验证与质控/不确定度/CNAS-CMA ＋ 能力评价案例 |
| 10 | 质谱专家 | `mass-spec-expert` | all | 0.2 | `mass-spectrometry`、`spectral-matching` ★ | 仪器与电离/方法开发定量验证/谱图解析与未知物鉴定 ＋ 证据条目 74 条 ＋ 本地谱库 3 套 |
| 11 | 毒理专家 | `toxicology-expert` | all | 0.2 | `toxicology` | 危害识别/剂量反应与 HBGV/毒性终点/计算毒理与 NAMs/试验规范与数据质量 ＋ 证据条目 104 条 |
| 12 | 文档专家 | `document-expert` | all | 0.4 | `document-format` | 7 份文档模板 ＋ 6 份 PPT 模板 ＋ `generate_pptx.py`；复用内置 `pptx/docx/official-document/scientific-report/xlsx/mindmap` |
| 13 | 投稿专家 | `submission-expert` | all | 0.3 | `journal-submission` | 期刊规则 Schema/稿件解析/合规诊断与修订分级/投稿材料/伦理红线/出版商要点 ＋ 规则缓存（ISSN 为唯一键） |

## 附录 B　公共层清单

**公共知识**（`opencode.json` 注册为全局 `references`，所有专家共用、只读）

| 分区 | 内容 |
|---|---|
| `政策法规与规划/` | 官方政策、规划、批复文件（含盖章件） |
| `标准规范/` | 标准要点与查询入口（不整篇下载） |
| `技术指南/` | 通用技术指南 ＋ **L3 原著证据条目 80 条**（公共技能 `risk-assessment` 的证据底座） |
| `案例库/` | 跨领域共享案例（多专家软链共享） |
| `知识图谱/` | 结构化知识；技能 `togomcp-sparql` 可查 **47 个 RDF 数据库** |
| `书库/` | 开放获取全文库 **815 MB**：WHO/FAO EHC 240 章节 4 篇、ICH M7(R2)(2023)、SANTE/11312/2021 v2026、MDPI Books 24 册、机构/OECD 指南 17 份、EuropePMC OA 全文 176 篇，配检索/按页取证工具 |

**公共技能**：`risk-assessment`（四步法、EDI/ESTI/IESTI、HQ/MOE/ILCR、Monte Carlo、风险排序，含可执行 `riskcalc.py`）、`togomcp-sparql`（TogoMCP / RDF Portal 查询规范）。

## 附录 C　关键统计

| 指标 | 数值 |
|---|---|
| Agent 总数 | **13**（1 primary + 12 `mode: all`） |
| 技能总数 | **19**（公共 2 + 私有 17，其中可执行 5） |
| 公共 L3 证据条目 | **80 条**（`公共知识/技术指南/风险评估-证据条目与出处.md`） |
| 三份核心 L3 合计 | **258 条**（公共 80 ＋ 毒理 104 ＋ 质谱 74） |
| 各专家私有 L3 | 营养 47 · 种植 61+47 · 发酵 46 · 食品加工 51 · 育种 64 · 育苗 60 |
| 公共书库 | 815 MB（EHC 240 4 篇 ＋ ICH M7(R2) ＋ SANTE v2026 ＋ MDPI 24 册 ＋ OECD 指南 17 份 ＋ OA 176 篇） |
| 私有书库（PDF 册/篇） | 种植 48 · 育种 16 · 育苗 14 · 发酵 34 · 食品加工 118 · 营养 221 |
| 本地质谱谱库 | 人参 1778 条 · 金线莲 2387 条 · **合并检索 2954 条**（跨库去重 1211） |
| 评估用例 | 15 个 P0，首轮 **15/15 通过**（自动预评） |
| 版本基线 | git tag `baseline-2026-10-23` |

---

## 重新生成

```bash
cd MyAgents/体系图

# 1) 单张重渲染（改 mmd/*.mmd 后）
mmdc -p puppeteer-config.json -i mmd/01-总览.mmd -o 01-总览.svg -b white
mmdc -p puppeteer-config.json -i mmd/01-总览.mmd -o 01-总览.png -b white -w 1634 -s 2

# 2) 拼全集 PNG
python3 compose_all.py

# 3) 重新生成 PPT
python3 make_ppt.py
```

- `puppeteer-config.json` 指向本机 `chrome-headless-shell`（mermaid-cli 未内置浏览器时需要，换机器请改此路径）。
- `-w` 取该图 SVG 的自然宽度、`-s 2` 出 2 倍图；PNG 尺寸不必手工维护，见 `compose_all.py` 的量算逻辑。
- 改图只改 `mmd/*.mmd`，再重跑即可；**事实来源仍是各专家 `agent.md` 与 `SKILL.md`**，本目录只是它们的投影。
