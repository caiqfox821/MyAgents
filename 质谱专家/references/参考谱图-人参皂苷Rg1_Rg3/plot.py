# -*- coding: utf-8 -*-
import csv, json, urllib.request, urllib.parse
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ENDPOINT="https://rdfportal.org/primary/sparql"
def sparql(q):
    d=urllib.parse.urlencode({"query":q}).encode()
    r=urllib.request.Request(ENDPOINT,data=d,headers={"Accept":"application/sparql-results+json"})
    return json.loads(urllib.request.urlopen(r,timeout=120).read().decode())
def rowsof(res): return [{k:v["value"] for k,v in b.items()} for b in res["results"]["bindings"]]

# Rg3 structure (MassBank stores the stereo-agnostic skeleton key)
q="""
PREFIX mb: <http://www.massbank.jp/ontology/>
PREFIX schema: <https://schema.org/>
SELECT DISTINCT ?formula ?mass ?ik WHERE {
  VALUES ?ik { <http://identifiers.org/inchikey/RWXIFXNRCLMQCD-UHFFFAOYSA-N> }
  GRAPH <http://rdfportal.org/dataset/massbank> {
    ?c schema:inChIKey ?ik ; schema:molecularFormula ?formula ; mb:ch_exact_mass ?mass .
  }
}"""
print("Rg3 structure:", json.dumps(rowsof(sparql(q))))

SPECS=[
 ("Rg1","MSBNK-RIKEN-PR307813","[M+HCOO]-  (NEG, MS2, LC-ESI-QTOF, CE 6V)"),
 ("Rg1","MSBNK-Univ_Toyama-TY000193","[M+CH3COOH-H]-  (NEG, MS2, LC-ESI-ITTOF)"),
 ("Rg1","MSBNK-Univ_Toyama-TY000020","[M+CH3COOH-H]-  (NEG, MS1, LC-ESI-ITTOF)"),
 ("Rg1","MSBNK-Univ_Toyama-TY000031","[M+Na]+  (POS, MS1, LC-ESI-ITTOF)"),
 ("Rg3(S)","MSBNK-RIKEN-PR308546","[M-H]-  (NEG, MS2, LC-ESI-QTOF, CE 6V)"),
 ("Rg3(S)","MSBNK-RIKEN-PR308678","[M+HCOO]-  (NEG, MS2, LC-ESI-QTOF, CE 6V)"),
 ("Rg3(R)","MSBNK-RIKEN-PR308649","[M-H]-  (NEG, MS2, LC-ESI-QTOF, CE 6V)"),
 ("Rg3(R)","MSBNK-RIKEN-PR308618","[M+HCOO]-  (NEG, MS2, LC-ESI-QTOF, CE 6V)"),
]

g=defaultdict(list)
with open("peaks_all.csv",encoding="utf-8") as f:
    for r in csv.DictReader(f):
        g[r["record"]].append((float(r["mz"]), int(r["relative_intensity"])))

def draw(specs, fname, title):
    n=len(specs)
    fig,axes=plt.subplots(n,1,figsize=(9.5,2.0*n),sharex=True)
    if n==1: axes=[axes]
    for ax,(comp,rid,lab) in zip(axes,specs):
        pk=sorted(g[rid])
        mz=[p[0] for p in pk]; rel=[p[1]/999*100 for p in pk]
        ax.vlines(mz,0,rel,linewidth=0.9,color="#1f5fa8")
        ax.set_ylim(-4,120); ax.set_yticks([0,50,100])
        ax.set_ylabel("Rel. int.\n(%)",fontsize=8)
        ax.text(0.995,0.93,f"{rid}   {lab}",transform=ax.transAxes,ha="right",va="top",fontsize=8)
        ax.tick_params(labelsize=8)
        ax.grid(axis="x",ls=":",lw=0.4,alpha=0.5)
    axes[-1].set_xlabel("m/z",fontsize=9)
    fig.suptitle(title,fontsize=11,y=0.995)
    fig.tight_layout(rect=[0,0,1,0.985])
    fig.savefig(fname,dpi=150); plt.close(fig)
    print("wrote",fname)

draw(SPECS[:4],"Rg1_mass_spectra.png","Ginsenoside Rg1 - MassBank reference spectra (4 records)")
draw(SPECS[4:],"Rg3_mass_spectra.png","Ginsenoside Rg3 - MassBank reference spectra (4 records)")

# print top fragments for the 4 MS2 spectra, for the writeup
for comp,rid,lab in [SPECS[0],SPECS[1],SPECS[4],SPECS[5],SPECS[6],SPECS[7]]:
    top=sorted(g[rid],key=lambda x:-x[1])[:8]
    print(rid, "|", comp, "|", "; ".join("%.3f(%d)"%(m,r) for m,r in top))
