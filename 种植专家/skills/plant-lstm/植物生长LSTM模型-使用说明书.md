---
title: 通用植物生长 LSTM 模型 使用说明书
version: 1.0
date: 2026/09/23
skill: plant_lstm_model
script: ./scripts/plant_lstm.py
---

# 通用植物生长 LSTM 模型 · 使用说明书

## 1 简介
本技能将金线莲、兰科植物、番茄、草莓、蓝莓等植物生长预测统一为**同一套 LSTM 时序网络引擎**：
- 纯数据驱动黑箱模型，不嵌入生理机理公式；
- 支持**自定义网络结构**与**训练参数**；
- 支持离线训练、**在线增量学习**、**跨季迭代**、多步预测与绘图；
- 各植物参数集中在 `植物生长模型参数库.md`，金线莲等为具体运行实例；
- 所有输出（模型、快照、图片、数据）默认写入**当前工作目录**。

适用对象：种植管理者、科研人员、需要做周度等间隔监测预测与功效成分预判的使用者。

## 2 运行环境
- Python 3.7+（使用 argparse 子命令）
- **依赖 `numpy`**（矩阵运算引擎；缺失时脚本会立即报错并提示安装命令）
- 可选：`matplotlib`（仅绘图时按需导入）
- 无需联网、无需 GPU，CPU 单进程即可

> 2026-10 起主脚本改用 numpy 做矩阵运算（训练提速 4–8 倍，等价性已验证）。
> 原始纯 Python 版备份在 `scripts/backup/`，接口完全相同，可直接回退使用。

文件清单：
```
SKILL.md                     # 技能定义（供 AI/助手读取）
植物生长LSTM模型-使用说明书.md  # 本说明书
植物生长模型参数库.md         # 各植物参数（json 代码块）
scripts/plant_lstm.py        # 主程序（numpy 版）
scripts/backup/              # 原始纯 Python 版备份 + 说明
dev/                         # 等价性验证 / 性能对比脚本（开发用）
```

## 3 快速开始
```bash
# 1) 查看有哪些植物
python3 scripts/plant_lstm.py list

# 2) 查看某植物参数
python3 scripts/plant_lstm.py config --plant 番茄

# 3) 生成模拟数据（无实测数据时试用）
python3 scripts/plant_lstm.py gen_data --plant 番茄 --weeks 40 --out 番茄_data.json

# 4) 训练
python3 scripts/plant_lstm.py train --plant 番茄 --data 番茄_data.json --model 番茄_model.json

# 5) 预测未来 12 周并画图
python3 scripts/plant_lstm.py predict --model 番茄_model.json --data 番茄_data.json --weeks 12 --plot 番茄_prediction.png
```

## 4 参数库
### 4.1 结构
`植物生长模型参数库.md` 中每个植物一段 `json` 代码块：

| 字段 | 说明 |
|---|---|
| `plant` | 植物名称（唯一标识） |
| `features` | 环境/栽培输入；`min`/`max` 用于归一化到 0–1 |
| `outputs` | 预测目标；`group` 为 `growth`（长势/胁迫）或 `component`（功效成分） |
| `network` | `layers`（各层神经元）、`fc_dim`、`lr`、`adaptive`、结构上下界 |
| `training` | `epochs`、`window`、`shuffle`、`sample_weight`、`forget`、`global_keep` |

### 4.2 内置植物实例
| 植物 | 输入维度 | 输出维度 | 主要功效成分 |
|---|---|---|---|
| 金线莲 | 8 | 11 | 金线莲苷、多糖、黄酮、生物碱 |
| 兰科植物 | 8 | 10 | 多糖、黄酮 |
| 番茄 | 8 | 14 | 番茄红素、可溶性固形物、维C、总酚、可滴定酸 |
| 草莓 | 8 | 14 | 花青素、维C、可溶性固形物、总酚、可滴定酸 |
| 蓝莓 | 8 | 14 | 花青素、总酚、可溶性固形物、维C、可滴定酸 |
| 自定义 | 8 | 6 | 可自行增删 |

### 4.3 新增植物
复制参数库中「自定义」配置块，修改 `plant`/`features`/`outputs`/`network`/`training` 即可，无需改代码。也可用 `--config 自定义.json` 完全脱离参数库运行。

