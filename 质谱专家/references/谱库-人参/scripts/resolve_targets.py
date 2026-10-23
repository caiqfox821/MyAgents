#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 targets.tsv 全部解析为 PubChem CID/InChIKey/分子式/单同位素质量（用于覆盖报告）"""
import os, sys, csv, json, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lib_common import load_targets, monoisotopic

def get(url, timeout=15, tries=3):
    for i in range(tries):
        try:
            return urllib.request.urlopen(url, timeout=timeout).read()
        except Exception as e:
            if i == tries - 1: return None
            time.sleep(1.5)

def resolve(name):
    enc = urllib.parse.quote(name)
    url = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/%s/"
           "property/InChIKey,MolecularFormula,ExactMass,IsomericSMILES/JSON" % enc)
    raw = get(url)
    if not raw: return None
    try:
        p = json.loads(raw.decode())["PropertyTable"]["Properties"][0]
        return {"cid": p["CID"], "inchikey": p["InChIKey"], "formula": p.get("MolecularFormula",""),
                "exact_mass": p.get("ExactMass",""), "smiles": p.get("IsomericSMILES","")}
    except Exception:
        return None

targets = load_targets(os.path.join(HERE, "targets.tsv"))
rows = []
for t in targets:
    r = resolve(t["name"]) or {}
    fm = r.get("formula","")
    mono = monoisotopic(fm) if fm else ""
    rows.append([t["name"], t["group"], t["note"], r.get("cid",""), r.get("inchikey",""),
                 fm, mono, r.get("exact_mass",""), r.get("smiles","")])
    print("%-32s %-12s %s" % (t["name"][:32], r.get("inchikey","(未解析)")[:27], fm), flush=True)

with open(os.path.join(BASE, "raw", "targets_resolved.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["target_name","group","note","pubchem_cid","inchikey","formula",
                "monoisotopic_mass","pubchem_exact_mass","isomeric_smiles"])
    for r in rows: w.writerow(r)
ok = sum(1 for r in rows if r[4])
print("DONE resolved %d/%d" % (ok, len(rows)))
