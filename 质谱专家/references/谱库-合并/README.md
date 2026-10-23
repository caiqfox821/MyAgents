# 统一检索入口 · 合并质谱参考谱库（人参 + 金线莲）

> 自动生成，请勿手改；由 `scripts/merge_libraries.py` 合并同级 `谱库-*` 得到。

## 一、概况

| 指标 | 数值 |
|---|---|
| 谱图总数 | **2954** |
| 化合物（去重） | **59** |
| MS² 谱（ms_type=MS2） | 2767 |
| 非 MS² 谱（MS1 等） | 187 |
| n_peaks 范围（中位） | 1 – 6000（17） |
| InChIKey 覆盖 | 2954 / 2954（缺 0） |
| 来源 MassBank | 2095 |
| 来源 MoNA | 515 |
| 来源 GNPS | 344 |

**归属（跨库重复已去重）**

| 归属 | 谱图数 |
|---|---|
| 人参 + 金线莲 | 1211 |
| 金线莲 | 1176 |
| 人参 | 567 |

**各库目标覆盖**

| 库 | 目标 | 收录 | 缺失 |
|---|---|---|---|
| 人参 | 99 | 46 | 53 |
| 金线莲 | 37 | 34 | 3 |

## 二、文件

| 文件 | 说明 |
|---|---|
| `library.msp` | 合并主库（NIST MS Search / MassHunter 可直接读；每条 `Comment` 内含 `library=` 归属） |
| `library.mgf` | 合并 MGF（每条含 `LIBRARY=` 字段） |
| `index.csv` | 全库索引（含 `library`、`inchikey_skeleton`＝InChIKey 前 14 位） |
| `compounds.csv` | 全库化合物汇总（含 `libraries` 列） |
| `coverage.csv` | 各库目标覆盖（保留 `library` 列，不混并语义） |
| `search.sh` | **统一检索入口**：`./search.sh <查询谱.msp|mgf> [match.py 参数]` |
| `scripts/merge_libraries.py` | 重新生成以上全部产物 |

## 三、用法

**① 一键检索（转发到 `spectral-matching` 技能）**

```bash
./search.sh /path/to/unknown.msp                 # 默认 top10、前体 50 ppm
./search.sh unknown.mgf --adduct '[M-H]-' --top 5 --method entropy,cosine_greedy
```
**② 只想在单个库内检索**：把 `--library` 指向 `../谱库-金线莲/library.msp`（或人参）。

**③ 只想检索某类记录**：按 `index.csv` 的 `library` / `ms_type` / `n_peaks` 过滤出子集后再建库，例如
```bash
python3 - <<'PY'
import csv;rows=[r for r in csv.DictReader(open('index.csv',encoding='utf-8')) if r['library']=='金线莲' and r['ms_type']=='MS2' and int(r['n_peaks'])>=5]
print(len(rows))
PY
```
**④ NIST MS Search / MassHunter** → 打开 `library.msp`；**MS-DIAL / MZmine / GNPS** → 用 `library.mgf`。

## 四、重要提示

1. **检索前先过滤 `ms_type==MS2`**（本库含 187 条一级谱），并按「极性 + 加合物 + 前体 ppm + 碰撞能量」一致后再算相似度。
2. 跨库重复已去重（同一谱同为两库目标者共 1211 条），`library` 列标注为 `人参;金线莲`。
3. **更新流程**：先在分库内重跑 `build_library.py`（可含 `user/` 自测谱）→ 再回本目录跑 `scripts/merge_libraries.py`。
4. `user/` 自测谱请放入**对应分库**的 `谱库-*/user/`；合并库不直接收谱。
5. 置信度：MS² 库匹配最高到 **Schymanski Level 2**；同分异构需保留时间、标准品或离子淌度 CCS。

## 五、溯源

数据来源、逐目标覆盖率和已知局限详见各分库说明：
- `../谱库-人参/README.md`（人参）
- `../谱库-金线莲/README.md`（金线莲）
