---
name: nutrition
description: 营养评估与配餐技能。用于能量与营养素测算、DRIs/NRV 评价、膳食结构与配餐推荐、营养标签（NRV%）及人群/运动营养。当膳食营养测算、配餐推荐、食谱设计、营养标签、营养声称时加载。
---

# 营养技能

## 何时使用
膳食营养测算、配餐推荐、食谱设计、营养标签（NRV%）、营养达标评价、人群与运动营养咨询。

## 能量与营养素换算
- 能量系数：碳水 4、蛋白 4、脂肪 9、酒精 7 kcal/g
- 身体指标：`BMI = 体重(kg) / 身高(m)²`
- 能量消耗：BMR（Mifflin-St Jeor 等）→ TDEE = BMR × 活动系数
- 运动量：`MET·min/周 = Σ(MET × 分钟 × 频次)`

## 供能与推荐区间
- 宏量供能比：蛋白 10–15%、脂肪 20–30%、碳水 50–65%
- 蛋白质：一般成人 1.0–1.2 g/kg/d；运动/增肌 1.4–2.0 g/kg/d
- 膳食纤维：25–30 g/d；添加糖 <50 g/d（最好 <25 g/d）
- 钠 <2000 mg/d（食盐 <5 g/d）
- 推荐摄入：中国 DRIs 的 EAR/RNI/AI/UL

## 配餐流程
1. 采集：性别、年龄、身高体重、活动水平、目标、限制与偏好
2. 计算：能量需求与三大营养素目标
3. 分配：三餐+加餐供能比（早 25–30%、午 35–40%、晚 30–35%、加餐 5–10%）
4. 编排：食物交换份或食材克重，覆盖谷薯/蔬果/蛋白/奶豆/油脂
5. 核算：能量、蛋白质、脂肪、碳水、NRV% 合计
6. 输出：食谱表 + 替换方案 + 烹调建议

## 营养标签（GB 28050）
- 核心营养素：能量、蛋白质、脂肪、饱和脂肪、碳水、糖、钠
- `NRV% = 含量 / NRV × 100%`
- 营养声称（低/无/高）需满足对应阈值

## 输出规范
- 默认中文；数值带单位（kcal、g、mg、μg、%）
- 一日三餐+加餐、能量与三大营养素占比、NRV%、食材克重
- 数据来源：中国食物成分表、中国 DRIs；标注版本
- 关键计算二次复核

## 营养综合技能（独立技能 `nutritionist`，met / macro / meal）
需实际测算或生成报告时调用独立技能 **`nutritionist`**（脚本 `../nutritionist/scripts/nutritionist.py`），必填 `mode`；未指定 mode 须先询问用户。
调用：`python3 /home/caiq/MyAgents/营养专家/skills/nutritionist/scripts/nutritionist.py '<JSON参数>'`

- `met` 运动营养测算：`weight`(kg，默认 60)、`exercises`[{name, minutes, freq}] 或 `weekly_activities`；返回每周 MET·min、消耗热量与 WHO 指南判定。
- `macro` 配餐计算：`weight`、`steps`、`target_protein`、`foods`[{name, amount}]；返回宏量营养素汇总、双指南评估与替换建议，生成 docx 报告（含玫瑰图）。
- `meal` 配餐推荐：`weight`、`height`、`target_protein`、`allowed_meats/eggs/dairy/soy`、`lunch_staple/dinner_staple`、`use_oats/use_sweet_potato`、`preferred_foods`；生成一日三餐+加餐食谱与 docx 配餐报告。

内置固定营养/MET 数据；不支持小众食材精准测算与慢病（肾病/糖尿病/痛风）治疗膳食。详规见技能 `nutritionist`。

## 参考资源（`references/`，详见 `references/README.md` 索引）
知识文件（位于 `/home/caiq/MyAgents/营养专家/references/`，可直接读取）：
- `DRIs与营养评价.md`：DRIs 四指标、能量需要（BMR/TDEE）、AMDR、营养状况评价四法与膳食调查
- `膳食结构与食物成分.md`：膳食宝塔、食物交换份、中国食物成分表使用、生熟换算
- `配餐与食谱设计.md`：配餐八步、餐次分配、特殊人群与慢病、减重/增肌、计算示例
- `营养标签与声称.md`：GB 28050 与 NRV%、含量/比较/功能声称条件框架、GB 13432
- `人群与运动营养.md`：各生命阶段营养、运动营养与补剂、体重管理
- `标准规范与法规-营养.md`：DRIs/膳食指南/GB 28050 等标准索引与合规清单
可执行技能：见独立技能 `nutritionist`（`../nutritionist/`，met / macro / meal 三种 mode，见上节）。
> DRIs、NRV、声称阈值与标准版本号以现行官方版本为准（复核入口见 `references/README.md`）。

## 关联
- 食品加工专家：配方营养化设计与标签测算
- 食品安全专家：安全与营养分工
- 文档专家：营养报告与科普材料