## 5 数据输入三种方式
1. **运行提示逐项输入**（对话式）：由助手询问并收集，每行一周记录，写入数据文件后调用脚本。
2. **一次性 md 文件输入**：md 中放 `json` 数组代码块，或 markdown 表格（表头 = 参数 key）。
3. **模拟数据**：`gen_data` 按参数区间随机生成，用于联调与演示。

数据 md 示例（json 代码块）：
````markdown
```json
[
  {"temperature": 24, "humidity": 65, "light": 25, "co2": 900, "ph": 6.0, "ec": 2.5, "irrigation": 2.5, "temp_diff": 6,
   "plant_height": 120, "stem_diameter": 9, "lycopene": 7.5, "brix": 6.5},
  {"temperature": 25, "humidity": 64, "light": 26, "co2": 950, "ph": 6.0, "ec": 2.6, "irrigation": 2.6, "temp_diff": 7,
   "plant_height": 128, "stem_diameter": 9.2, "lycopene": 7.8, "brix": 6.7}
]
```
````
说明：`features` 全部必填；`outputs` 在训练/增量时若缺项，按区间中点补齐；预测输入只需 `features`。

## 6 训练与自定义参数
```bash
python3 scripts/plant_lstm.py train --plant 番茄 --data 番茄_data.json --model 番茄_model.json \
  --layers 16,24 --fc-dim 32 --lr 0.03 --epochs 300 --window 6 --adaptive false \
  --shuffle true --sample-weight 1.0 --forget 0.95 --global-keep 0.98
```

| 参数 | 含义 | 默认 |
|---|---|---|
| `--layers` | 各 LSTM 层神经元数，如 `12,16` | 参数库 `network.layers` |
| `--fc-dim` | 全连接过渡层宽度 | 24 |
| `--lr` | 学习率 | 0.05 |
| `--epochs` | 训练轮次 | 参数库 `training.epochs` |
| `--window` | 时序窗口（依赖最近几周） | 4 |
| `--adaptive` | 是否自动增减层/神经元（true/false） | true |
| `--shuffle` | 每轮是否打乱样本 | true |
| `--sample-weight` | 学习率缩放 | 1.0 |
| `--forget` | 单季遗忘因子 | 0.95 |
| `--global-keep` | 跨季保留系数 | 0.98 |

训练输出：模型 JSON、每若干轮的 growth/comp 损失与当前结构、最终结构与总参数量。

## 7 增量学习与跨季迭代
参考金线莲生长黑箱模型：**每周在线微调、每季归档、跨季继承续训**。

完整工作流：
```bash
# 第1季：冷启动训练
python3 scripts/plant_lstm.py train --plant 金线莲 --data 第1季训练.md --model 金线莲_model.json

# 第1季：每周增量更新（可用 --out 指定快照）
python3 scripts/plant_lstm.py incremental --model 金线莲_model.json --data 本周.md --out 金线莲LSTM模型-第1季快照.json

# 季末：归档并开启第2季（继承结构与权重，清空本季缓冲）
python3 scripts/plant_lstm.py new_season --model 金线莲LSTM模型-第1季快照.json

# 第2季：每周继续增量（在继承模型上）
python3 scripts/plant_lstm.py incremental --model 金线莲LSTM模型-第2季快照.json --data 第2季本周.md

# 或一步完成“开新季 + 续训”
python3 scripts/plant_lstm.py incremental --model 金线莲LSTM模型-第1季快照.json --new-season --data 第2季本周.md
```

机制：
- **在线增量**：每周样本进入时序缓冲；满足 `window` 周且输出完整后执行一次反向传播；对最近若干周按 `forget^age` 加权重放，弱化本季早期旧数据。
- **跨季保留**：第 k 季 (k>1) 的更新按 `global_keep^(k-1)` 缩放，保护前序多季经验。
- **结构自适应**：损失连续无下降且残差偏高 → 加层/加神经元（层数 1–3，单层 12–48）；损失低且收敛 → 剪枝。可用 `--adaptive false` 关闭。
- **跨季继承**：`new_season` 仅清空缓冲，保留结构、全部权重与损失历史，`i=i+1`。
- **快照命名**：`<植物>LSTM模型-第<季>季快照.json`。

