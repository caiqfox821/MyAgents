#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 README.md 与《覆盖与稀有皂苷清单.md》"""
import csv, os, json, sys, datetime
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lib_common import monoisotopic, adduct_mz

def read(path):
    p = os.path.join(BASE, path)
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []

idx  = read("index.csv")
comp = read("compounds.csv")
cov  = read("coverage.csv")
res  = {r["target_name"]: r for r in read("raw/targets_resolved.csv")}

def n_src(rows):
    c = Counter(r["source"] for r in rows)
    return c

src_counts = n_src(idx)
n_spec = len(idx)
n_comp = len(comp)
pos = sum(1 for r in idx if r["ion_mode"] == "P")
neg = sum(1 for r in idx if r["ion_mode"] == "N")
today = datetime.date.today().isoformat()

covered = [r for r in cov if int(r["n_spectra"] or 0) > 0]
missing = [r for r in cov if int(r["n_spectra"] or 0) == 0]

def group_rows(g):
    return [r for r in cov if r["group"] == g]

# ---------- README ----------
L = []
L.append("# 人参皂苷与活性成分 质谱参考谱库\n")
L.append("> 生成日期：%s ｜ 来源：MassBank + GNPS/MoNA 镜像（多库合并）\n" % today)
L.append("## 一、概况\n")
L.append("| 指标 | 数值 |")
L.append("|---|---|")
L.append("| 谱图总数 | **%d** |" % n_spec)
L.append("| 化合物数（去重） | **%d** |" % n_comp)
L.append("| 正离子谱 | %d |" % pos)
L.append("| 负离子谱 | %d |" % neg)
for s, k in src_counts.most_common():
    L.append("| 来源 %s | %d |" % (s, k))
L.append("| 目标清单化合物 | %d |" % len(cov))
L.append("| 目标清单已收录 | %d |" % len(covered))
L.append("| 目标清单未收录 | %d |" % len(missing))
L.append("")
L.append("## 二、数据来源与版本\n")
L.append("| 来源 | 文件/接口 | 说明 |")
L.append("|---|---|---|")
L.append("| MassBank | `https://rdfportal.org/primary/sparql`（GRAPH massbank） | 主库（RDF Portal SPARQL，权威参考谱）；本库 %d 条 |" % src_counts.get("MassBank", 0))
L.append("| GNPS-LIBRARY.mgf / GNPS-NIH-NATURALPRODUCTSLIBRARY.mgf | `https://external.gnps2.org/gnpslibrary/`（MGF 镜像） | GNPS 社区库；命中本库目标 %d 条 |" % src_counts.get("GNPS", 0))
L.append("| MONA.mgf | 同上 | MoNA（MassBank of North America）镜像；命中本库目标 %d 条 |" % src_counts.get("MoNA", 0))
L.append("| MASSBANK.mgf | 同上 | MassBank 的 GNPS 镜像，**已跳过**（与 MassBank RDF 主库重复） |")
L.append("| `user/*.msp`、`user/*.mgf` | 本地（实验自测） | 若存在则并入，source=`User(实验)`；当前 %d 条 |" % src_counts.get("User(实验)", 0))
L.append("")
L.append("> 下载日期：%s。检索脚本见 `scripts/`。\n" % today)

L.append("## 三、收录化合物一览\n")
L.append("按谱图条数排序（详见 `compounds.csv`）：\n")
L.append("| 化合物 | 目标名 | InChIKey | 分子式 | 单同位素质量 | 谱图数 | 来源 |")
L.append("|---|---|---|---|---|---|---|")
for c in comp:
    L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
        c["compound"], c["matched_target"] or "-", c["inchikey"] or "-", c["formula"] or "-",
        c["monoisotopic_mass"] or "-", c["n_spectra"], c["sources"]))
L.append("")

L.append("## 四、目标清单覆盖情况\n")
for g in ["皂苷-常见", "皂苷-稀有", "皂苷-其他"]:
    rows = group_rows(g)
    if not rows: continue
    L.append("### %s\n" % g)
    L.append("| 目标 | 谱图数 | 状态 |")
    L.append("|---|---|---|")
    for r in rows:
        L.append("| %s | %s | %s |" % (r["target_name"], r["n_spectra"], r["status"]))
    L.append("")
for g in ["苷元", "活性成分"]:
    rows = group_rows(g)
    if not rows: continue
    L.append("### %s\n" % g)
    L.append("| 目标 | 谱图数 | 状态 |")
    L.append("|---|---|---|")
    for r in rows:
        L.append("| %s | %s | %s |" % (r["target_name"], r["n_spectra"], r["status"]))
    L.append("")
L.append("")

L.append("## 五、文件清单\n")
L.append("| 文件 | 说明 |")
L.append("|---|---|")
L.append("| `library.msp` | NIST/MassHunter 兼容主库（每谱一条记录） |")
L.append("| `library.mgf` | MGF 格式（MS-DIAL / MZmine / GNPS 可直接读） |")
L.append("| `index.csv` | 谱图索引（来源、ID、化合物、母离子、加合物、碰撞能量等） |")
L.append("| `compounds.csv` | 库内化合物汇总（去重、谱图数、前体 m/z） |")
L.append("| `coverage.csv` | 目标清单覆盖表（收录/缺失） |")
L.append("| `raw/` | 原始数据（MassBank 元数据/峰表、GNPS MGF、目标解析） |")
L.append("| `scripts/` | 抓取与建库脚本 + `targets.tsv` 目标清单 |")
L.append("| `user/` | **自测（实验）谱图投放处**：放 `*.mgf` 或 `*.msp` 后重跑即并入 |")
L.append("")

