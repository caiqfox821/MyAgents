---
name: microbial-growth
description: 微生物生长拟合预测技能（Gompertz/Logistic）。给定模型、最大生长速率、迟滞期、最大浓度、初始浓度、时间与温度，计算某时刻微生物浓度，并可绘制生长曲线。当需要微生物/发酵生长预测、生长曲线时加载。
---

# 微生物生长拟合预测技能

脚本：`scripts/MicrobialGrowth.py`（本技能目录内）。

## 触发场景
用户需要计算某一个时刻 time、某个温度条件 Temperature 下微生物生长的浓度 C。

## 模型选择（必须）
调用前必须先询问用户采用以下哪个模型，未指定时向用户询问后再继续：
- `gompertz`：修正 Gompertz 模型，`C = C0 * asymptote * exp(-exp((lag - time) * rate / asymptote + 1))`
- `logistic`：Logistic 模型，`C = asymptote / (1 + (asymptote / C0 - 1) * exp(rate * (lag - time)))`

## 输入参数
- model：模型选择，取值为 gompertz 或 logistic
- rate：最大生长速率
- lag：迟滞期
- asymptote：最大生长浓度
- C0：初始浓度
- time：计算时刻
- Temperature：环境温度

## 调用
计算某时刻浓度：
`python3 /home/caiq/MyAgents/发酵专家/skills/microbial-growth/scripts/MicrobialGrowth.py <model> <rate> <lag> <asymptote> <C0> <time> <Temperature>`

绘制生长曲线（追加 `--plot`，PNG 默认保存到当前目录）：
`python3 /home/caiq/MyAgents/发酵专家/skills/microbial-growth/scripts/MicrobialGrowth.py <model> <rate> <lag> <asymptote> <C0> <hours> [Temperature] [output] --plot`

## 约束
1. 未选择模型时，先询问用户采用 gompertz 还是 logistic
2. 传入非数字返回友好报错
3. 返回清晰格式化计算文本
