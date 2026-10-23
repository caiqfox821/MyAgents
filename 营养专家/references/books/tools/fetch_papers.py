#!/usr/bin/env python3
"""
营养干预疾病 · 开放获取文献抓取（EuropePMC REST，配合 PAPERS MCP 检索结果）。
- 主题化检索：营养干预 × 20 类疾病/人群
- 仅取开放获取（OPEN_ACCESS:Y）
- 输出 papers/papers.json + papers/文献清单-营养.md
- 下载 OA 全文：papers/fulltext/<pmcid>.xml（JATS 全文 XML，EuropePMC REST）

用法: python3 tools/fetch_papers.py [--max 10] [--no-fulltext]
"""
import os, re, json, time, argparse, urllib.parse, urllib.request, concurrent.futures

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))         # books/
PAPERS = os.path.join(os.path.dirname(ROOT), "papers")                     # references/papers/
API = "https://www.ebi.ac.uk/europepmc/webservices/rest"
HDRS = {"User-Agent": "nutrition-lib/1.0"}

TOPICS = [
    ("T2D", "营养干预与2型糖尿病", "dietary intervention type 2 diabetes glycemic control"),
    ("CVD", "膳食模式与心血管疾病预防", "dietary pattern cardiovascular disease prevention randomized"),
    ("HTN", "减钠/DASH 与高血压", "dietary sodium reduction blood pressure DASH hypertension"),
    ("Obesity", "膳食干预与肥胖/体重管理", "diet intervention obesity weight loss randomized controlled trial"),
    ("Cancer", "肿瘤患者营养干预与生活质量", "nutrition intervention cancer patients quality of life"),
    ("CKD", "慢性肾脏病医学营养治疗", "medical nutrition therapy chronic kidney disease protein"),
    ("IBD", "炎症性肠病膳食治疗", "diet therapy inflammatory bowel disease Crohn ulcerative colitis"),
    ("Sarcopenia", "蛋白质补充与肌少症", "protein supplementation sarcopenia older adults muscle"),
    ("Malnutrition", "口服营养补充与院内营养不良", "oral nutritional supplements hospital malnutrition outcomes"),
    ("GDM", "妊娠期糖尿病膳食干预", "dietary intervention gestational diabetes maternal outcomes"),
    ("MASLD", "MASLD/NAFLD 膳食干预", "diet intervention metabolic dysfunction associated steatotic liver disease"),
    ("Lipids", "植物甾醇/膳食与血脂异常", "dietary plant sterols dyslipidemia LDL cholesterol"),
    ("Microbiome", "膳食干预与肠道菌群", "diet intervention gut microbiome randomized"),
    ("VitD", "维生素D 补充与疾病预防", "vitamin D supplementation disease prevention randomized"),
    ("Cachexia", "肿瘤恶病质营养干预", "nutrition intervention cancer cachexia"),
    ("MetSyn", "膳食干预与代谢综合征", "dietary intervention metabolic syndrome components"),
    ("IBS", "低FODMAP 膳食与肠易激综合征", "low FODMAP diet irritable bowel syndrome"),
    ("ICU", "重症患者营养支持", "nutrition support critically ill enteral parenteral"),
    ("PlantBased", "植物性膳食与心血管代谢风险", "plant-based diet cardiometabolic risk factors"),
    ("Mortality", "膳食模式与全因死亡", "dietary patterns all-cause mortality cohort"),
]


def get(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def search(q, maxn):
    u = (f"{API}/search?query={urllib.parse.quote(q + ' AND OPEN_ACCESS:Y')}"
         f"&format=json&pageSize={maxn}&resultType=core&sort=CITED%20desc")
    try:
        d = json.loads(get(u).decode("utf-8", "ignore"))
    except Exception as e:
        print("  search fail", q, e)
        return []
    return d.get("resultList", {}).get("result", [])


def clean(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--no-fulltext", action="store_true")
    a = ap.parse_args()
    os.makedirs(os.path.join(PAPERS, "fulltext"), exist_ok=True)

    allrec = {}
    for key, cn, q in TOPICS:
        rs = search(q, a.max)
        recs = []
        for r in rs:
            pmcid = r.get("pmcid")
            if not pmcid:
                continue
            rec = {
                "topic": key, "topic_cn": cn,
                "pmcid": pmcid, "pmid": r.get("pmid"), "doi": r.get("doi"),
                "title": clean(r.get("title")), "authors": clean(r.get("authorString")),
                "journal": (r.get("journalInfo", {}) or {}).get("journal", {}).get("title", ""),
                "year": (r.get("journalInfo", {}) or {}).get("yearOfPublication"),
                "volume": (r.get("journalInfo", {}) or {}).get("volume"),
                "pages": r.get("pageInfo"), "cited": r.get("citedByCount"),
                "oa": r.get("isOpenAccess"), "pdf": f"https://europepmc.org/articles/{pmcid}?pdf=render",
            }
            recs.append(rec)
            allrec[pmcid] = rec
        print(f"  [{key}] {len(recs)} 篇 · {cn}")
        time.sleep(0.5)

    recs = sorted(allrec.values(), key=lambda x: (x["topic"], -(x["cited"] or 0)))
    json.dump(recs, open(os.path.join(PAPERS, "papers.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\npapers.json 写入 {len(recs)} 篇")

    # 下载 OA 全文 XML
    if not a.no_fulltext:
        def fetch_xml(rec):
            dest = os.path.join(PAPERS, "fulltext", rec["pmcid"] + ".xml")
            if os.path.exists(dest) and os.path.getsize(dest) > 2000:
                return rec["pmcid"], "skip"
            try:
                data = get(f"{API}/{rec['pmcid']}/fullTextXML")
                if data[:5] == b"<?xml" and len(data) > 2000:
                    open(dest, "wb").write(data)
                    return rec["pmcid"], "ok"
            except Exception as e:
                return rec["pmcid"], f"fail {e}"
            return rec["pmcid"], "fail"
        ok = skip = fail = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            for cid, st in ex.map(fetch_xml, recs):
                ok += st == "ok"; skip += st == "skip"; fail += st.startswith("fail")
        print(f"全文 XML: ok={ok} skip={skip} fail={fail}")

    # 生成 markdown 清单
    from collections import defaultdict
    bt = defaultdict(list)
    for r in recs:
        bt[(r["topic"], r["topic_cn"])].append(r)
    L = ["# 营养干预疾病 · 开放获取文献清单（OA）\n",
         f"> 由 PAPERS MCP（EuropePMC）检索生成，共 **{len(recs)} 篇**开放获取文献；全文 XML 见 `papers/fulltext/`。",
         "> 检索式：`(<主题>) AND OPEN_ACCESS:Y`，按被引降序；为初始清单，需按需扩充与更新。\n"]
    for (k, cn) in sorted(bt, key=lambda x: x[0]):
        L.append(f"## {cn}（{k}）\n")
        L.append("| 文献 | 期刊/年 | 被引 | PMCID | DOI |")
        L.append("|---|---|---|---|---|")
        for r in bt[(k, cn)]:
            au = (r["authors"].split(";")[0] if r["authors"] else "")
            L.append(f"| {r['title'][:120]}{' — ' + au if au else ''} | {r['journal'][:40]} {r['year'] or ''} | "
                     f"{r['cited'] or 0} | [{r['pmcid']}]({r['pdf']}) | {r['doi'] or '-'} |")
        L.append("")
    L.append("---\n*由营养专家维护；扩充后运行 `python3 tools/fetch_papers.py` 重建。*")
    open(os.path.join(PAPERS, "文献清单-营养.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("文献清单-营养.md 已生成")


if __name__ == "__main__":
    main()
