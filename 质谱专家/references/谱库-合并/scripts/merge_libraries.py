#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把同级目录下所有「谱库-*」合并成一个统一检索入口。

产出（本目录）：
  library.msp / library.mgf   全部记录（跨库去重；同一 source+record_id 只保留一份）
  index.csv                   全库索引，含 `library`（归属库）与 `inchikey_skeleton`（前 14 位）
  compounds.csv               全库化合物汇总
  coverage.csv                各库目标覆盖（保留 library 列，不跨库合并语义）
  README.md                   说明与用法

用法：python3 scripts/merge_libraries.py
数据源：`references/谱库-*/`（含 library.msp + index.csv 者，自动发现；排除本目录）
"""
import csv, io, os, re, sys
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)                    # .../references/谱库-合并
REF  = os.path.dirname(BASE)                    # .../references
SELF = os.path.basename(BASE)

DISCOVER = sorted(
    d for d in os.listdir(REF)
    if d.startswith("谱库-") and d != SELF
    and os.path.exists(os.path.join(REF, d, "library.msp"))
    and os.path.exists(os.path.join(REF, d, "index.csv"))
)
if not DISCOVER:
    sys.exit("未发现可合并的谱库目录（需含 library.msp + index.csv）")

def read_csv_rows(path):
    with io.open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def lib_label(dirname):
    return dirname[len("谱库-"):]               # 谱库-人参 -> 人参

# ---------- 解析 MSP / MGF 记录块 ----------
def parse_msp(txt):
    out = []
    for blk in txt.split("\n\n"):
        blk = blk.strip("\n")
        if not blk.strip():
            continue
        db  = re.search(r"^DB: (.+)$",  blk, re.M)
        rid = re.search(r"^DB#: (.+)$", blk, re.M)
        if db and rid:
            out.append(((db.group(1).strip(), rid.group(1).strip()), blk))
    return out

def parse_mgf(txt):
    out = []
    for m in re.finditer(r"BEGIN IONS\n(.*?)\nEND IONS", txt, re.S):
        body = m.group(1).strip("\n")
        src = re.search(r"^SOURCE=(.+)$", body, re.M)
        sid = re.search(r"^SPECTRUMID=(.+)$", body, re.M)
        if src and sid:
            out.append(((src.group(1).strip(), sid.group(1).strip()), body))
    return out

# ---------- 汇总 ----------
records = OrderedDict()   # (source, record_id) -> {"libs":[..], "msp":str, "mgf":str, "row":dict}
cover_rows = []
comp_by_lib = {}

for d in DISCOVER:
    lab = lib_label(d)
    root = os.path.join(REF, d)
    with io.open(os.path.join(root, "library.msp"), encoding="utf-8") as f:
        msp_map = dict(parse_msp(f.read()))
    with io.open(os.path.join(root, "library.mgf"), encoding="utf-8") as f:
        mgf_map = dict(parse_mgf(f.read()))
    for r in read_csv_rows(os.path.join(root, "index.csv")):
        key = (r["source"], r["record_id"])
        e = records.get(key)
        if e is None:
            e = records[key] = {"libs": [], "msp": msp_map.get(key), "mgf": mgf_map.get(key),
                                "row": r}
        if lab not in e["libs"]:
            e["libs"].append(lab)
    for r in read_csv_rows(os.path.join(root, "coverage.csv")):
        row = {"library": lab}
        row.update(r)
        cover_rows.append(row)
    comp_by_lib[lab] = read_csv_rows(os.path.join(root, "compounds.csv"))

missing_msp = [k for k, e in records.items() if not e["msp"]]
print("发现谱库: %s" % ", ".join(DISCOVER))
print("合并后记录: %d（各库合计 %d，跨库去重 %d）" % (
    len(records),
    sum(1 for _ in records) + sum(len(e["libs"]) - 1 for e in records.values()),
    sum(len(e["libs"]) - 1 for e in records.values())))
if missing_msp:
    print("!! 有 %d 条在 index.csv 但 library.msp 中缺块（将跳过）" % len(missing_msp))
shared = sum(1 for e in records.values() if len(e["libs"]) > 1)
print("两库共有记录（去重）: %d" % shared)

def with_libs_msp(blk, libs):
    tag = ";".join(libs)
    m = re.search(r'^Comment: "(.*)"$', blk, re.M)
    if m:
        return blk[:m.start()] + 'Comment: "%s; library=%s"' % (m.group(1), tag) + blk[m.end():]
    return blk + "\nLIBRARY: %s" % tag

def with_libs_mgf(body, libs):
    return re.sub(r"^SOURCE=(.+)$", lambda m: "SOURCE=%s\nLIBRARY=%s" % (m.group(1), ";".join(libs)),
                  body, count=1, flags=re.M)

# ---------- 写出 ----------
with io.open(os.path.join(BASE, "library.msp"), "w", encoding="utf-8") as f:
    n = 0
    for k, e in records.items():
        if not e["msp"]:
            continue
        f.write(with_libs_msp(e["msp"], e["libs"]) + "\n\n")
        n += 1
    print("library.msp: %d 条" % n)

with io.open(os.path.join(BASE, "library.mgf"), "w", encoding="utf-8") as f:
    n = 0
    for k, e in records.items():
        if not e["mgf"]:
            continue
        f.write("BEGIN IONS\n" + with_libs_mgf(e["mgf"], e["libs"]) + "\nEND IONS\n\n")
        n += 1
    print("library.mgf: %d 条" % n)

COLS = ["library", "source", "record_id", "name", "matched_target", "inchikey",
        "inchikey_skeleton", "formula", "monoisotopic_mass", "precursor_mz", "adduct",
        "ion_mode", "ms_type", "collision_energy", "instrument", "n_peaks", "splash",
        "smiles", "title"]
with io.open(os.path.join(BASE, "index.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(COLS)
    for k, e in records.items():
        if not e["msp"]:
            continue
        r = e["row"]
        ik = r.get("inchikey", "")
        w.writerow([";".join(e["libs"]), r["source"], r["record_id"], r["name"],
                    r["matched_target"], ik, ik[:14], r["formula"],
                    r["monoisotopic_mass"], r["precursor_mz"], r["adduct"], r["ion_mode"],
                    r["ms_type"], r["collision_energy"], r["instrument"], r["n_peaks"],
                    r["splash"], r["smiles"], r["title"]])
print("index.csv: %d 条" % sum(1 for e in records.values() if e["msp"]))

# ---------- compounds.csv（全库化合物汇总）----------
comp = OrderedDict()
for k, e in records.items():
    if not e["msp"]:
        continue
    r = e["row"]
    key = r["matched_target"] or (r["name"] or "").lower()
    c = comp.setdefault(key, {"compound": r["name"], "matched_target": r["matched_target"],
                              "inchikey": r["inchikey"], "formula": r["formula"],
                              "monoisotopic_mass": r["monoisotopic_mass"],
                              "n_spectra": 0, "sources": set(), "libraries": set()})
    c["n_spectra"] += 1
    c["sources"].add(r["source"])
    c["libraries"].update(e["libs"])
    if not c["inchikey"] and r["inchikey"]:
        c["inchikey"] = r["inchikey"]
    if not c["formula"] and r["formula"]:
        c["formula"] = r["formula"]
with io.open(os.path.join(BASE, "compounds.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["compound", "matched_target", "inchikey", "formula", "monoisotopic_mass",
                "n_spectra", "sources", "libraries"])
    for key, c in sorted(comp.items(), key=lambda kv: -kv[1]["n_spectra"]):
        w.writerow([c["compound"], c["matched_target"], c["inchikey"], c["formula"],
                    c["monoisotopic_mass"], c["n_spectra"],
                    "|".join(sorted(c["sources"])), "|".join(sorted(c["libraries"]))])
print("compounds.csv: %d 个化合物" % len(comp))

# ---------- coverage.csv（保留各库语义，加 library 列）----------
cov_cols = ["library"]
for r in cover_rows:
    for c in r:
        if c not in cov_cols:
            cov_cols.append(c)
with io.open(os.path.join(BASE, "coverage.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cov_cols, extrasaction="ignore")
    w.writeheader()
    for r in cover_rows:
        w.writerow(r)
print("coverage.csv: %d 行（各库目标覆盖之并集）" % len(cover_rows))

# ---------- README.md（数字全部由数据算出，避免手改失真）----------
from collections import Counter
recs = [e for e in records.values() if e["msp"]]
src_counts = Counter(e["row"]["source"] for e in recs)
mem = Counter(";".join(e["libs"]) for e in recs)
n_ms2 = sum(1 for e in recs if e["row"]["ms_type"] == "MS2")
n_noik = sum(1 for e in recs if not e["row"]["inchikey"])
nps = sorted(int(e["row"]["n_peaks"]) for e in recs)
cov_by = defaultdict(Counter)
for r in cover_rows:
    cov_by[r["library"]]["总目标"] += 1
    cov_by[r["library"]][("收录" if r.get("status") == "收录" else "缺失")] += 1

L = []
L.append("# 统一检索入口 · 合并质谱参考谱库（%s）\n" % " + ".join(lib_label(d) for d in DISCOVER))
L.append("> 自动生成，请勿手改；由 `scripts/merge_libraries.py` 合并同级 `谱库-*` 得到。\n")
L.append("## 一、概况\n")
L.append("| 指标 | 数值 |")
L.append("|---|---|")
L.append("| 谱图总数 | **%d** |" % len(recs))
L.append("| 化合物（去重） | **%d** |" % len(comp))
L.append("| MS² 谱（ms_type=MS2） | %d |" % n_ms2)
L.append("| 非 MS² 谱（MS1 等） | %d |" % (len(recs) - n_ms2))
L.append("| n_peaks 范围（中位） | %d – %d（%d） |" % (nps[0], nps[-1], nps[len(nps)//2]))
L.append("| InChIKey 覆盖 | %d / %d（缺 %d） |" % (len(recs) - n_noik, len(recs), n_noik))
for s, k in src_counts.most_common():
    L.append("| 来源 %s | %d |" % (s, k))
L.append("")
L.append("**归属（跨库重复已去重）**\n")
L.append("| 归属 | 谱图数 |")
L.append("|---|---|")
for k, v in mem.most_common():
    L.append("| %s | %d |" % (k.replace(";", " + "), v))
L.append("")
L.append("**各库目标覆盖**\n")
L.append("| 库 | 目标 | 收录 | 缺失 |")
L.append("|---|---|---|---|")
for lab in cov_by:
    c = cov_by[lab]
    L.append("| %s | %d | %d | %d |" % (lab, c["总目标"], c["收录"], c["缺失"]))
L.append("")
L.append("## 二、文件\n")
L.append("| 文件 | 说明 |")
L.append("|---|---|")
L.append("| `library.msp` | 合并主库（NIST MS Search / MassHunter 可直接读；每条 `Comment` 内含 `library=` 归属） |")
L.append("| `library.mgf` | 合并 MGF（每条含 `LIBRARY=` 字段） |")
L.append("| `index.csv` | 全库索引（含 `library`、`inchikey_skeleton`＝InChIKey 前 14 位） |")
L.append("| `compounds.csv` | 全库化合物汇总（含 `libraries` 列） |")
L.append("| `coverage.csv` | 各库目标覆盖（保留 `library` 列，不混并语义） |")
L.append("| `search.sh` | **统一检索入口**：`./search.sh <查询谱.msp|mgf> [match.py 参数]` |")
L.append("| `scripts/merge_libraries.py` | 重新生成以上全部产物 |")
L.append("")
L.append("## 三、用法\n")
L.append("**① 一键检索（转发到 `spectral-matching` 技能）**\n")
L.append("```bash")
L.append("./search.sh /path/to/unknown.msp                 # 默认 top10、前体 50 ppm")
L.append("./search.sh unknown.mgf --adduct '[M-H]-' --top 5 --method entropy,cosine_greedy")
L.append("```")
L.append("**② 只想在单个库内检索**：把 `--library` 指向 `../谱库-金线莲/library.msp`（或人参）。")
L.append("")
L.append("**③ 只想检索某类记录**：按 `index.csv` 的 `library` / `ms_type` / `n_peaks` 过滤出子集后再建库，例如")
L.append("```bash")
L.append("python3 - <<'PY'")
L.append("import csv;rows=[r for r in csv.DictReader(open('index.csv',encoding='utf-8')) if r['library']=='金线莲' and r['ms_type']=='MS2' and int(r['n_peaks'])>=5]")
L.append("print(len(rows))")
L.append("PY")
L.append("```")
L.append("**④ NIST MS Search / MassHunter** → 打开 `library.msp`；**MS-DIAL / MZmine / GNPS** → 用 `library.mgf`。")
L.append("")
L.append("## 四、重要提示\n")
L.append("1. **检索前先过滤 `ms_type==MS2`**（本库含 %d 条一级谱），并按「极性 + 加合物 + 前体 ppm + 碰撞能量」一致后再算相似度。" % (len(recs) - n_ms2))
L.append("2. 跨库重复已去重（同一谱同为两库目标者共 %d 条），`library` 列标注为 `人参;金线莲`。" % mem.get("人参;金线莲", 0))
L.append("3. **更新流程**：先在分库内重跑 `build_library.py`（可含 `user/` 自测谱）→ 再回本目录跑 `scripts/merge_libraries.py`。")
L.append("4. `user/` 自测谱请放入**对应分库**的 `谱库-*/user/`；合并库不直接收谱。")
L.append("5. 置信度：MS² 库匹配最高到 **Schymanski Level 2**；同分异构需保留时间、标准品或离子淌度 CCS。")
L.append("")
L.append("## 五、溯源\n")
L.append("数据来源、逐目标覆盖率和已知局限详见各分库说明：")
for d in DISCOVER:
    L.append("- `../%s/README.md`（%s）" % (d, lib_label(d)))
L.append("")
with io.open(os.path.join(BASE, "README.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("README.md 已生成")

