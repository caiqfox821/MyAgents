#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 3: 汇总 MassBank + GNPS(含 MoNA/MASSBANK 镜像) -> library.msp / library.mgf / index.csv / compounds.csv / coverage.csv"""
import csv, json, os, sys, glob, re
from collections import defaultdict, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lib_common import (monoisotopic, adduct_mz, norm_name, gnps_base_name,
                        load_targets, target_index, match_target)

RAW = os.path.join(BASE, "raw")
MB  = os.path.join(RAW, "massbank")
GN  = os.path.join(RAW, "gnps")

targets = load_targets(os.path.join(HERE, "targets.tsv"))
TIDX = target_index(targets)
TARGET_NAMES = {t["name"] for t in targets}

# ---------- 读取 MassBank ----------
def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

meta = read_csv(os.path.join(MB, "spectra_meta.csv")) if os.path.exists(os.path.join(MB,"spectra_meta.csv")) else []
peaks_rows = read_csv(os.path.join(MB, "peaks.csv")) if os.path.exists(os.path.join(MB,"peaks.csv")) else []

peaks_by_spectrum = defaultdict(list)
for p in peaks_rows:
    try:
        peaks_by_spectrum[p["spectrum"]].append((float(p["mz"]), float(p["rel"] or 0)))
    except Exception:
        pass

# 按谱图聚合元数据（同谱多 label 去重）
mb_meta = OrderedDict()
for r in meta:
    sid = r["spectrum"]
    if sid not in mb_meta:
        mb_meta[sid] = dict(r)
    else:
        for k, v in r.items():
            if not mb_meta[sid].get(k) and v:
                mb_meta[sid][k] = v

def ionchar(m):
    m = (m or "").upper()
    return "P" if m.startswith("POS") else ("N" if m.startswith("NEG") else "")

def mb_records():
    for sid, r in mb_meta.items():
        formula = r.get("formula", "")
        mass = monoisotopic(formula) or (float(r["mass"]) if r.get("mass") else None)
        name = r.get("name", "")
        tname = match_target(name, TIDX) or name
        ik = (r.get("ik", "") or "").split("/")[-1]
        yield {
            "source": "MassBank",
            "record_id": r.get("id", ""),
            "name": tname,
            "raw_name": name,
            "inchikey": ik,
            "formula": formula,
            "mass": mass,
            "mb_mass_reported": r.get("mass", ""),
            "precursor_mz": float(r["prec"]) if r.get("prec") else adduct_mz(mass, r.get("prectype", "")),
            "adduct": r.get("prectype", ""),
            "ion_mode": ionchar(r.get("ion")),
            "ms_type": r.get("mstype", ""),
            "ce": r.get("ce", ""),
            "instrument": r.get("itype", "") or r.get("acinst", ""),
            "splash": r.get("splash", ""),
            "smiles": r.get("smiles", ""),
            "title": r.get("title", ""),
            "npeaks": len(peaks_by_spectrum.get(sid, [])),
            "peaks": sorted(peaks_by_spectrum.get(sid, []), key=lambda x: x[0]),
            "matched_target": match_target(name, TIDX) or "",
        }

TARGET_META = {}
def _compute_tmap():
    global TARGET_META
    for sid, r in mb_meta.items():
        tname = match_target(r.get("name", ""), TIDX)
        ik = (r.get("ik", "") or "").split("/")[-1]
        if tname and tname not in TARGET_META and ik:
            TARGET_META[tname] = {"inchikey": ik, "formula": r.get("formula", ""),
                                  "mass": monoisotopic(r.get("formula", ""))}
_compute_tmap()

# ---------- 读取 GNPS ----------
ADDUCT_RE = re.compile(r'\[?(\d*)M([+\-][A-Za-z0-9]+)?\]?([+\-])')

def gnps_adduct(name, charge):
    m = ADDUCT_RE.search(name or "")
    if not m:
        return ""
    mult, tail, sign = m.group(1), m.group(2) or "", m.group(3)
    pre = (mult or "") + "M"
    return "[%s%s]%s" % (pre, tail, sign)

