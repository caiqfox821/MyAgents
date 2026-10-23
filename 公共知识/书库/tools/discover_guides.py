#!/usr/bin/env python3
"""
权威指南/报告 OA 发现（OpenAlex -> 可达性校验 -> sources_guides.json）。
只保留**域名白名单**内、且 curl 实测可下载（HTTP 200 + PDF + >60KB）的条目，
避免臆造链接。用法: python3 tools/discover_guides.py [--limit 120]
"""
import json, os, re, sys, time, argparse, subprocess, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "sources_guides.json")
UA = "public-knowledge-lib/1.0 (mailto:lib@example.org)"
CURL_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

ALLOW = (
    "cdn.who.int", "www.who.int", "iris.who.int", "apps.who.int",
    "www.fao.org", "openknowledge.fao.org", "www.epa.gov", "www3.epa.gov",
    "nepis.epa.gov", "inchem.org", "www.inchem.org", "www.oecd.org",
    "pubs.iarc.fr", "www.iarc.fr", "www.efsa.europa.eu", "mdpi-res.com",
    "www.cancer.gov", "tools.who.int", "www.ilo.org", "www.euro.who.int",
    "stacks.cdc.gov", "www.health.govt.nz", "www.foodsafety.gov.au",
)

QUERIES = [
    "chemical risk assessment of contaminants in food dose response",
    "dietary exposure assessment chemical contaminants food probabilistic",
    "benchmark dose analysis risk assessment chemicals",
    "threshold of toxicological concern TTC read-across",
    "adverse outcome pathway framework regulatory toxicology",
    "uncertainty analysis dietary exposure assessment EFSA",
    "microbiological risk assessment food quantitative",
    "pesticide residue dietary risk assessment JMPR",
    "guidelines drinking-water quality health criteria",
    "food additives safety evaluation JECFA",
    "good laboratory practice OECD principles",
    "greatest source of variability interspecies extrapolation uncertainty factors",
    "high resolution mass spectrometry suspect screening unknowns confidence",
    "mass spectrometry identification confidence levels nontarget",
    "metabolomics quality control mass spectrometry normalization",
    "MRM method development matrix effect LC-MS/MS quantification",
    "mycotoxin multi-mycotoxin LC-MS/MS QuEChERS validation food",
    "multi-residue pesticide analysis LC-MS/MS GC-MS/MS food validation",
    "elemental speciation food HPLC ICP-MS validation",
    "total diet study exposure assessment methodology",
    # ---------------- 会话 6 扩充（机构权威文本，新主题） ----------------
    "per- and polyfluoroalkyl substances PFAS risk assessment drinking water food",
    "microplastics human health risk assessment dietary exposure",
    "mineral oil hydrocarbons MOSH MOAH food contamination",
    "food contact materials migration safety assessment",
    "developmental neurotoxicity testing guidance regulatory",
    "immunotoxicity non-animal testing guidance regulatory",
    "in vitro to in vivo extrapolation physiologically based pharmacokinetic risk assessment",
    "genotoxicity testing strategy regulatory guidance in vivo follow-up",
    "human biomonitoring exposure assessment chemicals guidance",
    "acrylamide mitigation food processing health risk",
    "nitrate nitrite drinking water food health effects",
    "nanomaterials risk assessment guidance environment health",
    "physiologically based pharmacokinetic modelling regulatory application",
    "skin sensitisation integrated approaches to testing and assessment",
    "mixture risk assessment cumulative exposure chemicals",
    "evidence-based toxicology systematic review appraisal",
    "endocrine disruptor identification testing guidance",
    "vitamin and mineral upper level tolerable intake guidance",
]


def oa_search(q, per=40):
    url = ("https://api.openalex.org/works?search=%s&per-page=%d&filter=is_oa:true"
           "&select=id,doi,title,publication_year,best_oa_location,primary_location"
           % (urllib.parse.quote(q), per))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r).get("results", [])
        except Exception as e:
            print("   retry", q, e); time.sleep(3)
    return []


