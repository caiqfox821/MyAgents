# MyAgents — 领域专家 Agent 库

面向「健康食品与现代农业」的 opencode 专家 agent 集合：协调、种植、育种、育苗、发酵、食品加工、食品安全、营养、检测、质谱、毒理、文档（PPT/Word）、投稿（外文期刊）。

## 目录结构

```
MyAgents/
├── opencode.json                 # 项目配置（default_agent、skills.paths、references）
├── install.sh                    # 安装/同步脚本（全局或项目、链接或复制）
├── README.md
├── 公共知识/                   # 全局共享（所有专家共用，只读）
│   ├── 政策法规与规划/           # 官方政策、规划、批复文件
│   ├── 标准规范/                 # 标准要点与查询入口
│   ├── 技术指南/                 # 通用技术指南 + **风险评估-证据条目与出处.md**（L3 原著条目底座，公共技能 risk-assessment 共用）
│   ├── 书库/                     # 开放获取全文库：WHO/FAO EHC 240 章节 + MDPI 专著 + EuropePMC OA 文献（含 tools/ 检索与按页取证）
│   ├── 案例库/                   # 跨领域共享案例
│   └── 知识图谱/
├── 公共技能/                     # 全局共享技能（所有专家可用）
│   ├── skills/togomcp-sparql/    # TogoMCP/RDF Portal 生命科学数据库 SPARQL 查询技能
│   └── skills/risk-assessment/   # 跨域风险评估方法技能（SKILL + 6 份方法文件 + scripts/riskcalc.py + 报告模板；证据条目指向 公共知识/书库）
├── 协调专家/                     # orchestrator：总协调 / 路由
│   ├── agent.md
│   ├── skills/orchestration/SKILL.md
│   ├── templates/
│   └── references/
├── 种植专家/
│   ├── agent.md                  # agent 定义（frontmatter + 提示词）
│   ├── skills/planting-knowledge/SKILL.md
│   ├── skills/plant-lstm/        # 可执行技能：LSTM 生长预测（SKILL.md + 参数库 + 使用说明书 + scripts/）
│   ├── templates/                # 方案/记录表模板（README 说明）
│   └── references/               # 种植知识库（栽培/粮油/园艺/药用食用菌/水稻/标准）+ 证据条目（原著深度消化）
├── 育种专家/
│   ├── agent.md
│   ├── skills/breeding-knowledge/SKILL.md
│   ├── templates/
│   └── references/               # 育种知识库（种质/途径/分子/抗性品质/审定制种/标准）+ 证据条目（原著深度消化）+ 书库 16 册 + 项目
├── 育苗专家/
│   ├── agent.md
│   ├── skills/nursery-knowledge/SKILL.md
│   ├── templates/
│   └── references/               # 育苗知识库（种子/基质/嫁接扦插/组培/工厂化/质量标准）+ 证据条目（原著深度消化）+ 书库 14 册 + 项目
├── 发酵专家/
│   ├── agent.md
│   ├── skills/fermentation-knowledge/SKILL.md
│   ├── skills/microbial-growth/  # 可执行技能：微生物生长拟合（SKILL.md + scripts/MicrobialGrowth.py）
│   ├── templates/
│   └── references/               # 发酵知识库（工艺/菌种/培养基/动力学/下游/标准）+ 证据条目（原著深度消化）+ 书库
├── 文档专家/
│   ├── agent.md
│   ├── skills/document-format/SKILL.md
│   ├── templates/                # 机构模板（实体文件，已迁入）
│   └── references/
├── 食品加工专家/
│   ├── agent.md
│   ├── skills/food-processing/SKILL.md
│   ├── templates/
│   └── references/               # 食品加工知识库（单元操作/配方/货架期/中试/标准）+ 证据条目（原著深度消化）+ 项目
├── 食品安全专家/
│   ├── agent.md
│   ├── skills/food-safety/SKILL.md
│   ├── templates/
│   └── references/               # 风险排序案例
├── 营养专家/
│   ├── agent.md
│   ├── skills/nutrition/SKILL.md       # 营养知识技能
│   ├── skills/nutritionist/            # 可执行技能：SKILL.md + scripts/nutritionist.py
│   ├── templates/
│   └── references/               # 营养知识库（DRIs/膳食/配餐/标签/人群运动/标准）
├── 检测专家/
│   ├── agent.md
│   ├── skills/detection-analysis/SKILL.md
│   ├── templates/
│   └── references/               # 检测知识库（方法学/前处理/验证/不确定度/认可/标准）+ 案例
├── 质谱专家/
│   ├── agent.md
│   ├── skills/mass-spectrometry/SKILL.md
│   ├── templates/                # MS 方法开发与验证记录表
│   └── references/               # 质谱知识库（仪器与电离/方法开发·定量·验证/谱图解析与未知物鉴定）
├── 毒理专家/
│   ├── agent.md
│   ├── skills/toxicology/SKILL.md
│   ├── templates/                # 毒理危害表征表
│   └── references/               # 毒理知识库（基础与危害识别/剂量反应与 HBGV/毒性终点/计算毒理与 NAMs/试验规范与数据质量）
├── 投稿专家/
│   ├── agent.md
│   ├── skills/journal-submission/SKILL.md
│   ├── templates/                # Cover Letter / Response to Reviewers / 投稿前检查清单
│   └── references/               # 期刊规则 Schema、稿件解析、诊断修订、投稿材料、伦理红线、出版商指南
└── .opencode/
    ├── agent/                    # → 各专家 agent.md 的软链接（项目模式）
    └── skills/                   # → 各专家 skills 的软链接（项目模式）
```

