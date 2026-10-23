#!/usr/bin/env python3
"""
MDPI Books 书目发现（营养/膳食/慢病营养方向）。
- 数据源: Crossref REST API（prefix=10.3390, type=book）
- 由 resource.primary.URL（https://www.mdpi.com/books/reprint/<id>）取出 reprint id，
  即 mdpi-res.com/bookfiles/book/<id>/<slug>.pdf 的 id。
- 输出: sources_mdpi.json
用法: python3 tools/discover_mdpi.py
"""
import os, re, json, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "sources_mdpi.json")

QUERIES = [
    "nutrition", "diet nutrition", "human nutrition", "clinical nutrition",
    "dietary pattern", "micronutrient", "vitamin", "mineral nutrition",
    "obesity nutrition", "diabetes nutrition", "metabolic syndrome diet",
    "nutritional epidemiology", "public health nutrition", "sports nutrition",
    "nutritional status", "diet disease", "nutrition intervention",
    "dietary supplement", "functional food health", "nutrition aging",
]

# 主题标签推断（关键词 -> 标签）
TAGRULES = [
    (("obes", ), "肥胖"),
    (("diabet", "glyc"), "糖尿病"),
    (("metabolic", "cardiovascular", "hypertension", "lipid", "cholesterol"), "代谢与心血管"),
    (("cancer", "oncolog"), "肿瘤营养"),
    (("micronutrient", "vitamin", "mineral", "iron", "iodine", "zinc", "folate", "calcium"), "微量营养素"),
    (("diet", "dietary", "food pattern", "mediterranean", "vegetarian"), "膳食模式"),
    (("sport", "exercise", "athlet", "muscle", "sarcopenia"), "运动与肌少症"),
    (("pregnan", "infant", "child", "pediatric", "maternal", "lactation"), "母婴与儿童"),
    (("aging", "elder", "older", "geriatric"), "老年营养"),
    (("gut", "microbiom", "probiotic", "prebiotic", "gastro"), "肠道与菌群"),
    (("supplement", "nutraceutical", "functional food", "bioactive"), "补剂与功能成分"),
    (("epidemiolog", "public health", "population", "survey"), "营养流行病与公共卫生"),
    (("immun", "inflamm"), "免疫与炎症"),
    (("bone", "osteopor"), "骨骼营养"),
    (("renal", "kidney"), "肾脏营养"),
    (("enteral", "parenteral", "malnutri"), "临床营养支持"),
    (("label", "claim", "fortif"), "标签与强化"),
]


def tags_for(title):
    t = title.lower()
    tags = []
    for keys, tag in TAGRULES:
        if any(k in t for k in keys):
            tags.append(tag)
    return tags or ["营养综合"]


def slug(title):
    s = re.sub(r"[^A-Za-z0-9.]+", "_", title)
    return re.sub(r"_+", "_", s).strip("_")


def crossref(query, rows=100):
    url = ("https://api.crossref.org/works?filter=type:book,prefix:10.3390"
           "&rows=%d&select=DOI,title,ISBN,published,resource&query.bibliographic=%s"
           % (rows, urllib.parse.quote(query)))
    req = urllib.request.Request(url, headers={"User-Agent": "nutrition-lib/1.0 (mailto:lib@example.org)"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)["message"]["items"]


def main():
    seen = {}
    for q in QUERIES:
        try:
            items = crossref(q)
        except Exception as e:
            print("query fail", q, e)
            continue
        for it in items:
            doi = it.get("DOI")
            res = (it.get("resource", {}) or {}).get("primary", {}) or {}
            m = re.search(r"/books/reprint/(\d+)", res.get("URL", "") or "")
            if not m or doi in seen:
                continue
            title = (it.get("title") or ["?"])[0].strip()
            year = (it.get("published", {}).get("date-parts", [[None]])[0] or [None])[0]
            bid = m.group(1)
            seen[doi] = {
                "id": bid,
                "url_title": slug(title),
                "file": f"{slug(title)}_{year}" if year else slug(title),
                "year": year,
                "doi": doi,
                "pdf_isbn": next((i for i in it.get("ISBN", []) if i.startswith("9783")), None),
                "tags": tags_for(title),
                "title": title,
            }
        print(f"  [{q}] 累计 {len(seen)}")
        time.sleep(1.0)
    entries = sorted(seen.values(), key=lambda e: -(e.get("year") or 0))
    json.dump(entries, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nsources_mdpi.json 写入 {len(entries)} 册")
    for e in entries:
        print(f"  {e['id']:>6}  {e['year']}  {e['title'][:70]}  [{','.join(e['tags'])}]")


if __name__ == "__main__":
    main()