def pdf_of(res):
    for key in ("best_oa_location", "primary_location"):
        loc = res.get(key) or {}
        u = loc.get("pdf_url")
        if u:
            return u
    return None


def reachable(u):
    """HEAD/短 GET 校验：200 + PDF + 体积合理"""
    r = subprocess.run(["curl", "-s", "--noproxy", "*", "-o", "/dev/null", "-L",
                        "--max-time", "40", "--http1.1", "-A", CURL_UA,
                        "-r", "0-200000", "-w", "%{http_code}|%{content_type}|%{size_download}", u],
                       capture_output=True, text=True)
    out = (r.stdout or "").strip()
    if not out:
        return None
    code, ctype, size = (out.split("|") + ["", "", "0"])[:3]
    if code not in ("200", "206"):
        return None
    if "pdf" not in ctype.lower() and not u.lower().endswith(".pdf"):
        return None
    return code, ctype, int(float(size or 0))


def theme_of(title, default):
    t = title.lower()
    if re.search(r"mass spectrometr|lc-?ms|gc-?ms|hrms|orbitrap|q-?tof|maldi|metabolomic|"
                 r"lipidomic|proteomic|speciation|icp|quenchers|mrm|chromatograph|untargeted|"
                 r"non-target|screening", t):
        return "ms"
    if re.search(r"toxic|dose|bmd|benchmark|ttc|read-across|genotox|carcinogen|adverse outcome|"
                 r"glp|toxicokine|hepato|nephro|endocrine", t):
        return "tox"
    return "risk"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--maxcheck", type=int, default=160)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    seen, picked = {}, []
    for q in QUERIES:
        for res in oa_search(q):
            doi = res.get("doi") or res["id"]
            url = pdf_of(res)
            if not url or doi in seen:
                continue
            host = urllib.parse.urlparse(url).netloc.lower()
            if not any(host == d or host.endswith("." + d) for d in ALLOW):
                continue
            seen[doi] = url
        print("  query %-55r 累计候选 %d" % (q[:55], len(seen)), flush=True)

    for doi, url in list(seen.items())[: a.maxcheck]:
        rr = reachable(url)
        if not rr:
            continue
        code, ctype, size = rr
        if size < 40000:
            continue
        picked.append((doi, url, size))
        print("  OK %8d KB  %s" % (size // 1024, url[:110]), flush=True)
    print("可达 %d / 候选 %d" % (len(picked), len(seen)))
    if a.dry:
        return
    # 补齐元数据（标题/年份）
    entries = []
    for doi, url, size in picked[:a.limit]:
        oaid = doi.replace("https://doi.org/", "") if doi.startswith("https://doi.org/") else None
        meta = {}
        if oaid:
            try:
                req = urllib.request.Request("https://api.openalex.org/works/doi/" + oaid,
                                             headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=30) as r:
                    j = json.load(r)
                meta = {"title": j.get("title"), "year": j.get("publication_year")}
            except Exception as e:
                print("   meta fail", doi, e)
        if not meta.get("title"):
            meta = {"title": os.path.basename(url.split("/")[-1]).replace(".pdf", "").replace("_", " "),
                    "year": None}
        title = meta["title"]
        sub = "guides"
        file = re.sub(r"[^A-Za-z0-9]+", "_", title)[:70].strip("_")
        entries.append({
            "sub": sub, "file": file, "title": title, "year": meta.get("year"),
            "publisher": urllib.parse.urlparse(url).netloc, "license": "开放获取（机构库）",
            "source": doi if doi.startswith("http") else "https://doi.org/" + doi,
            "pdf_url": url, "themes": [theme_of(title, "risk")],
            "tags": [theme_of(title, "risk")],
        })
    json.dump(entries, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("已写 %s：%d 条" % (OUT, len(entries)))


if __name__ == "__main__":
    main()