> `.opencode/` 中的软链接让 opencode 在项目模式下自动发现专家；`agent.md` 与 `skills/` 是唯一事实来源。

### 风险评估的归属（三个角色的分界）

| 问题 | 归属 | 载体 |
|---|---|---|
| 「风险有多大」：暴露、HQ/MOE/ILCR、概率评估、排序 | **公共技能 `risk-assessment`**（各专家按需加载执行） | 方法 + 脚本，跨域复用 |
| 「毒性凭什么」：证据权重、POD/BMD、HBGV 推导、TTC/read-across | **毒理专家** | `toxicology` 技能 + 私有知识库 |
| 「是否超标、怎么管」：GB 限量比对、合规判定、HACCP、处置建议 | **食品安全专家** | `food-safety` 技能 + 私有知识库 |

> 这样划分的理由：风险评估是**方法**（跨域复用，宜为公共技能），毒理是**独立专业深度**（宜为 agent），限量合规是**管理判定**（留在食品安全专家）。三者不得互相替代。

### 知识库分层（公共 vs 私有）

- **公共知识（共享）**：顶层 `公共知识/`，经 `opencode.json` 的 `references` 注册为全局引用，**所有专家共用、只读**；存放政策法规、标准规范、技术指南、跨领域案例与知识图谱。法规/标准/政策/案例类查询优先到此。
- **公共技能（共享）**：顶层 `公共技能/skills/`，经 `install.sh` 软链接到全局技能目录，**所有专家可加载**；存放跨领域的**工具/方法型**技能：`togomcp-sparql`（查询 MediaDive/BacDive/BRENDA/MassBank/ChEBI 等 47 个生命科学数据库）、`risk-assessment`（风险评估四步法、EDI/ESTI/IESTI、HQ/MOE/ILCR、Monte Carlo、风险排序，含可执行 `riskcalc.py`）。与公共知识分工：前者是**方法与工具**，后者是**知识与资料**。
- **私有知识库（隔离）**：各专家目录下的 `references/` 与 `skills/`，仅本专家职责范围使用；`agent.md` 只索引本目录的 `references/README.md`，不直接引用其他专家的私有库。
- **跨界资料**：同时服务多个领域的资料（如"育种+育苗一体化"建议）统一上移到 `公共知识/案例库/`，由相关专家以软链接共享，避免在各私有库重复存放。
- 维护 `公共知识/` 时保持**只读约定**：内容变更需在 `EVOLUTION.md` 登记；各私有库不得写入公共库。

## 专家清单

