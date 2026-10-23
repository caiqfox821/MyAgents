#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 2(GNPS/MoNA): 扫描所有 GNPS 镜像 MGF，筛出命中目标清单的记录"""
import os, re, json, glob, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
GP = os.path.join(BASE, "raw", "gnps")
MGF_DIR = os.environ.get("GNPS_MGF_DIR") or GP   # 可复用其他库已下载的镜像
os.makedirs(GP, exist_ok=True)
sys.path.insert(0, HERE)
from lib_common import load_targets, target_index, match_target, norm_name, gnps_base_name

targets = load_targets(os.path.join(HERE, "targets.tsv"))
TIDX = target_index(targets)

# 宽口径关键词：用于审计“库里有、但不在目标清单”的同族化合物
# 每库可用 scripts/broad_keywords.txt 覆盖（每行一条正则片段）
_DEF_KW = (
 r"ginsenoside|notoginsenoside|gypenoside|sanchinoside|panaxoside|vinaginsenoside|"
 r"majonoside|pseudoginsenoside|quinquenoside|ocotillol|protopanaxadiol|protopanaxatriol|"
 r"panaxadiol|panaxatriol|panaxynol|panaxydol|panaxytriol|falcarinol|"
 r"\bmaltol\b|hydroxymethylfurfural|aminobutyric acid|aminobutanoic|"
 r"\bquercetin\b|\bkaempferol\b|isorhamnetin|\brutin\b|\btrifolin\b|hyperoside|"
 r"oleanolic|ursolic|salicylic acid|vanillic acid|syringic acid|ferulic acid|caffeic acid|"
 r"coumaric acid|protocatechuic|gentisic|sitosterol|stigmasterol|daucosterol")
def _read_kw(path):
    if not os.path.exists(path): return None
    ls = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#"): ls.append(line)
    return "|".join(ls) if ls else None
KW = re.compile(_read_kw(os.path.join(HERE, "broad_keywords.txt")) or _DEF_KW, re.I)

def parse_mgf(path):
    hdr = None; peaks = None
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("BEGIN IONS"):
                hdr = {}; peaks = []
            elif line.startswith("END IONS"):
                if hdr is not None: yield hdr, peaks
                hdr = None; peaks = None
            elif hdr is not None and line:
                if "=" in line and not line[0].isdigit() and line[0] != "-":
                    k, _, v = line.partition("=")
                    hdr[k.strip().upper()] = v.strip()
                else:
                    p = line.split()
                    if len(p) >= 2:
                        try: peaks.append((float(p[0]), float(p[1])))
                        except Exception: pass

def rec(hdr, peaks, mtarget, broad):
    return {"source": os.path.basename(CUR[0]), "spectrumid": hdr.get("SPECTRUMID",""),
            "name": hdr.get("NAME","").strip('"'), "pepmass": hdr.get("PEPMASS",""),
            "charge": hdr.get("CHARGE",""), "ionmode": hdr.get("IONMODE",""),
            "mslevel": hdr.get("MSLEVEL",""), "instrument": hdr.get("SOURCE_INSTRUMENT",""),
            "smiles": hdr.get("SMILES",""), "inchiaux": hdr.get("INCHIAUX",""),
            "libraryquality": hdr.get("LIBRARYQUALITY",""),
            "matched_target": mtarget, "broad_keyword": broad,
            "npeaks": len(peaks), "peaks": peaks}

CUR = [""]
hits = []; broad_names = Counter()
for path in sorted(glob.glob(os.path.join(MGF_DIR, "*.mgf"))):
    CUR[0] = path; n_t = 0; n_b = 0
    for hdr, peaks in parse_mgf(path):
        name = hdr.get("NAME","")
        if not name: continue
        mt = match_target(name, TIDX)
        is_broad = bool(KW.search(name))
        if mt:
            hits.append(rec(hdr, peaks, mt, is_broad)); n_t += 1
        if is_broad:
            broad_names[gnps_base_name(name)] += 1; n_b += 1
    print("  %-45s target-matched=%d broad=%d" % (os.path.basename(path), n_t, n_b), flush=True)

with open(os.path.join(GP, "gnps_hits.jsonl"), "w", encoding="utf-8") as f:
    for h in hits: f.write(json.dumps(h, ensure_ascii=False) + "\n")
print("GNPS target-matched records:", len(hits))

with open(os.path.join(GP, "gnps_names_all.csv"), "w", encoding="utf-8") as f:
    f.write("name,n_spectra\n")
    for nm, k in broad_names.most_common():
        f.write('"%s",%d\n' % (nm.replace('"','""'), k))
print("broad distinct names:", len(broad_names))
