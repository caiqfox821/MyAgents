# spectral-matching（谱库匹配技能）· 结构说明

一个**自带引擎、可扩展**的本地质谱谱库比对技能。核心零第三方依赖（仅 numpy），
装 `matchms/ms_entropy/pyteomics/rdkit` 后自动增强。

## 目录

```
spectral-matching/
├─ SKILL.md                      技能说明（何时用/铁律/工作流/选型/边界）
├─ README.md                     本文件（结构 + 开发指引）
├─ templates/
│  └─ 匹配报告模板.md
└─ scripts/
   ├─ specmatch/                 引擎（纯 Python 包）
   │  ├─ __init__.py             公开 API
   │  ├─ spectrum.py             数据模型 Spectrum
   │  ├─ io.py                   MSP/MGF/JSON/CSV 读写（+mzML 走后端）
   │  ├─ filters.py              清洗与元数据规范化（matchms 风格）
   │  ├─ similarity.py           8 种打分器 + 注册表
   │  ├─ search.py               候选过滤 + 检索排序
   │  ├─ network.py              谱相似度网络
   │  ├─ report.py               Schymanski 分级 + 报告
   │  └─ backends.py             可选后端（matchms/ms_entropy/pyteomics/rdkit）
   ├─ build_index.py             raw/ → 标准 MSP 库 + index.json
   ├─ match.py                   查询 vs 库，CLI
   ├─ selftest.py                自检/回归（31 项）
   └─ setup_env.sh               建可选增强后端的环境
```

## 设计要点

1. **数据 / 算法 / 说明三层分离**：库数据只读（`references/谱库-*`），算法可测（`scripts/specmatch`），说明定契约（`SKILL.md`）。
2. **确定性输出**：`rank_table()` 表头固定，便于人工评分与回归。
3. **一切可插拔**：打分器（`similarity.register`）、读入格式、后端探测都留了扩展点。

## 新增一个打分器

```python
from specmatch.similarity import register

@register("my_dot")
def my_dot(query, reference, mz_tol=0.01, **kw):
    ...
    return score, n_matched
```

随后 `--method my_dot` 即可用。

## 自检 / 回归

```bash
python3 scripts/selftest.py                       # 合成数据
python3 scripts/selftest.py <峰表.csv>            # 追加真实数据自命中回归
```

## 可选增强后端

```bash
bash scripts/setup_env.sh                 # 默认 ~/opt/specmatch-venv
~/opt/specmatch-venv/bin/python scripts/match.py --caps
```

---
*维护者：质谱专家。修改公开 API 或文件结构时，请同步 SKILL.md 与 `references/README.md`。*
