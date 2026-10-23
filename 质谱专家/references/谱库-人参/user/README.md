# user/ —— 实验自测谱投放处

把**实验鉴定确证**的 MS² 谱放进本目录（`*.msp` 或 `*.mgf`），然后重跑建库：

```bash
cd ../scripts
python3 build_library.py     # 自测谱以 source=User(实验) 并入 library.msp / .mgf / index.csv
python3 make_report.py       # 刷新覆盖率与说明
```

## 格式要求

- **MSP（NIST 兼容）** 建议字段：`Name`、`InChIKey`、`Formula`、`PrecursorMZ`、
  `Precursor_type`、`Ion_mode`（`P`/`N`）、`Collision_energy`、`Num Peaks` + 峰表（每行 `m/z 相对强度`）。
- **MGF**：`BEGIN IONS` / `NAME=` / `PEPMASS=` / `CHARGE=` / `IONMODE=` / `MSLEVEL=2` /
  `ADDUCT=` / `COLLISIONENERGY=` + 峰表 / `END IONS`。

## 自动归类

谱的名称若与本库 `../scripts/targets.tsv` 的目标（或其同义名）一致，会自动归入该目标并计入覆盖率；
也可用 `MATCHED_TARGET=<目标名>`（MSP 字段）显式指定。名称不在目标清单里的谱仍会入库
（`matched_target` 留空），作为「库外参考」保留。

## 命名建议

`<化合物>_<极性>_<CE>_<仪器>_<日期>.msp`，例如 `Kinsenoside_N_6V_QQQ_20261023.msp`。