| Agent 名 | 中文 | 职责 |
|---|---|---|
| `orchestrator` | 协调专家 | 任务拆解、专家路由、交接管理、汇总校验（默认入口，mode=primary） |
| `planting-expert` | 种植专家 | 栽培、水肥、植保、生长模型、品质逆境 |
| `breeding-expert` | 育种专家 | 种质资源、选择/杂交/分子育种、品种审定、制种 |
| `nursery-expert` | 育苗专家 | 播种催芽、基质与穴盘、嫁接/扦插/组培、工厂化育苗 |
| `fermentation-expert` | 发酵专家 | 菌种、发酵工艺、动力学建模、下游纯化与膜分离 |
| `document-expert` | 文档专家 | PPT/Word 生成与排版、套用公文/报告/申报模板 |
| `food-processing-expert` | 食品加工专家 | 配方、单元操作、中试放大、货架期、HACCP |
| `food-safety-expert` | 食品安全专家 | 风险评估四步法、风险排序、限量合规、HACCP 危害分析 |
| `nutrition-expert` | 营养专家 | 能量与营养素测算、DRIs/NRV、配餐推荐、营养标签 |
| `detection-expert` | 检测专家 | 检测方法与开发、前处理、仪器分析、方法验证、质量体系 |
| `mass-spec-expert` | 质谱专家 | 质谱仪器与电离选型、方法开发与参数优化、谱图解析、定量与基质效应、未知物鉴定、组学数据处理 |
| `toxicology-expert` | 毒理专家 | 毒性证据与证据权重、POD/HBGV 推导、BMD 建模、遗传毒/致癌/DART、TTC/read-across、OECD TG/GLP |
| `submission-expert` | 投稿专家 | 期刊规则获取与结构化、稿件合规诊断、定向修订、Cover Letter/Highlights/声明、审稿意见回复 |

除 `orchestrator`（`primary`，默认入口）外，其余专家模式均为 `all`：既可手动选择为主 agent，也可被 orchestrator 作为子 agent 调用。复合任务交给 `orchestrator`，它会自动路由到对应专家。

## 使用方式

### 方式一：项目模式
在 `MyAgents` 目录下启动 opencode：

```bash
cd /home/caiq/MyAgents
opencode
```

项目 `.opencode/agent` 与 `.opencode/skills` 会被自动加载。

### 方式二：全局模式
已通过 `install.sh` 把 13 个 agent 与 18 个技能软链接到 `~/.config/opencode/`，在任何目录启动 opencode 均可用。

### 维护命令

```bash
cd /home/caiq/MyAgents
./install.sh            # 软链接到全局 ~/.config/opencode（默认）
./install.sh --copy     # 复制到全局（源更新后需重跑）
./install.sh --project  # 仅刷新项目 .opencode 链接
```

## 进化闭环（评估 / 复盘 / 变更）

以「评估 → 复盘 → 固化 → 回归」持续提升专家能力：

| 目录 / 文件 | 作用 |
|---|---|
| `evals/` | 可复现的验收用例（人工按 rubric 打分），见 `evals/README.md` |
| `retrospectives/` | 交付/失败后的复盘，产物是**文件变更清单** |
| `EVOLUTION.md` | 进化日志，记录每次结构性变更 |
| `scripts/new-eval.sh` | 新增评估用例：`scripts/new-eval.sh 种植专家 soil-fertigation` |
| `scripts/new-retro.sh` | 新增复盘：`scripts/new-retro.sh 种植专家 番茄施肥返工` |

流程：挑用例运行 → 按 rubric 打分 → 写复盘定位根因 → 改 `agent.md`/`SKILL.md`/`references/` → 更新 `EVOLUTION.md` → 重跑用例回归。**失败一个用例，就应产出一条固化动作。**

## 说明与约定

- **唯一事实来源**：修改 `<专家目录>/agent.md` 或 `skills/*/SKILL.md`；项目与全局链接自动生效。
- **模型**：未在 agent 中指定，继承全局默认 `paratera/DeepSeek-V4-Flash`。
- **模板依赖**：文档专家的 `templates/` 为本地实体文件（已从 `/home/caiq/project/template` 迁入）；多数 `references/` 仍为软链接，指向 `Tsaiskills` 等既有资源。
- **内置技能复用**：文档专家可直接调用全局内置技能 `pptx`、`docx`、`official-document`、`scientific-report`、`xlsx`、`mindmap`。
- **改动后需重启 opencode**：配置与 agent 在启动时加载，不热更新。

## 新增一个专家

1. 新建目录 `新专家/`，含 `agent.md`、`skills/<skill-name>/SKILL.md`、`templates/`、`references/`。
2. 在 `install.sh` 的 `AGENTS` 与 `SKILLS` 数组中加入对应行。
3. 运行 `./install.sh`，重启 opencode。