## 8 预测与绘图
```bash
# 预测未来若干周；--data 为最近监测数据，--future 为未来环境计划（可选）
python3 scripts/plant_lstm.py predict --model 番茄_model.json --data 最近监测.md --future 未来环境.md --weeks 12 --plot 番茄_prediction.png

# 仅绘图：给 --data 画预测图；不给 --data 画训练损失曲线
python3 scripts/plant_lstm.py plot --model 番茄_model.json --out 番茄_prediction.png
```
- 未提供 `--future` 时，未来各周环境默认**沿用最近一周**。
- 预测结果以 JSON 输出（各输出指标的反归一化值），并可同时出图。

## 9 输出文件
| 文件 | 说明 |
|---|---|
| `<植物>_model.json` | 训练模型（含季数、周数、结构、权重、缓冲、本季样本对） |
| `<植物>LSTM模型-第<季>季快照.json` | 增量/跨季快照 |
| `<植物>_prediction.png` | 预测曲线（按 group 分面板） |
| `<植物>_loss.png` | 训练损失收敛曲线 |
| `<植物>_data.json` | 生成的模拟数据 |

以上均写入**当前工作目录**。模型 JSON 自带 `features`/`outputs`，`predict`/`plot` 无需再指定参数库。

## 10 常见问题 FAQ
**Q1 没有实测数据能否运行？**
可以，用 `gen_data` 生成模拟数据验证流程。

**Q2 训练数据最少要多少周？**
至少 `window+1` 周；增量学习需先攒够 `window` 周缓冲且当周输出完整才开始更新。

**Q3 如何换用固定网络结构？**
`--adaptive false` 并指定 `--layers`，训练中结构不再自动增减。

**Q4 预测为什么各周数值变化平缓？**
未提供 `--future` 时环境沿用最近一周；提供未来环境计划可得到更丰富趋势。

**Q5 如何调整时序窗口？**
`--window 6`（同时影响训练与增量重放长度）。

**Q6 跨季后精度为何应更高？**
每季继承上一季结构/权重并按 `global_keep` 保护历史经验，数据越多、越贴合本场地规律。

**Q7 想新增一种植物？**
在 `植物生长模型参数库.md` 复制「自定义」块修改即可，脚本自动识别。

## 11 约束与注意事项
1. 仅适配**周度等间隔**监测；非均匀零散数据不适用。
2. 结构边界默认 LSTM 层数 1–3、单层神经元 12–48，可在参数库 `network` 调整。
3. 参数区间为典型农艺值，实际建模应以**本地实测数据校准**。
4. 在线增量每次仅微调权重，不做全局重训练。
5. 跨季归档建议保留历史快照以支持回溯对比。
6. 缺项特征按区间中点补齐，少量缺项不中断流程。
7. **多层网络的「末层扩容」**：当层数已达 `max_layers` 且损失仍偏高时，脚本会扩容末层神经元；此时末层（及中间层）权重矩阵的列数会大于实际输入宽度，脚本**只取前若干列参与计算**（原纯 Python 版行为完全相同，numpy 版已如实复刻）。若希望结构始终严格自洽，建议 `--adaptive false` 固定结构。
8. 主脚本依赖 numpy；无 numpy 环境可用 `scripts/backup/` 下的纯 Python 版（该文件位于子目录，需显式指定参数库 `--library`，或直接复制回 `scripts/plant_lstm.py`）。

## 12 命令速查表
| 命令 | 用途 |
|---|---|
| `list` | 列出参数库植物 |
| `config --plant X` | 查看 X 的完整参数 |
| `gen_data --plant X --weeks N --out F` | 生成模拟数据 |
| `train --plant X --data D --model M [自定义参数]` | 训练/续训 |
| `incremental --model M --data D [--new-season]` | 在线增量（可开新季） |
| `new_season --model M` | 季末归档并开新季 |
| `predict --model M --data D [--future F] --weeks N [--plot P]` | 多步预测 |
| `plot --model M [--data D] [--out P]` | 预测图 / 损失曲线 |

通用选项：`--library 参数库.md` 指定参数库路径。
