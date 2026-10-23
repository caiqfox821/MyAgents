#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 1: 目标清单 -> PubChem 解析 -> MassBank 谱图抓取"""
import csv, json, os, time, urllib.request, urllib.parse, sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(BASE, "raw")
MB   = os.path.join(RAW, "massbank")
os.makedirs(MB, exist_ok=True)
MBSPARQL = "https://rdfportal.org/primary/sparql"

def http(url, data=None, headers=None, timeout=90):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    return urllib.request.urlopen(req, timeout=timeout).read()

def pubchem(name):
    enc = urllib.parse.quote(name)
    url = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/%s/"
           "property/InChIKey,MolecularFormula,ExactMass,CanonicalSMILES/JSON" % enc)
    try:
        d = json.loads(http(url, timeout=30).decode())
        p = d["PropertyTable"]["Properties"][0]
        return {"cid": p["CID"], "ik": p["InChIKey"],
                "formula": p.get("MolecularFormula",""), "exact_mass": p.get("ExactMass",""),
                "smiles": p.get("CanonicalSMILES","")}
    except Exception as e:
        return None

def sparql(q):
    data = urllib.parse.urlencode({"query": q}).encode()
    raw = http(MBSPARQL, data=data, headers={"Accept":"application/sparql-results+json",
              "Content-Type":"application/x-www-form-urlencoded"}, timeout=300)
    b = json.loads(raw.decode())["results"]["bindings"]
    return [{k:v["value"] for k,v in row.items()} for row in b]

# ---------- 1. resolve ----------
targets = []
with open(os.path.join(BASE,"scripts","targets.tsv"), encoding="utf-8") as f:
    for line in f:
        line=line.rstrip("\n")
        if not line or line.startswith("#"): continue
        parts=line.split("\t")
        targets.append({"name":parts[0], "group":parts[1] if len(parts)>1 else "", "note":parts[2] if len(parts)>2 else ""})
print("targets:", len(targets))

resolved={}   # ik -> dict
for t in targets:
    r = pubchem(t["name"])
    t["resolved"] = r
    if r:
        resolved.setdefault(r["ik"], {"ik":r["ik"],"cid":r["cid"],"formula":r["formula"],
                                      "exact_mass":r["exact_mass"],"smiles":r["smiles"],
                                      "names":[t["name"]],"groups":[t["group"]]})
        resolved[r["ik"]]["names"].append(t["name"])
    else:
        print("  !! unresolved:", t["name"])
    time.sleep(0.25)

with open(os.path.join(RAW,"resolved.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["inchikey","skeleton","pubchem_cid","formula","monoisotopic_mass","smiles","name"])
    for ik,d in sorted(resolved.items()):
        w.writerow([ik, ik.split("-")[0], d["cid"], d["formula"], d["exact_mass"], d["smiles"], d["names"][0]])
print("resolved unique compounds:", len(resolved))

# ---------- 2. MassBank metadata ----------
skels = sorted({ik.split("-")[0] for ik in resolved})
vals = " ".join('"%s"'%s for s in skels)
qA = """
PREFIX mb: <http://www.massbank.jp/ontology/>
PREFIX schema: <https://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?spectrum ?id ?title (SAMPLE(?npeaks) AS ?npeaks) (SAMPLE(?ion) AS ?ion)
       (SAMPLE(?itype) AS ?itype) (SAMPLE(?mstype) AS ?mstype) (SAMPLE(?ce) AS ?ce)
       (SAMPLE(?acinst) AS ?acinst) (SAMPLE(?col) AS ?col) (SAMPLE(?rt) AS ?rt)
       (SAMPLE(?prec) AS ?prec) (SAMPLE(?prectype) AS ?prectype) (SAMPLE(?splash) AS ?splash)
       ?formula (SAMPLE(?mass) AS ?mass) ?ik (SAMPLE(?nm) AS ?name)
WHERE {
  VALUES ?sk { %s }
  ?c schema:inChIKey ?ik .
  BIND(SUBSTR(STR(?ik),33,14) AS ?s) FILTER(?s = ?sk)
  ?spectrum a mb:MassSpectrum ; mb:compound ?c ;
            dcterms:identifier ?id ; skos:definition ?title .
  OPTIONAL { ?spectrum mb:pk_num_peak ?npeaks }
  OPTIONAL { ?spectrum mb:pk_splash ?splash }
  OPTIONAL { ?spectrum mb:analytical_methods_and_conditions ?ac .
    OPTIONAL { ?ac mb:ion_mode ?ion } OPTIONAL { ?ac mb:instrument_type ?itype }
    OPTIONAL { ?ac mb:ms_type ?mstype } OPTIONAL { ?ac mb:collision_energy ?ce }
    OPTIONAL { ?ac mb:ac_instrument ?acinst } OPTIONAL { ?ac mb:column_name ?col }
    OPTIONAL { ?ac mb:retention_time ?rt } }
  OPTIONAL { ?spectrum mb:mass_spectram_meta_data ?m .
    OPTIONAL { ?m mb:precursor_mz_value ?prec } OPTIONAL { ?m mb:precursor_type_value ?prectype } }
  ?c schema:molecularFormula ?formula . OPTIONAL { ?c mb:ch_exact_mass ?mass }
  OPTIONAL { ?c rdfs:label ?nm }
} GROUP BY ?spectrum ?id ?title ?formula ?ik
""" % vals
print("querying MassBank metadata for %d skeletons ..." % len(skels))
meta = sparql(qA)
print("  spectra found:", len(meta))
keys=["spectrum","id","title","npeaks","ion","itype","mstype","ce","acinst","col","rt",
      "prec","prectype","splash","formula","mass","ik","name"]
with open(os.path.join(MB,"spectra_meta.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=keys); w.writeheader()
    for r in meta: w.writerow({k:r.get(k,"") for k in keys})

# ---------- 3. MassBank peaks ----------
ids = [r["spectrum"] for r in meta]
peaks=[]
CH=40
for i in range(0,len(ids),CH):
    chunk=ids[i:i+CH]
    v=" ".join("<%s>"%x for x in chunk)
    qB="""
PREFIX mb: <http://www.massbank.jp/ontology/>
SELECT ?spectrum ?mz ?rel ?intensity WHERE {
  VALUES ?spectrum { %s }
  GRAPH <http://rdfportal.org/dataset/massbank> {
    ?spectrum mb:has_peak ?p . ?p mb:mz ?mz ; mb:relative_intensity ?rel .
    OPTIONAL { ?p mb:intensity ?intensity }
  }
}""" % v
    try:
        peaks += sparql(qB)
    except Exception as e:
        print("  ! chunk %d failed: %s"%(i,e))
    print("  peaks chunk %d/%d  total=%d"%(i//CH+1, (len(ids)+CH-1)//CH, len(peaks)))
with open(os.path.join(MB,"peaks.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["spectrum","mz","rel","intensity"])
    for p in peaks: w.writerow([p.get("spectrum",""),p.get("mz",""),p.get("rel",""),p.get("intensity","")])
print("DONE. peaks:", len(peaks))
