---
name: spectral-matching
description: 本地质谱参考谱库的自动化比对与鉴定技能。用于把实测谱/峰表与本地 MSP/MGF/MassBank/GNPS 参考谱比对，输出 Top-N 命中、多种相似度分数与 Schymanski 置信度级；覆盖 EI 匹配因子与 ESI MS² 熵相似度、修饰余弦（找类似物）、候选过滤（前体 ppm/加合物/极性/CE）、谱相似度网络与批量注释。自带纯 Python 引擎（仅需 numpy），装 matchms/ms_entropy 后自动增强。当需要谱库检索、谱图自动比对、未知物初筛、同分异构区分、批量鉴定或自建谱库时加载。
---

# 质谱谱库匹配技能（spectral-matching）

## 何时使用

- 已把参考谱下载到本地（MassBank / MoNA / GNPS / NIST 导出 / 自测），需要**自动比对**得出结论。
- 需要给实测谱做**未知物初筛**、**批量注释**、**同分异构区分**。
- 需要**自建库**（本仪器、同碰撞能）并做可复现检索。
- 需要把比对结果按**置信度分级**写进报告。

## 一、四条铁律（先看这个）

1. **先候选过滤，再打分**：前体 m/z（ppm）＋ 极性 ＋ 加合物 ＋ 碰撞能必须一致。
   跨条件相似度没有意义——本库实测：同一化合物（Rg1）换加合物后 cosine 在 **0.001–0.52** 间剧烈波动
   （[M+HCOO]⁻ vs [M+CH3COOH-H]⁻＝0.52；vs [M+Na]⁺＝0.001），而熵相似度仍有 0.73–0.90；
   故**禁止**跨极性/加合物直接比分数。
2. **打分器按电离方式选**：EI 用 `match_factor`（NIST 风格），ESI MS² 用 `entropy`。
3. **MS² 库匹配最高到 Level 2**：Level 1 必须标准品 + 保留时间一致。
4. **"查不到" ≠ "不存在"**：库覆盖有限；查不到时应扩库或转**原位解析**（SIRIUS/CSI:FingerID、MetFrag）。

## 二、快速上手

```bash
cd 质谱专家/skills/spectral-matching/scripts

# 0) 看当前可用的增强后端
python3 match.py --caps

# 1) 把 raw/ 下的谱图统一成标准 MSP 库 + index.json
python3 build_index.py --raw ../../../references/谱库-人参/raw --out ../../../references/谱库-人参/index

# 2) 检索（ESI MS²：熵相似度）
python3 match.py --library ../../../references/谱库-人参/index/library.msp \
    --query sample.mgf --method entropy --mz-tol 0.02 --precursor-ppm 20 --top 5

# 3) 检索（GC-EI：匹配因子）
python3 match.py --library ei_lib.msp --query gc_unknown.msp \
    --method match_factor --mz-tol 0.5 --top 5

# 4) 自检 / 回归
python3 selftest.py

# 5) 用 matchms 官方实现打分（已装则自动启用；也可显式指定）
~/opt/specmatch-venv/bin/python match.py --library library.msp --query sample.mgf \
    --method cosine_greedy,modified_cosine --backend matchms --mz-tol 0.02 --top 5
```

检索结果同时给出 `cosine_greedy,entropy,match_factor...`（可多选，逗号分隔），
并自动附 **Schymanski 置信度级**与理由。`--backend native|auto|matchms` 控制用自带引擎还是 matchms 官方实现。

## 三、工作流（5 步）

```
① 建库/读库        load_spectra / build_index.py   → Spectrum 列表或 library.msp
② 清洗            filters.default_filters()        → 规范化元数据、去噪、归一化
③ 候选过滤        SpectralLibrary.candidates()     → 前体 ppm + 极性 + 加合物 + CE
④ 打分排序        SpectralLibrary.query()          → entropy / cosine / match_factor ...
⑤ 定级出报告      report.schymanski_level/to_markdown
```

## 四、打分器选型

| 场景 | 打分器 | 容差起点 | 说明 |
|---|---|---|---|
| **ESI MS²** | `entropy` | 0.01–0.02 Da | 抗强度/仪器差异，首选 |
| ESI 通用 | `cosine_greedy` | 0.01 Da | 与 matchms 口径一致 |
| 最优匹配 | `cosine_hungarian` | 0.01 Da | 需 scipy，否则回退贪心 |
| 找类似物/同系物 | `modified_cosine` | 0.01 Da | 允许中性丢失对齐 |
| 只看中性丢失 | `neutral_losses` | 0.01 Da | 诊断性 |
| 低质量噪声多 | `weighted_cosine` | 0.01 Da | m/z 加权 |
| **EI / GC-MS** | `match_factor` | 0.3–0.5 Da | 近似 NIST 匹配因子（×999） |
| 快速粗筛 | `intersect_mz` | 0.01 Da | 匹配峰占比 |

