---
name: nutritionist
description: 营养综合技能（可执行）。按 mode 选择：运动营养测算(met)、食材宏量营养测算(macro)、个人营养配餐推荐(meal)、体型与内脏脂肪评估(body)；内置 MET/食材营养/东亚 BMI/内脏脂肪/性别化 DRIs 数据，可生成 docx 报告。当需要运动量测算、宏量核算、配餐报告、BMI/腰围/体脂/内脏脂肪评估时加载。
---

# 营养综合技能（营养测算 / 配餐计算 / 配餐推荐 / 体型评估）

脚本：`scripts/nutritionist.py`（本技能目录内）。调用方式：
`python3 <技能目录>/scripts/nutritionist.py '<JSON参数>'`，必填参数 `mode`。

完整示例（复制可用）：

```bash
python3 /home/caiq/.config/opencode/skills/nutritionist/scripts/nutritionist.py \
  '{"mode":"body","sex":"女","age":38,"weight":62,"height":162,"waist":82,"body_fat":31,"visceral_fat_level":11,"tg":1.8,"hdl":1.2}'
```

## 模式选择（必须）
调用前必须先询问用户要执行哪个功能，未指定 mode 时先问再继续：
- `met`：营养测算器 —— 计算运动代谢当量（MET）与热量，对标 WHO 运动指南
- `macro`：营养配餐计算 —— 计算食材组合的宏量营养素，生成报告（docx + 雷达图）
- `meal`：个人营养配餐推荐 —— 按身体数据、性别与偏好定制一日三餐+加餐，生成配餐报告（docx）
- `body`：体型与内脏脂肪评估 —— 只做 BMI（多口径）/腰围/体脂率/内脏脂肪/CVAI 判定与性别化营养目标，返回 JSON，不出文件

## 输入要求

### 公共字段（所有模式）
| 字段 | 说明 |
|---|---|
| `sex` 或 `gender` | `男`/`女`/`male`/`female`。**建议必填**：缺失时无法给出性别化目标与分性别阈值 |
| `age` | 岁。≥50 岁女性按“无月经”铁需求（10 mg）处理 |
| `height` | cm。用于 BMI、腰围身高比、能量估算 |
| `weight` | kg |
| `waist` | cm（可选）。内脏脂肪评估的核心字段，强烈建议提供 |
| `hip` | cm（可选，暂仅存参） |
| `body_fat` | %（可选）。体脂秤或 DEXA 结果 |
| `visceral_fat_level` | 体脂秤内脏脂肪等级 1–30（可选） |
| `visceral_fat_area` | 体检 CT/MRI 内脏脂肪面积 cm²（可选） |
| `tg` / `hdl` | 甘油三酯 / 高密度脂蛋白胆固醇，mmol/L（可选，用于 CVAI） |
| `activity` | MET·min/周（meal 用）；缺省用 `steps` 推算 |

### met（营养测算器）
1. `exercises`：[{name, minutes, freq}] 或 `weekly_activities`（同结构）
2. `weight`（默认 60）

### macro（营养配餐计算）
必填：`weight`、`steps`、`target_protein`、`foods`（[{name, amount}]，至少一种）
建议：`sex`、`age`、`height`、`waist`、`body_fat`、`visceral_fat_level`、`tg`、`hdl`

### meal（个人营养配餐推荐）
必填：`weight`、`target_protein`
常用：`height`、`activity` 或 `steps`、`weight_loss_goal`、`allowed_meats`、`allowed_eggs`、
`allowed_dairy`、`allowed_soy`、`lunch_staple`、`dinner_staple`（白米饭/糙米/燕麦/红薯）、
`use_oats`、`use_sweet_potato`、`preferred_foods`
建议：`sex`、`age`、`waist`、`body_fat`、`visceral_fat_level`、`visceral_fat_area`、`tg`、`hdl`

### body（体型与内脏脂肪评估）
必填：`weight`、`height`
其余同上（`waist`/`body_fat`/`visceral_fat_level`/`visceral_fat_area`/`tg`/`hdl` 至少给一项，
否则内脏脂肪只能判“未评估”）

