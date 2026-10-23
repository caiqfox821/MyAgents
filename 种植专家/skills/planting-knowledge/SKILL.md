---
name: planting-knowledge
description: 种植领域知识库与作业清单。用于作物/药用植物/食用菌的栽培方案、水肥管理、病虫害绿色防控、逆境应对、生长模型与产量品质调控。当制定种植方案、田间诊断或育种计划时加载。
---

# 种植知识技能

## 何时使用
用户提出种植/栽培/育种/土肥水/植保/设施农业/生长模型相关任务，需要结构化方案或诊断时。

## 方案输出清单（按需取用）

### 1. 栽培方案
- 品种选择与依据（适应性、抗性、市场）
- 播期与密度、育苗与移栽、生育期划分
- 设施环境目标（昼/夜温、光照、湿度、CO₂）
- 关键农事历（播种/定植/追肥/灌溉/采收节点）

### 2. 土肥水
- 测土配方：目标产量 × 单位养分需求 − 土壤供肥 = 施肥量
- 养分（N-P-K-Ca-Mg + 微量元素）分次施用比例
- 水肥一体化：EC/pH 目标、灌溉频次与单次水量
- 盐碱/酸化土壤改良措施

### 3. 植保（绿色防控优先）
- 病害：真菌/细菌/病毒判别要点
- 虫害：监测（黄板/性诱/灯诱）与防治阈值
- 措施优先级：农业防治 > 物理/生物防治 > 精准化学防治
- 用药三要素：药剂、浓度/剂量、**安全间隔期**

### 4. 逆境胁迫
- 干旱、渍涝、低温/霜冻、高温、盐碱、弱光
- 每类给出预警指标 + 应急措施 + 恢复管理

### 5. 生长模型
- Logistic：`C = A / (1 + (A/C0 − 1)·exp(−μ·t))`
- Gompertz：`C = A·exp(−exp((λ−t)·μ/A + 1))`
- 参数含义：C0 初始、A 最大、μ 速率、λ 迟滞期
- 拟合流程：数据清洗 → 初值设定 → 非线性回归 → 残差检验 → 预测

## 诊断决策树（田间问题）
1. 大面积连片 vs 零星分布 → 环境/管理 vs 病虫害
2. 有无明确病斑/虫体/霉层 → 生物因素
3. 老叶先发 vs 新叶先发 → 移动性养分缺乏（N/Mg/K vs Fe/Ca/B）
4. 昼夜/边际差异 → 温度、水分、设施问题

## 关键计量与标准
- 施肥量换算：1 亩 = 667 m²；纯养分 = 实物量 × 含量
- 农药标签核对：登记作物、防治对象、剂量、安全间隔期
- 记录：产地环境、投入品、农事活动（GAP 追溯）

## 参考资源（`references/`，详见 README.md 索引）
- 栽培技术-综合篇.md：土肥水、水肥一体化、育苗移栽、设施环境、绿色防控、逆境、生长模型
- 作物栽培-粮油作物.md：水稻、小麦、玉米、大豆、马铃薯、油菜
- **水稻栽培-证据条目与出处.md**：水稻原著深度消化，含生态区/水肥/密度/产量差/病虫草害/抗逆育种/ORYZA 模型的**可引用数据条目 + 出处页码**（做水稻方案时优先取用）
- **作物栽培-综合证据条目与出处.md**：综合农学原著深度消化，含养分管理与 4R/NUE、保护性耕作（CA/NT/残茬）、植保与生物防治、非生物胁迫、小麦、分子育种的**可引用数据条目 + 出处页码**（做小麦/大田/土壤植保方案时优先取用）
- 作物栽培-园艺作物.md：蔬菜、果树、茶叶、花卉
- 栽培-药用植物与食用菌.md：药用植物 GAP、食用菌栽培
- 标准规范-种植业.md：GAP、绿色食品、有机、测土配方、农药安全、农产品质量安全
- 独立技能 `plant-lstm`：植物生长/功效成分 LSTM 时序预测（参数库、使用说明书与脚本 `scripts/plant_lstm.py` 均在该技能目录内）
- 关联：育种专家（品种）、育苗专家（种苗）、食品安全专家（农残/重金属/毒素源头控制）、营养专家（营养成分/品质）

### 开放获取电子书库（`references/books/`，48 册，含水稻专题 28 册）

书库位于 `/home/caiq/MyAgents/种植专家/references/books/`，含 IRRI/Springer/CGIAR/IntechOpen/MDPI/WUR 等开放获取专著与手册。**水稻专题（28 册）**覆盖：综合与年鉴（Rice Almanac）、栽培手册（CGIAR/AfricaRice）、产量差与绿色革命（Springer《Closing Rice Yield Gaps in Asia》）、水肥管理（Water-wise、灌溉培训指南、氮素管理）、病虫害与杂草（病虫害图鉴、亚洲稻田杂草图鉴）、分子/遗传育种（MDPI 系列）、生长模型（WUR《ORYZA》）。
**全文检索（需要原著细节、试验数据、图鉴、页码时优先使用）**：

```bash
python3 /home/caiq/MyAgents/种植专家/references/books/tools/search_books.py "rice blast" --context 1
python3 /home/caiq/MyAgents/种植专家/references/books/tools/search_books.py "nitrogen" --books          # 各书命中统计
python3 /home/caiq/MyAgents/种植专家/references/books/tools/search_books.py "transplanting" --book rice  # 限定水稻
python3 /home/caiq/MyAgents/种植专家/references/books/tools/read_page.py Rice_Almanac 120               # 按页读原文
```

- **水稻问题检索建议**：病害/虫害→`"rice blast"`/`"brown planthopper"`；水肥→`"water management"`/`"nitrogen use efficiency"`；产量与产量差→`"yield gap"`；杂草→`"weed management"`；模型→`"ORYZA"`；育种→`"QTL"`/`"genomic selection"`；`--book rice` 可只搜水稻分区。

- 索引：`references/books/INDEX.md`（主题标签→书目）；单书目录 `references/books/toc/<分区>/<书名>.md`；全文 `references/books/text/<分区>/<书名>.txt`；元数据 `references/books/catalog.json`。
- 命中 `书|页码|原文` 后读 `toc/` 定位章节、`text/` 页码附近引用；引用注明 作者/编者、书名、出版社、年份、页码。
- 仅收录开放获取资源；商业版权教材只在 `references/books/README.md` 列正规获取入口，禁止臆造其内容。
