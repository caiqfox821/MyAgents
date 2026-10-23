#!/usr/bin/env python3
"""
WHO IRIS（DSpace 7）营养/膳食与慢病指南发现与 PDF 直链解析。
流程: discover/search -> item.uuid -> bundles(ORIGINAL) -> bitstreams -> *.pdf content URL
输出: sources_who.json（含 pdf_url，供 build_booklib.py 下载）
用法: python3 tools/discover_who.py [--check]
"""
import os, re, json, time, argparse, urllib.parse, urllib.request, concurrent.futures

BASE = "https://iris.who.int/server/api"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "sources_who.json")
HDRS = {"Accept": "application/json", "User-Agent": "nutrition-lib/1.0"}

# 主题检索词（营养干预/膳食与疾病，WHO 指南与报告）
QUERIES = [
    "guideline sugars intake adults children",
    "guideline sodium intake",
    "guideline potassium intake",
    "guideline saturated fatty acid trans-fatty acid intake",
    "guideline non-sugar sweeteners",
    "guideline iron supplementation women adolescent",
    "guideline vitamin A supplementation infants children",
    "guideline multiple micronutrient powders",
    "guideline wheat flour fortification vitamins minerals",
    "guideline maize flour corn meal fortification",
    "guideline use of lower-sodium salt substitutes",
    "guideline lipid-based nutrient supplements",
    "guideline zinc supplementation diarrhoea",
    "guideline calcium supplementation pregnancy",
    "guideline vitamin B12 folate",
    "recommendations antenatal care positive pregnancy experience",
    "guideline infant feeding low birth weight",
    "guideline complementary feeding breastfed children",
    "guideline obesity prevention children",
    "guideline physical activity sedentary behaviour",
    "global action plan prevention control noncommunicable diseases",
    "nutrition noncommunicable disease prevention diet",
    "healthy diet nutrition policy",
    "guideline healthy eating food environment fiscal policies",
    "guideline nutrition labelling front-of-pack",
    "guideline malnutrition severe acute",
    "guideline management moderate acute malnutrition",
    "guideline school health nutrition",
    "guideline maternal nutrition pregnancy",
    "repository nutrition older persons",
]

MUST = re.compile(r"guideline|recommendation|action plan|action package|action framework|"
                  r"\breport\b|technical note|training course|policy brief|"
                  r"\bframework\b|\bstrategy\b|\bmanual\b|evidence review|"
                  r"\bat a glance\b|summary|annex|fortification meeting|"
                  r"global report|nutrition profile|nutrient profile", re.I)
BAD = re.compile(r"influence on|textual analysis|commentary|erratum|corrigendum|"
                 r"backdrop|interview|"
                 # 期刊论文/单次研究标题特征
                 r"\bin healthy\b|\bserum\b|\btrial\b|\baudit\b|\bcase\b|"
                 r"level of trans-fatty acids in|ring trial|taxation in|"
                 r"content as a percentage|measuring trans-fatty", re.I)

TAG = [
    (r"sugar|sweetener|carbohydrate", "糖/碳水化合物"),
    (r"sodium|salt", "钠盐"),
    (r"potassium|calcium|magnesium", "矿物质"),
    (r"fat|fatty acid|trans", "脂肪"),
    (r"vitamin", "维生素"),
    (r"iron|zinc|micronutrient|folate|b12", "微量营养素补充"),
    (r"fortification", "食品强化"),
    (r"infant|breastfeed|complementary|low birth weight|child|childhood", "婴幼儿/儿童"),
    (r"maternal|antenatal|pregnan|women", "母婴"),
    (r"obesity|overweight|weight", "肥胖"),
    (r"malnutrition|acute malnutrition|wasting|stunting", "营养不良"),
    (r"physical activity|sedentary", "身体活动"),
    (r"noncommunicable|ncd|cardiovascular|diabetes|cancer", "慢病(NCD)"),
    (r"labelling|fiscal|food environment|policy|plan", "政策/环境"),
    (r"older|ageing|aging", "老年营养"),
]


def get(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def search(q, size=8):
    u = f"{BASE}/discover/search/objects?query={urllib.parse.quote(q)}&size={size}&dsoType=item"
    try:
        d = get(u)
        objs = d["_embedded"]["searchResult"]["_embedded"]["objects"]
    except Exception as e:
        print("  search fail", q, e)
        return []
    out = []
    for o in objs:
        io = o["_embedded"]["indexableObject"]
        out.append({"uuid": io["uuid"], "name": io.get("name", ""), "handle": io.get("handle")})
    return out


def resolve_pdf(uuid):
    """返回 (pdf_url, size) 或 (None, None)"""
    try:
        b = get(f"{BASE}/core/items/{uuid}/bundles")
        orig = next((x for x in b["_embedded"]["bundles"] if x["name"] == "ORIGINAL"), None)
        if not orig:
            return None, None
        bs = get(f"{BASE}/core/bundles/{orig['uuid']}/bitstreams")
        pdfs = [x for x in bs["_embedded"]["bitstreams"] if x["name"].lower().endswith(".pdf")]
        if not pdfs:
            return None, None
        # 优先英文版（-eng / _eng / eng.pdf）
        eng = [x for x in pdfs if re.search(r"[-_]eng(\.|$)|eng\.pdf$", x["name"], re.I)]
        pick = (eng or pdfs)[0]
        return pick["_links"]["content"]["href"], pick.get("sizeBytes")
    except Exception as e:
        return None, None


def tags_for(t):
    ts = [tag for pat, tag in TAG if re.search(pat, t, re.I)]
    return ts or ["营养综合"]


def slug(title):
    s = re.sub(r"[^A-Za-z0-9.]+", "_", title)
    return re.sub(r"_+", "_", s).strip("_")[:90]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    cand = {}
    for q in QUERIES:
        for it in search(q):
            if it["uuid"] not in cand:
                cand[it["uuid"]] = it
        print(f"  [{q}] 累计 {len(cand)}")
        time.sleep(0.4)

    print(f"\n候选 {len(cand)}，解析 PDF 直链...")
    entries = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        fs = {ex.submit(resolve_pdf, u): it for u, it in cand.items()}
        for f in concurrent.futures.as_completed(fs):
            it = fs[f]
            url, size = f.result()
            if not url:
                continue
            name = it["name"]
            if BAD.search(name):
                continue
            if not MUST.search(name):
                continue
            year = None
            m = re.search(r"\b(19|20)\d{2}\b", name)
            if m:
                year = int(m.group(0))
            entries.append({
                "uuid": it["uuid"], "title": name, "year": year,
                "file": f"{slug(name)}_{year}" if year else slug(name),
                "pdf_url": url, "size": size, "sub": "who", "publisher": "World Health Organization",
                "license": "CC BY-NC-SA 3.0 IGO（WHO 开放获取）",
                "source": f"https://iris.who.int/handle/{it['handle']}" if it.get("handle") else "",
                "tags": tags_for(name),
            })
    # 按标题去重（保留最短/最规范名）
    entries.sort(key=lambda e: (e["title"].lower(), len(e["title"])))
    seen, uniq = set(), []
    for e in entries:
        k = re.sub(r"[^a-z0-9]+", " ", e["title"].lower()).strip()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(e)
    uniq.sort(key=lambda e: (-(e["year"] or 0), e["title"]))
    json.dump(uniq, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nsources_who.json 写入 {len(uniq)} 篇")
    for e in uniq:
        print(f"  {e['year'] or '----'}  {e['title'][:78]}  {e['tags']}")


if __name__ == "__main__":
    main()
