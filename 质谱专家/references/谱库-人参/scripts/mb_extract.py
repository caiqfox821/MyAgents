#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 1(MassBank): 通用抓取器
按 targets.tsv（+可选 scripts/aliases.txt 精确名、scripts/family_regex.txt 族名正则）
抓取参考谱的元数据与峰表。"""
import csv, json, os, urllib.request, urllib.parse, time, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
MB   = os.path.join(BASE, "raw", "massbank")
os.makedirs(MB, exist_ok=True)
EP   = os.environ.get("MB_SPARQL_EP", "https://rdfportal.org/primary/sparql")

def sparql(q, timeout=300):
    data = urllib.parse.urlencode({"query": q}).encode()
    req = urllib.request.Request(EP, data=data, headers={
        "Accept":"application/sparql-results+json",
        "Content-Type":"application/x-www-form-urlencoded"})
    b = json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode())
    return [{k:v["value"] for k,v in row.items()} for row in b["results"]["bindings"]]

def read_lines(p):
    if not os.path.exists(p): return []
    out=[]
    for line in open(p, encoding="utf-8"):
        line=line.strip()
        if line and not line.startswith("#"): out.append(line)
    return out

# 目标名
targets=[]
for line in open(os.path.join(HERE,"targets.tsv"), encoding="utf-8"):
    line=line.rstrip("\n")
    if not line or line.startswith("#"): continue
    targets.append(line.split("\t")[0])
aliases = read_lines(os.path.join(HERE,"aliases.txt"))
regexes = read_lines(os.path.join(HERE,"family_regex.txt"))
exact = sorted({n.lower() for n in targets + aliases})
print("targets=%d aliases=%d regexes=%d" % (len(targets), len(aliases), len(regexes)), flush=True)

SEL = """
PREFIX mb: <http://www.massbank.jp/ontology/>
PREFIX schema: <https://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?spectrum ?id ?title ?npeaks ?ion ?itype ?mstype ?ce ?acinst ?prec ?prectype ?splash
       ?formula ?mass ?ik ?name
WHERE {
  GRAPH <http://rdfportal.org/dataset/massbank> {
    ?c rdfs:label ?name ; schema:molecularFormula ?formula ; schema:inChIKey ?ik .
    %s
    ?spectrum a mb:MassSpectrum ; mb:compound ?c ;
              dcterms:identifier ?id ; skos:definition ?title .
    OPTIONAL { ?spectrum mb:pk_num_peak ?npeaks }
    OPTIONAL { ?spectrum mb:pk_splash ?splash }
    OPTIONAL { ?spectrum mb:analytical_methods_and_conditions ?ac .
      OPTIONAL { ?ac mb:ion_mode ?ion } OPTIONAL { ?ac mb:instrument_type ?itype }
      OPTIONAL { ?ac mb:ms_type ?mstype } OPTIONAL { ?ac mb:collision_energy ?ce }
      OPTIONAL { ?ac mb:ac_instrument ?acinst } }
    OPTIONAL { ?spectrum mb:mass_spectram_meta_data ?m .
      OPTIONAL { ?m mb:precursor_mz_value ?prec } OPTIONAL { ?m mb:precursor_type_value ?prectype } }
    ?c mb:ch_exact_mass ?mass .
  }
}"""

META=[]
if exact:
    q = SEL % ('FILTER(LCASE(STR(?name)) IN (%s))' % ", ".join('"%s"'%n for n in exact))
    print("query exact-name (%d) ..." % len(exact), flush=True); t=time.time()
    r=sparql(q); print("  rows:", len(r), "%.1fs"%(time.time()-t), flush=True)
    for x in r: x["match_source"]="exact-name"; META.append(x)
for rx in regexes:
    q = SEL % ('FILTER(REGEX(STR(?name), "%s", "i"))' % rx)
    print("query regex %s ..." % rx[:40], flush=True); t=time.time()
    r=sparql(q); print("  rows:", len(r), "%.1fs"%(time.time()-t), flush=True)
    for x in r: x["match_source"]="family-regex"; META.append(x)

seen=set(); U=[]
for r in META:
    k=(r["spectrum"], r["name"], r.get("ce",""), r.get("prec",""))
    if k in seen: continue
    seen.add(k); U.append(r)
print("merged spectra rows:", len(U), flush=True)

cols=["spectrum","id","title","npeaks","ion","itype","mstype","ce","acinst","prec","prectype",
      "splash","formula","mass","ik","name","match_source"]
with open(os.path.join(MB,"spectra_meta.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in U: w.writerow({c:r.get(c,"") for c in cols})

ids=[]; 
for r in U:
    if r["spectrum"] not in ids: ids.append(r["spectrum"])
print("fetching peaks for %d spectra ..."%len(ids), flush=True)
OUT=os.path.join(MB,"peaks.csv")
if os.path.exists(OUT): os.remove(OUT)
w=csv.writer(open(OUT,"w",newline="",encoding="utf-8")); w.writerow(["spectrum","mz","rel","intensity"])
CH=25; total=0
for i in range(0,len(ids),CH):
    v=" ".join("<%s>"%x for x in ids[i:i+CH])
    q="""PREFIX mb: <http://www.massbank.jp/ontology/>
SELECT ?spectrum ?mz ?rel ?intensity WHERE {
  VALUES ?spectrum { %s }
  GRAPH <http://rdfportal.org/dataset/massbank> {
    ?spectrum mb:has_peak ?p . ?p mb:mz ?mz ; mb:relative_intensity ?rel .
    OPTIONAL { ?p mb:intensity ?intensity } } }""" % v
    rows=None
    for a in (1,2,3):
        try: rows=sparql(q); break
        except Exception as e:
            print("  retry %d %s"%(a,e), flush=True); time.sleep(3)
    if not rows: continue
    for p in rows:
        w.writerow([p.get("spectrum",""),p.get("mz",""),p.get("rel",""),p.get("intensity","")])
    total+=len(rows)
    print("  chunk %d/%d (+%d)"%(i//CH+1,(len(ids)+CH-1)//CH,len(rows)), flush=True)
print("DONE spectra=%d peaks=%d"%(len(ids),total), flush=True)
