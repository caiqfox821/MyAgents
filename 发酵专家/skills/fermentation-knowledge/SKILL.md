---
name: fermentation-knowledge
description: 发酵工程知识库与工艺清单。用于菌种选育、培养基设计、液态/固态发酵参数、补料策略、动力学建模、下游分离纯化与膜分离。当设计或优化发酵工艺、分析发酵异常、放大到中试时加载。
---

# 发酵知识技能

## 何时使用
涉及菌种、发酵罐、培养基、代谢产物、酿造、生物制造、下游纯化、发酵尾水资源化的任务。

## 标准发酵方案模板

### 1. 菌种
- 菌株名称/编号、来源、保藏形式
- 活化 → 种子液 → 扩大培养（种龄、接种量 OD/体积比）
- 污染排查：镜检、平板、噬菌体

### 2. 培养基
| 组分 | 作用 | 浓度 | 灭菌 |
|---|---|---|---|
| 碳源（葡萄糖/糖蜜/淀粉） | 供能/骨架 | g/L | 115℃ 20min |
| 氮源（酵母粉/蛋白胨/铵盐） | 生长 | g/L | 同行 |
| 无机盐/微量元素 | 辅因子 | g/L/mg/L | 过滤除菌 |
| 前体/诱导物 | 定向合成 | — | 视性质 |

### 3. 关键参数
- pH、温度、溶氧（DO）、通气 vvm、搅拌 rpm、罐压、补料速率
- 补料分批：指数补料 `F = μ·X·V/(Yx/s·S)` 思路
- 泡沫控制（消泡剂）、染菌监测

### 4. 动力学建模
- 菌体生长：Monod `μ = μmax·S/(Ks+S)`
- 生长曲线：Logistic / **Gompertz**（见下方式子）
  - Logistic：`X = A / (1 + (A/X0 − 1)·exp(−μ·t))`
  - Gompertz：`X = A·exp(−exp((λ−t)·μ/A + 1))`
- 产物生成：与生长偶联/部分偶联/非偶联（Luedeking-Piret）
- 参数：A 最大生物量、μmax 比生长速率、λ 迟滞期、Yx/s 得率

### 5. 下游
1. 固液分离（离心/板框/膜）
2. 浓缩/纯化（超滤、纳滤、**渗透气化**、萃取、色谱）
3. 结晶/干燥/制剂
4. 尾水与副产物资源化（例：发酵尾水酒精回收至 30%+，排水酒精 <1%）

## 异常排查
| 现象 | 可能原因 | 对策 |
|---|---|---|
| 生长缓慢 | 种龄老/营养不足/抑制物 | 换种、补料、解毒 |
| 产量低 | C/N 失衡、DO 不足 | 调配方、提通气 |
| pH 异常漂移 | 代谢产酸/氨、缓冲不足 | 补碱/酸、加缓冲 |
| 泡沫过多 | 蛋白/多糖高 | 消泡剂、降转速 |
| 染菌 | 灭菌不彻底、操作污染 | 排查灭菌、无菌操作 |

## 放大准则
- 恒 kLa / 恒 P/V / 恒叶端线速度
- 关注剪切对菌丝体/细胞的损伤、混合时间

## 参考资源（`references/`，详见 `references/README.md` 索引）

知识文件（位于发酵专家目录 `references/`，绝对路径 `/home/caiq/MyAgents/发酵专家/references/`，可直接读取）：

- `发酵工程基础与工艺参数.md`：生长与代谢、关键参数、氧传递 OTR=kLa(C*−CL)、培养方式、补料策略、灭菌 F₀ 与染菌控制、反应器、放大准则（恒 kLa/P/V/叶端线速度）、PAT
- `菌种选育与保藏.md`：菌种来源、筛选/HTS、诱变/ALE/代谢工程/CRISPR/DBTL、保藏与种子扩培、噬菌体防治
- `培养基设计与优化.md`：组分与作用、C/N、工业原料、灭菌、PB/RSM/ANN-GA 优化、典型配方框架
- `发酵动力学与建模.md`：Monod/抑制模型、Logistic & Gompertz、Pirt、Luedeking–Piret、物料衡算、参数估计与示例
- `液态与固态发酵工艺.md`：液态/固态、两阶段与补料、酱油/食醋/白酒/黄酒/啤酒酿造、氨基酸/有机酸/酶/益生菌/生物乙醇/ABE/PHA 等生物制造
- `下游分离纯化与膜分离.md`：固液分离、破碎、萃取/色谱/结晶、MF/UF/NF/RO/ED、**渗透气化**、尾水酒精回收与资源化
- `标准规范与法规.md`：发酵食品/食品用菌种/发酵饲料/GMP/生物安全/知识产权/环保政策，附合规清单
- `异常排查与质量控制.md`：异常排查表、染菌/噬菌体处置、原辅料/过程/成品质控、偏差 CAPA、CIP/SIP
- `证据条目与出处.md`：**原著深度消化**——动力学/氧传递 kLa/培养基统计优化/液态与固态发酵/蒸馏与膜分离/发酵食品安全/接种量/PAT 的逐条证据（含书库页码）

模型脚本（独立技能）：
- **`microbial-growth`**：生长曲线计算与绘图（Gompertz/Logistic，使用前须与用户确认模型），脚本 `skills/microbial-growth/scripts/MicrobialGrowth.py`
- **`chemostat-dynamics`**：五级递进恒化发酵动力学模型（双入口：预测计算 / 案例演示），Scale 1–5 = Monod 基础 / Haldane 底物抑制 / 双菌竞争 / 产物抑制 / 代谢时滞；支持仿真、稳态、稀释率分岔与控制设计，脚本 `skills/chemostat-dynamics/scripts/chemostat.py`（方程与案例见该技能 `references/五级模型方程与案例.md`）

### 开放获取电子书库（`references/books/`，34 册 CC BY/公共领域全文）

书库位于 `/home/caiq/MyAgents/发酵专家/references/books/`，含 IntechOpen、MDPI 开放获取专著与酿造/发酵历史经典。
**全文检索（需要原著细节、公式、案例、页码时优先使用）**：

```bash
python3 /home/caiq/MyAgents/发酵专家/references/books/tools/search_books.py "Monod" --context 1
python3 /home/caiq/MyAgents/发酵专家/references/books/tools/search_books.py "kLa" --word --max 20
python3 /home/caiq/MyAgents/发酵专家/references/books/tools/search_books.py "solid-state fermentation" --books   # 定位哪本书讲得最多
# 命中页码后按页读原文
python3 /home/caiq/MyAgents/发酵专家/references/books/tools/read_page.py Modern_Technologies 214
```

- 目录索引：`references/books/INDEX.md`（主题标签→书目）；单书目录 `references/books/toc/<分区>/<书名>.md`；全文 `references/books/text/<分区>/<书名>.txt`；结构化元数据 `references/books/catalog.json`。
- 检索命中 `书|页码|原文` 后，读取对应 `toc/` 定位章节、`text/` 页码附近引用；引用须注明 作者/编者、书名、出版社、年份、许可与页码。
- 仅收录开放获取资源；商业版权教材（Shuler、Doran、Stanbury 等）只在 `references/books/README.md` 列出采购/借阅入口，禁止臆造其内容。

关联专家：种植专家（原料规格）、食品加工专家（功能配料应用）、食品安全专家（生物胺/毒素/菌种安全）、营养专家（功能配料评价）、检测专家（产物/代谢物方法）、文档专家（工艺报告/专利/申报）。

> 数值免责：知识文件中"典型/参考区间"为工程经验量级；标准号与限量须以现行官方版本复核（复核入口见 `references/README.md`）。
