# scripts/backup/ —— 原始纯 Python 版备份

这里保存 2026-10-18 改造前的 `plant_lstm.py`（纯 Python 矩阵运算版本），作为回退与对照用。

| 文件 | 说明 |
|---|---|
| `plant_lstm_pure_20261018-194825.py` | 改造前的原版，与当时的 `../plant_lstm.py` 逐字节相同 |

## 与当前版本的关系

当前 `../plant_lstm.py` 只是把矩阵运算换成了 numpy，**接口、命令行参数、模型 JSON 格式、
随机数调用顺序（初始化/扩容/剪枝）全部保持不变**。已用 `dev/verify_equiv.py` 验证：
同随机种子下，两版的损失、全部权重与预测输出的最大偏差 ≤ 2.2e-16（仅浮点求和顺序差异）。
训练速度提高约 4–8 倍（大配置约 7.8x）。

## 怎么用这个备份

**方式一：临时对照运行**

该文件在 `backup/` 子目录，脚本按 `脚本目录的上一级` 找参数库，所以必须显式指定 `--library`：

```bash
python3 scripts/backup/plant_lstm_pure_20261018-194825.py \
  --library /home/caiq/MyAgents/种植专家/skills/plant-lstm/植物生长模型参数库.md \
  train --plant 番茄 --data 番茄_data.json --model 番茄_model.json
```

**方式二：彻底回退（不依赖 numpy）**

```bash
cp scripts/backup/plant_lstm_pure_20261018-194825.py scripts/plant_lstm.py
```

复制回原位后默认参数库路径即恢复正确，之后按原文档使用即可。

## 注意

- 新版 `scripts/plant_lstm.py` 需要 numpy（缺失时会报错并提示 `pip3 install numpy`）。
- 两版生成的模型 JSON 可以互相加载，数值一致。
- 若还要再做一次改造，建议先按同样方式备份当前版本。