def gnps_records():
    out = []
    for path in sorted(glob.glob(os.path.join(GN, "gnps_hits*.jsonl"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                h = json.loads(line)
                fn = h.get("source", "")
                if fn == "MASSBANK.mgf":
                    continue          # 与主库 MassBank(RDF) 重复，跳过
                src = "MoNA" if fn.startswith("MONA") else "GNPS"
                # 以本库 targets 重新判定（防旧 hits 文件里残留他库同义名匹配）
                tname = match_target(h["name"], TIDX)
                if not tname and (h.get("matched_target") or "") in TARGET_NAMES:
                    tname = h["matched_target"]
                if not tname:
                    continue  # 只保留命中本库目标清单的 GNPS 记录
                peaks = sorted((float(a), float(b)) for a, b in h["peaks"])
                if peaks:
                    mx = max(p[1] for p in peaks) or 1.0
                    peaks = [(a, round(b / mx * 100.0, 1)) for a, b in peaks]  # 归一到基峰100
                dm = TARGET_META.get(tname, {})
                charge = h.get("charge", "") or "1"
                try: charge = int(float(charge))
                except Exception: charge = 1
                out.append({
                    "source": src,
                    "record_id": h.get("spectrumid", ""),
                    "name": tname,
                    "raw_name": h.get("name", ""),
                    "inchikey": (h.get("inchiaux", "") if h.get("inchiaux", "") not in ("", "N/A") else dm.get("inchikey", "")),
                    "formula": dm.get("formula", ""),
                    "mass": dm.get("mass"),
                    "mb_mass_reported": "",
                    "precursor_mz": (float(str(h["pepmass"]).split()[0]) if h.get("pepmass") else None),
                    "adduct": gnps_adduct(h.get("name", ""), charge),
                    "ion_mode": ionchar(h.get("ionmode", "") or ("POSITIVE" if "M+H" in h.get("name","") else "NEGATIVE")),
                    "ms_type": "MS" + str(h.get("mslevel", "") or "2"),
                    "ce": "",
                    "instrument": h.get("instrument", ""),
                    "splash": "",
                    "smiles": h.get("smiles", ""),
                    "title": h.get("name", ""),
                    "npeaks": len(peaks),
                    "peaks": peaks,
                    "matched_target": tname,
                    "library": h.get("source", ""),
                })
    return out

# ---------- 用户自测谱（实验补充，放入 <库>/user/*.mgf 或 *.msp）----------
def norm_ion(s):
    s = (s or "").strip().upper()
    if s.startswith("P") or s == "+" or s.startswith("POS"): return "P"
    if s.startswith("N") or s == "-": return "N"
    return ""

def _user_rec(d, peaks, fname, need_norm):
    if need_norm and peaks:
        mx = max(p[1] for p in peaks) or 1.0
        peaks = [(a, round(b/mx*100.0, 1)) for a, b in peaks]
    peaks = sorted(peaks)
    nm = d.get("name") or d.get("title") or ""
    fmt = d.get("formula","")
    mass = monoisotopic(fmt) if fmt else None
    try: pmz = float(str(d.get("precursormz") or d.get("pepmass") or "").split()[0])
    except Exception: pmz = None
    return {
     "source":"User(实验)", "record_id": d.get("db#") or d.get("spectrumid") or fname,
     "name": nm, "raw_name": nm, "inchikey": d.get("inchikey",""), "formula": fmt, "mass": mass,
     "mb_mass_reported":"", "precursor_mz": pmz or adduct_mz(mass, d.get("precursor_type","")),
     "adduct": d.get("precursor_type",""), "ion_mode": norm_ion(d.get("ion_mode")),
     "ms_type": d.get("spectrum_type","MS2"), "ce": d.get("collision_energy",""),
     "instrument": d.get("instrument_type",""), "splash": d.get("splash",""),
     "smiles": d.get("smiles",""), "title": d.get("title", nm), "npeaks": len(peaks), "peaks": peaks,
     "matched_target": d.get("matched_target","") or match_target(nm, TIDX) or "",
     "library": "user/" + fname,
    }

def user_records():
    out = []; udir = os.path.join(BASE, "user")
    for path in sorted(glob.glob(os.path.join(udir, "*.mgf"))):
        hdr = None; peaks = None
        for line in open(path, encoding="utf-8", errors="ignore"):
            line = line.rstrip("\n")
            if line.startswith("BEGIN IONS"): hdr = {}; peaks = []
            elif line.startswith("END IONS"):
                if hdr is not None: out.append(_user_rec(hdr, peaks or [], os.path.basename(path), True))
                hdr = None; peaks = None
            elif hdr is not None and line:
                if "=" in line and not line[0].isdigit() and line[0] != "-":
                    k, _, v = line.partition("="); hdr[k.strip().upper()] = v.strip()
                else:
                    p = line.split()
                    if len(p) >= 2:
                        try: peaks.append((float(p[0]), float(p[1])))
                        except Exception: pass
    for path in sorted(glob.glob(os.path.join(udir, "*.msp"))):
        for b in open(path, encoding="utf-8", errors="ignore").read().split("\n\n"):
            cur = {}; pk = []
            for line in b.splitlines():
                if not line.strip(): continue
                if ":" in line and not re.match(r'^\s*[\d.+-]', line):
                    k, _, v = line.partition(":"); cur[k.strip().lower()] = v.strip()
                else:
                    p = line.split()
                    if len(p) >= 2:
                        try: pk.append((float(p[0]), float(p[1])))
                        except Exception: pass
            if cur.get("name") or pk:
                out.append(_user_rec(cur, pk, os.path.basename(path), False))
    return out

MB_RECS = list(mb_records())
GN_RECS = gnps_records()
USER_RECS = user_records()
ALL = MB_RECS + GN_RECS + USER_RECS
# 丢弃无峰记录（空谱对检索无用；MassBank 峰表未抓全时会出现）
_nopk = sum(1 for r in ALL if not r.get("peaks"))
if _nopk:
    print("跳过无峰记录: %d（可由 fetch_peaks.py 补齐后重跑）" % _nopk)
ALL = [r for r in ALL if r.get("peaks")]
# 去重 (source, record_id)
seen = set(); RECS = []
for r in ALL:
    k = (r["source"], r["record_id"], tuple(r["peaks"][:1]))
    if k in seen: continue
    seen.add(k); RECS.append(r)
print("MassBank spectra:", len(MB_RECS), " GNPS(target-matched):", len(GN_RECS),
      " User(实验):", len(USER_RECS), " total(有峰):", len(RECS))

# ---------- 写 library.msp ----------
def fmt(x, nd=5):
    return ("%.*f" % (nd, x)).rstrip("0").rstrip(".") if isinstance(x, float) else (str(x) if x is not None else "")

with open(os.path.join(BASE, "library.msp"), "w", encoding="utf-8") as f:
    for i, r in enumerate(RECS, 1):
        f.write("Name: %s\n" % (r["name"] or r["raw_name"]))
        f.write("DB#: %s\n" % r["record_id"])
        f.write("DB: %s\n" % r["source"])
        if r["inchikey"]:  f.write("InChIKey: %s\n" % r["inchikey"])
        if r["formula"]:   f.write("Formula: %s\n" % r["formula"])
        if r["mass"]:      f.write("ExactMass: %s\n" % fmt(r["mass"], 5))
        if r["precursor_mz"]: f.write("PrecursorMZ: %s\n" % fmt(r["precursor_mz"], 4))
        if r["adduct"]:    f.write("Precursor_type: %s\n" % r["adduct"])
        if r["ion_mode"]:  f.write("Ion_mode: %s\n" % r["ion_mode"])
        if r["ms_type"]:   f.write("Spectrum_type: %s\n" % r["ms_type"])
        if r["ce"]:        f.write("Collision_energy: %s\n" % r["ce"])
        if r["instrument"]: f.write("Instrument_type: %s\n" % r["instrument"])
        if r["splash"]:    f.write("Splash: %s\n" % r["splash"])
        comment = "source=%s; record=%s; matched=%s; raw_name=%s" % (
            r["source"], r["record_id"], r["matched_target"] or "-", (r["raw_name"] or "")[:60])
        if r["mb_mass_reported"]:
            comment += "; MB_ch_exact_mass=%s" % r["mb_mass_reported"]
        if r.get("library"): comment += "; library=%s" % r["library"]
        f.write("Comment: \"%s\"\n" % comment.replace('"', "'"))
        f.write("Num Peaks: %d\n" % r["npeaks"])
        for mz, it in r["peaks"]:
            f.write("%s %s\n" % (fmt(mz, 4), fmt(it, 1)))
        f.write("\n")

# ---------- 写 library.mgf ----------
with open(os.path.join(BASE, "library.mgf"), "w", encoding="utf-8") as f:
    for r in RECS:
        f.write("BEGIN IONS\n")
        f.write("TITLE=%s|%s\n" % (r["name"], r["record_id"]))
        f.write("NAME=%s\n" % (r["name"] or r["raw_name"]))
        if r["precursor_mz"]: f.write("PEPMASS=%.4f\n" % r["precursor_mz"])
        f.write("CHARGE=1%s\n" % ("+" if r["ion_mode"] == "P" else "-"))
        f.write("MSLEVEL=%s\n" % (r["ms_type"].replace("MS", "") or "2"))
        f.write("IONMODE=%s\n" % ("Positive" if r["ion_mode"] == "P" else "Negative"))
        if r["adduct"]:     f.write("ADDUCT=%s\n" % r["adduct"])
        f.write("SOURCE_INSTRUMENT=%s\n" % r["instrument"])
        if r["inchikey"]:   f.write("INCHIKEY=%s\n" % r["inchikey"])
        if r["formula"]:    f.write("FORMULA=%s\n" % r["formula"])
        if r["smiles"]:     f.write("SMILES=%s\n" % r["smiles"])
        if r["ce"]:         f.write("COLLISIONENERGY=%s\n" % r["ce"])
        f.write("SPECTRUMID=%s\n" % r["record_id"])
        f.write("SOURCE=%s\n" % r["source"])
        f.write("MATCHED_TARGET=%s\n" % (r["matched_target"] or ""))
        for mz, it in r["peaks"]:
            f.write("%.4f\t%.1f\n" % (mz, it))
        f.write("END IONS\n\n")

# ---------- 写 index.csv ----------
with open(os.path.join(BASE, "index.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["source","record_id","name","matched_target","inchikey","formula","monoisotopic_mass",
                "precursor_mz","adduct","ion_mode","ms_type","collision_energy","instrument",
                "n_peaks","splash","smiles","title"])
    for r in RECS:
        w.writerow([r["source"], r["record_id"], r["name"], r["matched_target"], r["inchikey"],
                    r["formula"], fmt(r["mass"],5), fmt(r["precursor_mz"],4) if r["precursor_mz"] else "",
                    r["adduct"], r["ion_mode"], r["ms_type"], r["ce"], r["instrument"],
                    r["npeaks"], r["splash"], r["smiles"], r["title"]])

# ---------- 写 compounds.csv（库内化合物汇总）----------
comp = OrderedDict()
for r in RECS:
    key = r["matched_target"] or norm_name(r["name"])
    c = comp.setdefault(key, {"name": r["name"], "target": r["matched_target"], "inchikey": r["inchikey"],
                              "formula": r["formula"], "mass": r["mass"],
                              "n_total": 0, "n_pos": 0, "n_neg": 0, "sources": set(),
                              "precursors": set(), "adducts": set()})
    c["n_total"] += 1
    if r["ion_mode"] == "P": c["n_pos"] += 1
    if r["ion_mode"] == "N": c["n_neg"] += 1
    c["sources"].add(r["source"])
    if r["precursor_mz"]: c["precursors"].add(round(r["precursor_mz"], 3))
    if r["adduct"]: c["adducts"].add(r["adduct"])
    if not c["inchikey"] and r["inchikey"]: c["inchikey"] = r["inchikey"]
    if not c["formula"] and r["formula"]: c["formula"] = r["formula"]

with open(os.path.join(BASE, "compounds.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["compound","matched_target","inchikey","formula","monoisotopic_mass",
                "n_spectra","n_positive","n_negative","sources","precursors_mz","adducts"])
    for c in sorted(comp.values(), key=lambda x: (-x["n_total"], x["name"])):
        w.writerow([c["name"], c["target"], c["inchikey"], c["formula"], fmt(c["mass"],5),
                    c["n_total"], c["n_pos"], c["n_neg"], "|".join(sorted(c["sources"])),
                    "|".join(str(p) for p in sorted(c["precursors"])),
                    "|".join(sorted(c["adducts"]))])
print("unique compounds in library:", len(comp))

# ---------- 写 coverage.csv（目标清单覆盖情况）----------
found = defaultdict(lambda: {"n": 0, "sources": set(), "ik": ""})
for r in RECS:
    if r["matched_target"]:
        f_ = found[r["matched_target"]]
        f_["n"] += 1; f_["sources"].add(r["source"])
        if not f_["ik"] and r["inchikey"]: f_["ik"] = r["inchikey"]

with open(os.path.join(BASE, "coverage.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["target_name","group","note","n_spectra","sources","inchikey","status"])
    for t in targets:
        f_ = found.get(t["name"])
        n = f_["n"] if f_ else 0
        w.writerow([t["name"], t["group"], t["note"], n,
                    "|".join(sorted(f_["sources"])) if f_ else "",
                    f_["ik"] if f_ else "",
                    "收录" if n else "缺失"])
print("DONE")