## 内置固定数据（无需外部文件）
1. 三大营养素热量换算系数；Mifflin-St Jeor + PAL 能量估算
2. 中美两套膳食指南宏量供能区间
3. 不同活动强度对应的蛋白质推荐克重区间
4. 60 种常用食材营养成分表 + 55 种食材微量营养素估算表（铁/锌/钙/膳食纤维）
5. 不同运动方式的 MET 当量值
6. **东亚 BMI 三套口径**：中国（18.5/24.0/28.0）、WHO 亚洲（23.0/27.5）、日本 JASSO（25.0）
7. **分性别 BMI 等危换算**：同体脂口径（男 23.0/27.9，女 24.4/32.5）、同代谢风险口径（男 22.5/25.9，女 22.8/26.6）
8. **腰围/体脂/内脏脂肪阈值**：中国腰围（男 90 / 女 85）、日本（男 85 / 女 90）、腰高比 0.5；
   体脂过多（男 >25% / 女 >30%）、亚洲正常体重肥胖（男 20.6% / 女 33.4%）；
   VFA（<100 / 100–150 / ≥150 cm²）、VFL（1–9 / 10–14 / ≥15 级）、CVAI（男 101.80 / 女 88.42）
9. **DRIs 2023 性别化目标**：蛋白质 男 65 / 女 55 g；铁 男 12 / 女 18 mg（无月经 10）；
   锌 男 12 / 女 8.5 mg；钙 800 mg；维生素 A 男 770 / 女 660 μgRAE；膳食纤维 25–30 g；酒精 男 25 / 女 15 g

### 关于“女性 BMI 可以更高”
必须在报告中同时呈现三套口径，不能只给一个放宽后的 BMI：
- **官方中国标准不分性别**（24/28）；
- **同体脂率**换算，女性肥胖对应 BMI 32.5、男性 27.9 —— 女性在同一体脂水平下确实可以对应更高 BMI；
- **同代谢风险**换算，两者几乎相同（女 26.6 / 男 25.9）—— 所以“BMI 高一点”不等于“风险低一点”。
因此女性评估必须以腰围、体脂率、内脏脂肪为准；BMI 正常但体脂超标的“正常体重肥胖”在女性中更常见。

## 输出强制格式

### met
- 当日运动当量（MET·min/周）、当日消耗热量、对标 WHO 运动指南的判定

### body
- JSON：`bmi_assessment`（三套口径 + 分性别等危）、`waist`、`body_fat`、`visceral`（含 CVAI）、
  `energy`、`gender_targets`、`advice`（内脏脂肪偏高时给出对策）

### macro
- 按顺序输出：个人基本信息、体型与内脏脂肪评估、食材明细、宏量营养素分析（汇总表/比值/雷达图）、
  双指南评估、性别化营养目标与微量营养素达成、结构调整建议、附录计算依据
- 生成 docx：中文字体宋体、西文 Times、紧凑排版，文件名 `姓名-个人膳食宏量营养素报告.docx`，存于当前目录

### meal
- 按顺序输出：个人信息、体型与内脏脂肪评估、需求汇总（配餐约束/性别化目标）、配餐建议（分餐食谱）、
  营养素计算（宏量汇总/分餐分布/双指南/运动量/减重计划/微量营养素达成）、调整建议、附录
- 所有数字保留 1 位小数，数字与单位之间空一格
- 生成 docx：文件名 `姓名-个人精准配餐报告.docx`，存于当前目录

## 约束
1. 未选择模式时，先询问用户采用 met / macro / meal / body 哪个功能
2. 传入非法 mode、缺失必填参数或数值越界，返回友好报错（`{"error": "..."}`）
3. 不支持复杂小众食材（无内置营养数据）精准测算；微量营养素为估算值，非实验室检测
4. 不支持慢性病（肾病/糖尿病/痛风）治疗膳食、婴幼儿/孕妇/老年人定制、药膳保健品代餐
5. `body_fat`/`visceral_fat_level`/`VFA` 来自不同仪器，绝对值不可直接互比；报告只做分级，不做诊断

## 数据来源
- 成人体重判定 WS/T 428—2013；《肥胖症诊疗指南（2024 年版）》；《体重管理指导原则（2024）》
- WHO 亚洲人群 BMI 行动点（2004）；日本肥胖学会（JASSO）肥胖症诊断标准
- Obesity (2015) 中国人群 BMI 等危换算；CHARLS 队列 CVAI 切点；Xia et al. 2016 CVAI 公式
- 中国居民膳食营养素参考摄入量（2023 版）；中国居民膳食指南（2022）
- 亚洲正常体重肥胖体脂阈值系统评价；Omron/InBody 内脏脂肪等级判读