L.append("## 六、使用说明\n")
L.append("**NIST MS Search / MassHunter**：直接打开 `library.msp` 作为用户谱库检索。\n")
L.append("**MS-DIAL / MZmine / GNPS**：用 `library.mgf` 建立本地库或做谱库比对。\n")
L.append("**自建脚本/编程**：读 `index.csv` + `raw/massbank/peaks.csv` 或直接解析 `library.mgf`。\n")
L.append("> 建议：母离子过滤 + 加合物 + 极性 + 碰撞能量一致后再算相似度；MS² 库匹配置信度最高到 Schymanski Level 2。\n")

L.append("## 七、如何补充自测（实验）谱图\n")
L.append("把鉴定确证的实测 MS² 谱放入本库 `user/` 目录（`*.mgf` 或 NIST `*.msp` 均可），然后重跑：\n")
L.append("```bash")
L.append("cd <本库>/scripts")
L.append("python3 build_library.py    # 自测谱以 source=User(实验) 并入 library.msp / .mgf / index.csv")
L.append("python3 make_report.py      # 刷新覆盖率与说明")
L.append("```")
L.append("MSP 记录建议含：`Name`、`InChIKey`、`Formula`、`PrecursorMZ`、`Precursor_type`、`Ion_mode`、`Collision_energy`、`Num Peaks` 及峰表；名称与目标清单一致时自动归入该目标（也可写 `MATCHED_TARGET=` 指定）。\n")

L.append("## 八、已知局限（务必阅读）\n")
L.append("1. **公开库覆盖不全**：目标清单中未能检索到实测 MS² 的化合物见 `coverage.csv` 与《覆盖与缺失清单》。公开免费库（MassBank / GNPS / MoNA）对它们确无记录——**「查不到」不等于「不存在」**，多属需自测、或仅散见于论文的稀有成分类。")
L.append("2. **同分异构体无法仅凭 MS² 区分**：分子式相同者（立体/位置异构）须靠色谱保留时间、标准品或离子淌度 CCS；本库相关同分异构对见 `notes_extra.md`。")
L.append("3. **MassBank 的 `ch_exact_mass` 字段不可靠**（部分为平均分子量），本库的质量已改由分子式重新计算（`ExactMass`），原始值保留在 `Comment` 中备查。")
L.append("4. **前体 m/z**：MassBank 多数记录未给前体值，本库按加合物由分子式推算并在 MSP 中给出 `PrecursorMZ`；如与实际仪器条件不符请以原始 `Comment` 为准。")
L.append("5. **强度标尺不同**：MassBank 为相对强度(%)；GNPS/MoNA 原始为绝对强度，本库已归一到基峰=100。")
L.append("6. **无保留时间/CCS**：均为谱库（MS²）参考谱，不含 RT/CCS。")
L.append("7. 多库合并存在**同化合物多来源重复**（保留各自来源记录，便于交叉验证）。")
L.append("8. 本库**保留全部**参考谱（含少量低信息量记录，如仅 1–2 个碎片的谱）。可在 `index.csv` 中按 `n_peaks` 列过滤（如 `n_peaks>=5`）后使用，以获得更干净的子库。")
L.append("")

L.append("## 九、补充说明与使用提示\n")
_extra = os.path.join(BASE, "notes_extra.md")
if os.path.exists(_extra):
    L.append(open(_extra, encoding="utf-8").read().rstrip() + "\n")
else:
    L.append("（本库暂无专属补充说明。）\n")

L.append("## 十、参考\n")
L.append("- MassBank: Horai et al., *J. Mass Spectrom.* 2010, 45, 703–714. 数据经 RDF Portal（https://rdfportal.org/dataset/massbank）获取。")
L.append("- GNPS / GNPS2: Wang et al., *Nat. Biotechnol.* 2016, 34, 828–837.")
L.append("- MoNA (MassBank of North America): https://mona.fiehnlab.ucdavis.edu")
L.append("")

open(os.path.join(BASE, "README.md"), "w", encoding="utf-8").write("\n".join(L))
print("README.md written:", n_spec, "spectra,", n_comp, "compounds")

# ---------- 覆盖与稀有皂苷清单 ----------
R = []
R.append("# 覆盖情况与稀有皂苷清单\n")
R.append("> 目标清单共 %d 个化合物，已收录 %d 个，未收录 %d 个。\n" % (len(cov), len(covered), len(missing)))
R.append("## 未收录（各公开库均无实测 MS²）\n")
R.append("| 目标 | 分组 | PubChem InChIKey | 分子式 | 单同位素质量 | [M+H]+ | [M-H]- |")
R.append("|---|---|---|---|---|---|---|")
for r in missing:
    rr = res.get(r["target_name"], {})
    fm = rr.get("formula", "")
    mono = monoisotopic(fm) if fm else None
    R.append("| %s | %s | %s | %s | %s | %s | %s |" % (
        r["target_name"], r["group"], rr.get("inchikey", "-") or "-", fm or "-",
        ("%.4f" % mono) if mono else "-",
        ("%.4f" % adduct_mz(mono, "[M+H]+")) if mono else "-",
        ("%.4f" % adduct_mz(mono, "[M-H]-")) if mono else "-"))
R.append("")
R.append("## 已收录\n")
R.append("| 目标 | 分组 | 谱图数 | 来源 |")
R.append("|---|---|---|---|")
for r in covered:
    R.append("| %s | %s | %s | %s |" % (r["target_name"], r["group"], r["n_spectra"], r["sources"]))
R.append("")
open(os.path.join(BASE, "覆盖与稀有皂苷清单.md"), "w", encoding="utf-8").write("\n".join(R))
print("coverage md written. missing:", len(missing))
