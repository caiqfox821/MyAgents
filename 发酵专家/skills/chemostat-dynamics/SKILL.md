---
name: chemostat-dynamics
description: 五级递进恒化发酵动力学模型（双入口）。入口一用于恒化/连续发酵的仿真预测、稳态求解、稀释率分岔与控制设计；入口二用于展示真实菌种案例（酿酒酵母/醋酸杆菌/大肠杆菌-假单胞菌/干酪乳杆菌/里氏木霉）、控制方案与使用示范。含 Scale 1–5：Monod 基础、Haldane 底物抑制、双菌竞争、产物抑制、代谢时滞。当出现恒化、连续发酵、chemostat、稀释率 D、洗出、临界稀释率、稳态/分岔/双稳态、竞争排斥、产物抑制、代谢时滞与振荡、发酵动力学仿真预测、控制策略设计、案例演示等需求时加载。
---

# 五级递进恒化发酵动力学模型（双入口技能）

引擎：`scripts/chemostat.py`（本技能目录内）。
事实来源：`references/五级模型方程与案例.md`（方程、参数、案例、稳态判据）。

## 规则约束（必须遵守）

1. **只使用**本技能/原始文档给出的方程、参数与案例，**不新增任何动力学机制**（不引入维持系数、Luedeking–Piret、氧传递等额外项）。
2. **模型必须手动选择** `--scale 1..5`；用户未指定时先询问，不擅自替用户选型。
3. 严格按照下方触发词模板**路由分发**：命中"计算/预测"进【入口一】，命中"案例/演示"进【入口二】。
4. 文档未给出的数值（如 Scale 3/5 部分参数、各 Scale 的 $S_0$/$D$）默认使用**明确标注的演示默认值**，可用 `--set key=value` 覆盖。

## 模型选择面板

| Scale | 模型 | 真实示范菌种 |
|---|---|---|
| 1 | Monod 基础恒化模型（无抑制，单菌） | 酿酒酵母 *Saccharomyces cerevisiae* |
| 2 | Haldane 底物抑制恒化模型（底物高浓度抑制） | 醋酸杆菌 *Acetobacter aceti* |
| 3 | 双菌种竞争恒化模型（两菌竞争同一底物） | 大肠杆菌 vs 假单胞菌 |
| 4 | 产物抑制单菌恒化模型（代谢产物抑制菌体） | 干酪乳杆菌 *Lactobacillus casei* |
| 5 | 带代谢时滞单菌恒化模型（代谢响应迟滞） | 里氏木霉 *Trichoderma reesei* |

---

## 二、触发词模板（OpenCode / Agent 调度）

> 当输入命中任意一条关键词组合，即可唤醒本 Skill，并按分支路由。

### 分支 A：唤醒 —— 入口一（模型预测计算）

最小触发短语（可直接写入路由规则）：

- 恒化 / 连续发酵 / chemostat / 连续培养 / 恒化培养
- 稀释率 D / 临界稀释率 / 洗出 / washout
- 发酵动力学仿真 / 稳态求解 / 稳态解 / 稳态多解
- 分岔 / 双稳态 / 多稳态 / 底物抑制 / 产物抑制
- 竞争排斥 / 共培养竞争 / 菌群筛选
- 代谢时滞 / 时滞振荡 / 滞后补偿
- 给定参数算浓度 → 预测某某时刻的 X 或 S

路由动作：进入【入口一】，**先确认 Scale（1..5）**，再按需调用 `simulate` / `steady` / `bifurcation` / `control`。

### 分支 B：唤醒 —— 入口二（案例 Demo 演示）

最小触发短语：

- 案例 / Demo / 演示 / 示范 / 展示 / 举例
- 真实菌种 / 文献案例（酿酒酵母、醋酸杆菌、大肠杆菌、假单胞菌、干酪乳杆菌、里氏木霉）
- 控制方案 / 控制策略 / 过程控制示范
- "给我看看……" / "跑一个例子" / "演示一下 Scale N"

路由动作：进入【入口二】调用 `demo`；用户给定 Scale 就演示单个，说"全部/都看看"则 `--all`。

### 分支冲突

同时命中 A、B 且用户明确说"演示/案例/Demo"→ 取【入口二】；否则默认【入口一】。

---

## 入口一：模型预测计算

> 必须带 `--scale`；参数用 `--set key=value` 覆盖（可重复）。

```bash
S=/home/caiq/MyAgents/发酵专家/skills/chemostat-dynamics/scripts/chemostat.py

python3 $S list                                  # 列出模型面板与案例
python3 $S params --scale 1                      # 查看某 Scale 的参数与"演示默认值"
python3 $S simulate --scale 1 --tend 60 --out x1.png
python3 $S steady   --scale 2                    # 稳态解 + 稳定性 + D_crit
python3 $S bifurcation --scale 2 --out bif.png   # 稀释率分岔（o 稳定 / x 不稳定）
python3 $S control  --scale 2                    # 控制要点（Scale2 另附文档控制案例）
python3 $S simulate --scale 5 --set tau=5 --out delay.png
```

- `simulate`：时程积分。Scale 1–4 用自适应求解器；**Scale 5 用定步长 RK4 + 时滞缓冲**，`--dt` 可调步长。
- `steady`：给出洗出态与非平凡稳态，判定稳定性（Scale 5 有时滞故标注"未判"）。
- `bifurcation`：以 D 为扫描变量，自动区分稳定/不稳定分支（Scale 2 展示双稳态最直观）。
- `control`：按模型给出控制要点；Scale 2 附文档"过程控制实际案例"。

## 入口二：案例 Demo 演示

```bash
python3 $S demo --scale 1 --outdir chemostat_demo
python3 $S demo --all --bifurcation --outdir chemostat_demo
```

- 每个 Scale 打印：菌种/底物/条件、参数（含演示默认值）、**文档控制结果**、仿真终点，并输出曲线 PNG。
- Scale 2 自动附**分级进料对照**（高 $S_0=30$ → 洗出；分级 $S_0=5$ → 稳定生产），对应文档控制案例。
- Scale 5 自动附**时滞对照**（$\tau=0.2$ h 稳定 vs $\tau=5$ h 振荡），展示时滞诱发振荡。

## 输出规范

- 默认中文；参数标明单位（g/L、h⁻¹）。
- 图表坐标用英文（避免缺字），关键结论用中文文字说明。
- 引用参数/案例时注明来自文档哪个 Scale；演示默认值须显式标注。

## 关联

- 生长曲线拟合（Gompertz/Logistic）用独立技能 `microbial-growth`。
- 动力学背景知识见 `../fermentation-knowledge/references/发酵动力学与建模.md`。
- 连续发酵下游与产物原位分离见 `../fermentation-knowledge/references/下游分离纯化与膜分离.md`。