## 五、候选过滤（必须）

```python
lib.query(q, precursor_ppm=20, adduct="[M-H]-", polarity=True, collision_energy=35, ce_tol=0.25)
```
- `precursor_ppm`：前体精确质量窗口；`None` 表示不过滤（**仅用于自比对/调试**）。
- `adduct`/`polarity`/`collision_energy`：条件一致性；缺一项都可能把正确答案排到后面。
- 召回时要**放宽**（ppm 20–50、CE 容忍），定级时要**收紧**。

## 六、置信度分级（Schymanski 2014）

| 级 | 含义 | 触发（启发式） |
|---|---|---|
| 1 | 已确证结构 | 标准品 + RT 一致 |
| 2 | 推定结构 | entropy ≥ 0.80 且匹配峰 ≥ 4（**MS² 库匹配上限**） |
| 3 | 候选结构 | 0.50 ≤ 分数 < 0.80 |
| 4 | 唯一分子式 | 仅有分子式证据 |
| 5 | 仅精确质量 | 无结构证据 |

**同分异构/立体异构必须用 RT 或离子淌度 CCS 区分**（本库实测 Rg3(S) vs Rg3(R) MS² 熵相似度 0.925，无法区分）。

## 七、输出契约（确定性，便于人工评分）

`report.rank_table()` 输出固定表头：

```
rank | library_id | compound | inchikey | adduct | ionmode | collision_energy |
precursor_mz | score_<method> | nmatched_<method> | level | rationale
```

## 八、扩展（"保留更多可能性"）

- **加打分器**：`similarity.register("my_score", fn)`，签名 `fn(q, r, **kw) -> (score, n_matched)`。
- **加读入格式**：在 `io.load_spectra` 分发处注册扩展名。
- **加后端**：`backends.py` 里 `_try("库名")` 探测；已预留 `matchms / ms_entropy / pyteomics / rdkit`。
- **网络分析**：`network.build_network(spectra, threshold=0.7)` 得边表与聚类（分子网络雏形）。

## 九、可选增强后端

核心引擎**零第三方依赖**（仅 numpy，已在 Python 3.7 验证）。装了以下库自动增强：

| 后端 | 解锁 | 安装 |
|---|---|---|
| `matchms` | 完整 IO/过滤/打分生态、与官方实现互校 | `scripts/setup_env.sh` |
| `ms_entropy` | 高速熵相似度（大库） | 同上 |
| `pyteomics` | 直接读 **mzML/mzXML** | 同上 |
| `rdkit` | SMILES → InChIKey/指纹 | 同上 |

`setup_env.sh` 会用 python3.9+ 建独立 venv（本机为 3.12）并安装；随后可用该解释器跑本技能。

> **本机已建**：`~/opt/specmatch-venv`（Python 3.12）
> —— matchms **0.33.1**、ms_entropy **1.5.3**、pyteomics **5.0.1**、rdkit **2026.9.1**，已验证。
> 用 `~/opt/specmatch-venv/bin/python match.py --caps` 查看；打分加 `--backend matchms`。
> ⚠️ matchms 0.33 的修饰余弦名为 `ModifiedCosineGreedy`（旧名 `ModifiedCosine` 已移除），桥接层已适配。

## 十、边界与常见坑

- 熵/余弦**不是绝对阈值**；先用已知样建立本仪器的分布再定阈值。
- `match_factor` 为**近似实现**，绝对分值以 NIST MS Search/AMDIS 为准。
- 库数据质量参差（如 MassBank 个别记录 `ch_exact_mass` 存了平均分子量）——引用前核对。
- 大量干扰/共流出时考虑 **reverse/inverse search**（样品峰是否都被库解释）。
- 计算量大时用 `ms_entropy` 的 FlashEntropySearch，或先 `intersect_mz` 粗筛。

## 十一、与知识库的接口

- 方法学与阈值来源：`references/谱图解析与未知物鉴定.md`、`references/证据条目与出处.md`（C-1 五级、H-6 PFAS 判据；GNPS 参数见书目 PMC13467950）。
- 共享库：`references/书库索引.md`（为何共用 `公共知识/书库/`）。
- 参考谱数据：`references/谱库-人参/`、`references/参考谱图-人参皂苷Rg1_Rg3/`。
- 外部 RDF 谱库：公共技能 `togomcp-sparql`（MassBank）。

---
*本技能由质谱专家维护。新增打分器/格式请同步更新本文件与 `references/README.md`。*
