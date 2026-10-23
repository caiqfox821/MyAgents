#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 1b: 抓 MassBank 峰表（可断点续跑，逐块落盘）

性能提示：RDF Portal 的 SPARQL 端点返回 `text/csv` 比
`application/sparql-results+json` 快约 10 倍以上（同一查询 JSON 40 s / CSV 3 s），
故这里统一用 CSV 输出。
"""
import csv, io, json, os, urllib.request, urllib.parse, sys, time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MB   = os.path.join(BASE, "raw", "massbank")
EP   = os.environ.get("MB_SPARQL_EP", "https://rdfportal.org/primary/sparql")
OUT  = os.path.join(MB, "peaks.csv")

def sparql(q, timeout=240):
    """执行 SPARQL，返回 list[dict]；用 CSV 输出以大幅提速。"""
    d = urllib.parse.urlencode({"query": q}).encode()
    r = urllib.request.Request(EP, data=d, headers={
        "Accept": "text/csv",
        "Content-Type": "application/x-www-form-urlencoded"})
    raw = urllib.request.urlopen(r, timeout=timeout).read().decode("utf-8")
    rows = list(csv.reader(io.StringIO(raw)))
    if not rows:
        return []
    hdr = rows[0]
    return [dict(zip(hdr, row)) for row in rows[1:]]

ids = []
for r in csv.DictReader(open(os.path.join(MB, "spectra_meta.csv"), encoding="utf-8")):
    if r["spectrum"] not in ids: ids.append(r["spectrum"])

done = set()
if os.path.exists(OUT):
    for r in csv.DictReader(open(OUT, encoding="utf-8")): done.add(r["spectrum"])
todo = [i for i in ids if i not in done]
print("spectra total=%d  done=%d  todo=%d" % (len(ids), len(done), len(todo)), flush=True)

new = not os.path.exists(OUT)
f = open(OUT, "a", newline="", encoding="utf-8"); w = csv.writer(f)
if new: w.writerow(["spectrum", "mz", "rel", "intensity"])
CH = 25
for i in range(0, len(todo), CH):
    ch = todo[i:i+CH]
    v = " ".join("<%s>" % x for x in ch)
    q = """
PREFIX mb: <http://www.massbank.jp/ontology/>
SELECT ?spectrum ?mz ?rel ?intensity WHERE {
  VALUES ?spectrum { %s }
  GRAPH <http://rdfportal.org/dataset/massbank> {
    ?spectrum mb:has_peak ?p . ?p mb:mz ?mz ; mb:relative_intensity ?rel .
    OPTIONAL { ?p mb:intensity ?intensity }
  }
}""" % v
    rows = None
    for attempt in (1, 2, 3):
        try:
            rows = sparql(q); break
        except Exception as e:
            print("  retry %d (%s)" % (attempt, e), flush=True); time.sleep(3); rows = None
    if rows is None:
        print("  !! chunk %d failed permanently" % i, flush=True); continue
    for p in rows:
        w.writerow([p.get("spectrum", ""), p.get("mz", ""), p.get("rel", ""), p.get("intensity", "")])
    f.flush()
    print("  chunk %d/%d (+%d peaks)" % (i // CH + 1, (len(todo) + CH - 1) // CH, len(rows)), flush=True)
f.close()
print("DONE", flush=True)
