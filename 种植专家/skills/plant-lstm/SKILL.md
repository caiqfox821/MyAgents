---
name: plant-lstm
description: 通用植物生长 LSTM 时序预测技能（可执行）。支持金线莲/兰科/番茄/草莓/蓝莓/自定义植物的训练、在线增量学习、跨季迭代、多步预测与绘图；网络结构与训练参数可自定义，参数存于植物生长模型参数库。当需要植物生长或功效成分时序预测、生长曲线建模时加载。
---

# 通用植物生长 LSTM 模型

脚本：`scripts/plant_lstm.py`；参数库：`植物生长模型参数库.md`；详细操作见 `植物生长LSTM模型-使用说明书.md`（均在本技能目录内）。

将金线莲、兰科植物、番茄、草莓、蓝莓等统一为**同一套 LSTM 时序网络引擎**（纯数据驱动黑箱模型，不嵌入生理机理公式），具备**离线训练、在线增量学习、跨季迭代**能力。

## 1 使用前必须确认（选项选择）
调用前先向用户确认以下三项（缺省则用选项询问）：
1. **植物类型**：`金线莲` / `兰科植物` / `番茄` / `草莓` / `蓝莓` / `自定义`（可先运行 `list` 列出参数库）
2. **动作**：`训练(train)` / `增量更新(incremental)` / `新季迭代(new_season)` / `预测(predict)` / `绘图(plot)` / `生成数据(gen_data)`
3. **输入方式**：对话式逐项输入 / 一次性 md 文件输入 / 参数库模拟数据（`gen_data`）

## 2 可自定义内容
- 网络结构：`--layers 12,16`、`--fc-dim 32`、`--adaptive true|false`
- 训练参数：`--epochs 150`、`--window 4`、`--lr 0.03`、`--shuffle true`、`--sample-weight 1.0`、`--forget 0.95`、`--global-keep 0.98`
- 植物/特征/输出：编辑 `植物生长模型参数库.md` 对应 `json` 配置块，或用 `--config 自定义.json`

## 3 常用命令
```bash
python3 scripts/plant_lstm.py list
python3 scripts/plant_lstm.py config --plant 番茄
python3 scripts/plant_lstm.py gen_data --plant 番茄 --weeks 40 --out 番茄_data.json
python3 scripts/plant_lstm.py train --plant 番茄 --data 番茄_data.json --model 番茄_model.json
python3 scripts/plant_lstm.py train --plant 番茄 --data 番茄_data.json --model 番茄_model.json \
  --layers 16,24 --fc-dim 32 --lr 0.03 --epochs 300 --window 6 --adaptive false
python3 scripts/plant_lstm.py predict --model 番茄_model.json --data 最近监测.md --weeks 12 --plot 番茄_prediction.png
python3 scripts/plant_lstm.py plot --model 番茄_model.json --data 最近监测.md --out 番茄_prediction.png
```
（实际调用请用绝对路径 `/home/caiq/MyAgents/种植专家/skills/plant-lstm/scripts/plant_lstm.py`，并在技能目录下运行或显式 `--library` 指定参数库。）

## 4 增量学习与跨季迭代
```bash
python3 scripts/plant_lstm.py incremental --model 金线莲_model.json --data 本周数据.md --out 金线莲LSTM模型-第1季快照.json
python3 scripts/plant_lstm.py new_season --model 金线莲LSTM模型-第1季快照.json
python3 scripts/plant_lstm.py incremental --model 金线莲LSTM模型-第2季快照.json --data 第2季本周.md
python3 scripts/plant_lstm.py incremental --model 金线莲LSTM模型-第1季快照.json --new-season --data 第2季本周.md
```
机制：每周样本在线微调权重（按 `forget` 遗忘因子加权）；跨季按 `global_keep^(k-1)` 保护历史经验；损失无下降且残差高时自动增减结构（层数 1–3，单层 12–48），可用 `--adaptive false` 关闭；`new_season` 仅清空本季缓冲，保留结构、权重与损失历史。

## 5 md 一次性输入格式
数据 md 支持两种写法，脚本自动识别：
1）`json` 代码块（周记录数组，key = 参数库中的 features/outputs key）；
2）markdown 表格（首行表头使用参数 key）。

## 6 参数库
- 文件：`植物生长模型参数库.md`（本技能目录内）
- 内置实例：金线莲、兰科植物、番茄、草莓、蓝莓、自定义模板
- 新增植物：复制「自定义」配置块，修改 `plant`/`features`/`outputs`/`network`/`training` 即可

## 7 输出
- 模型 JSON、快照、预测图 PNG、预测 JSON、生成数据 JSON 等**一律输出到当前工作目录**。
- 默认文件名：`<植物>_model.json`、`<植物>LSTM模型-第<季>季快照.json`、`<植物>_prediction.png`、`<植物>_data.json`。

## 8 约束
1. 使用前先确认植物类型、动作与输入方式（未确定先询问）
2. 训练数据至少需 `window+1` 周；增量学习需 `window` 周缓冲 + 完整输出才开始更新
3. 预测默认沿用最近一周环境；提供 `--future` 可按未来环境计划预测
4. 结构边界：LSTM 层数 1–3、单层神经元 12–48
5. 参数区间为典型农艺值，实际建模应以本地实测数据校准
6. 不嵌入生理机理公式，纯数据驱动黑箱模型
7. 运行依赖 **numpy**（缺失会直接报错并提示安装）；原始纯 Python 版备份在 `scripts/backup/`，接口相同，回退时该文件在子目录需加 `--library` 指定参数库
8. 多层网络达到层数上限后的「末层扩容」会让权重列数大于实际输入宽度，脚本只取前若干列参与计算（与原版行为一致）；需要严格自洽结构时用 `--adaptive false`
