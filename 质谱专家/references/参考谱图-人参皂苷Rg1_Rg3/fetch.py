# -*- coding: utf-8 -*-
import json, urllib.request, urllib.parse, csv, os, sys

ENDPOINT = "https://rdfportal.org/primary/sparql"

def sparql(q):
    data = urllib.parse.urlencode({"query": q}).encode()
    req = urllib.request.Request(ENDPOINT, data=data,
        headers={"Accept":"application/sparql-results+json",
                 "Content-Type":"application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

def rows(res):
    out=[]
    for b in res["results"]["bindings"]:
        out.append({k:v["value"] for k,v in b.items()})
    return out

SPECS = [
 ("Rg1","MSBNK-RIKEN-PR307813","NEGATIVE","[M+HCOO]-","LC-ESI-QTOF","MS2","6V"),
 ("Rg1","MSBNK-Univ_Toyama-TY000193","NEGATIVE","[M+CH3COOH-H]-","LC-ESI-ITTOF","MS2",""),
 ("Rg1","MSBNK-Univ_Toyama-TY000020","NEGATIVE","[M+CH3COOH-H]-","LC-ESI-ITTOF","MS",""),
 ("Rg1","MSBNK-Univ_Toyama-TY000031","POSITIVE","[M+Na]+","LC-ESI-ITTOF","MS",""),
 ("Rg3(S)","MSBNK-RIKEN-PR308546","NEGATIVE","[M-H]-","LC-ESI-QTOF","MS2","6V"),
 ("Rg3(S)","MSBNK-RIKEN-PR308678","NEGATIVE","[M+HCOO]-","LC-ESI-QTOF","MS2","6V"),
 ("Rg3(R)","MSBNK-RIKEN-PR308649","NEGATIVE","[M-H]-","LC-ESI-QTOF","MS2","6V"),
 ("Rg3(R)","MSBNK-RIKEN-PR308618","NEGATIVE","[M+HCOO]-","LC-ESI-QTOF","MS2","6V"),
]

vals = " ".join("<https://identifiers.org/massbank/%s>"%s[1] for s in SPECS)
qpeak = """
PREFIX mb: <http://www.massbank.jp/ontology/>
SELECT ?spectrum ?mz ?rel ?intensity WHERE {
  VALUES ?spectrum { %s }
  GRAPH <http://rdfportal.org/dataset/massbank> {
    ?spectrum mb:has_peak ?peak .
    ?peak mb:mz ?mz ; mb:relative_intensity ?rel . OPTIONAL{?peak mb:intensity ?intensity}
  }
}""" % vals
res = sparql(qpeak)
peaks = rows(res)
print("peaks fetched:", len(peaks))

# group
from collections import defaultdict
g = defaultdict(list)
for p in peaks:
    rid = p["spectrum"].rsplit("/",1)[-1]
    g[rid].append((float(p["mz"]), int(p["rel"]), float(p.get("intensity",0) or 0)))

with open("peaks_all.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["record","compound","ion_mode","adduct","ms_level","mz","relative_intensity","intensity"])
    for comp,rid,ion,add,inst,ms,ce in SPECS:
        for mz,rel,inten in sorted(g.get(rid,[]), key=lambda x:-x[1]):
            w.writerow([rid,comp,ion,add,ms,"%.4f"%mz,rel,"%.6g"%inten])

# structure info
qcmp = """
PREFIX mb: <http://www.massbank.jp/ontology/>
PREFIX schema: <https://schema.org/>
SELECT DISTINCT ?formula ?mass ?smiles ?ik WHERE {
  VALUES ?ik { <http://identifiers.org/inchikey/YURJSTAIMNSZAE-HHNZYBFYSA-N>
               <http://identifiers.org/inchikey/RWXIFXNRCLMQCD-JBVRGBGGSA-N> }
  GRAPH <http://rdfportal.org/dataset/massbank> {
    ?c schema:inChIKey ?ik ; schema:molecularFormula ?formula ; mb:ch_exact_mass ?mass .
    OPTIONAL { ?c schema:smiles ?smiles }
  }
}"""
print(json.dumps(rows(sparql(qcmp)), ensure_ascii=False, indent=1))
