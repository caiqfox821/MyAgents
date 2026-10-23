#!/usr/bin/env python3
"""
EuropePMC REST 开放获取文献抓取（风险评估 / 毒理 / 质谱 三线）。
- 检索: .../webservices/rest/search?query=<>&format=json&resultType=core （限 OPEN_ACCESS:Y）
- 全文: .../webservices/rest/<PMCID>/fullTextXML -> papers/xml/，并去标签存 papers/txt/
- 索引: papers/index.json + papers/INDEX.md（DOI/PMCID 级引用，L3 条目据此写"§/段落"出处）
用法: python3 tools/fetch_papers.py [--per-theme 16] [--theme tox]
"""
import os, re, sys, json, time, argparse, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDIR = os.path.join(ROOT, "papers")
API = "https://www.ebi.ac.uk/europepmc/webservices/rest"
UA = "public-knowledge-lib/1.0 (mailto:lib@example.org)"

QUERIES = {
    "risk": [
        "EFSA guidance uncertainty analysis dietary exposure",
        "probabilistic dietary exposure assessment Monte Carlo chemicals",
        "pesticide residues dietary risk assessment children",
        "total diet study chemical exposure assessment",
        "margin of exposure genotoxic carcinogens risk assessment",
        "cumulative risk assessment pesticide residues mixture",
        "risk assessment contaminants food review methodology",
        "microbiological risk assessment quantitative food review",
        "human biomonitoring internal dose exposure assessment",
        "food additives safety evaluation JECFA approach",
    ],
    "tox": [
        "benchmark dose modelling BMD comparison risk assessment",
        "threshold of toxicological concern TTC regulatory",
        "read-across accuracy case studies regulatory toxicology",
        "adverse outcome pathway regulatory acceptance",
        "uncertainty factors interspecies intraspecies extrapolation",
        "chemical specific adjustment factors CSAF human variability",
        "new approach methods regulatory acceptance toxicology",
        "transcriptomic point of departure benchmark dose",
        "mode of action genotoxic carcinogen threshold of dose response",
        "NOAEL limitations benchmark dose regulatory",
        "physiologically based pharmacokinetic modelling chemical risk assessment",
        "repeated dose toxicity study design derivation reference dose",
    ],
    "ms": [
        "confidence levels identification non-target screening mass spectrometry",
        "suspect screening high resolution mass spectrometry food",
        "metabolomics quality control normalisation data processing",
        "matrix effect quantification liquid chromatography mass spectrometry",
        "isotope dilution mass spectrometry reference method accuracy",
        "multi-mycotoxin LC-MS/MS validation food",
        "pesticide residues QuEChERS LC-MS/MS GC-MS/MS validation food",
        "effect-directed analysis unknown identification mass spectrometry",
        "shotgun lipidomics identification confidence",
        "data-independent acquisition proteomics quantification",
        "MALDI mass spectrometry imaging quantification validation",
        "speciation ICP-MS hyphenated techniques arsenic food",
    ],
}
TAGRULES = {
    "risk": [
        (("exposure", "intake", "dietary"), "暴露评估"),
        (("pesticide", "residue"), "农药残留"),
        (("mycotoxin", "aflatoxin"), "真菌毒素"),
        (("microbiolog", "salmonella", "listeria", "haccp"), "微生物危害"),
        (("uncertainty", "probabilistic", "monte carlo"), "不确定性与概率"),
        (("risk assess", "risk analysis", "hazard"), "风险评估"),
        (("additive", "contaminant"), "添加剂与污染物"),
    ],
    "tox": [
        (("benchmark dose", "bmd", "noael", "point of departure"), "剂量-反应"),
        (("ttc", "threshold of toxicological"), "TTC"),
        (("read-across", "qsar", "in silico", "cross-reference"), "计算毒理"),
        (("adverse outcome", "mode of action", "mechanis"), "毒作用机制/AOP"),
        (("uncertainty factor", "adjustment factor", "csaf", "interspecies"), "不确定系数"),
        (("new approach", "in vitro", "organoid", "NAM", "alternative"), "替代方法/NAMs"),
        (("genotox", "carcinogen", "mutagen"), "遗传毒性与致癌"),
        (("pbpk", "pharmacokinet", "adme"), "毒代动力学"),
        (("review", "regulatory"), "法规与指南"),
    ],
    "ms": [
        (("non-target", "untargeted", "unknown", "confidence level"), "非靶向筛查与鉴定"),
        (("suspect screening", "hrms", "orbitrap", "q-tof", "high-resolution"), "高分辨质谱"),
        (("mycotoxin",), "毒素分析"),
        (("pesticide", "quenchers"), "农残分析"),
        (("metabolom",), "代谢组学"),
        (("lipidom",), "脂质组学"),
        (("proteom",), "蛋白质组学"),
        (("matrix effect", "isotope dilution", "validation", "quantif"), "定量与验证"),
        (("maldi", "imaging"), "质谱成像"),
        (("speciation", "icp"), "元素形态分析"),
        (("quality control", "normali", "reproducib"), "质谱质控"),
    ],
}


QUERIES["guides"] = [
    'TITLE:"Guidance on Uncertainty Analysis"',
    'TITLE:"read-across approach" AND JOURNAL:"EFSA journal"',
    'TITLE:"State of the Art of Toxicological Risk Assessment"',
    'TITLE:"threshold of toxicological concern" AND (JOURNAL:"EFSA journal" OR TOPICS:"toxicology")',
    'TITLE:"Dose–Response Assessment and Health-based Guidance Values"',
    'TITLE:"Guideline on the Health Risk Assessment of Exposure to Pesticide Residues"',
    'TITLE:"Benchmark Dose Software" OR TITLE:"benchmark dose technical guidance"',
    'TITLE:"Chemical-Specific Adjustment Factors"',
    'TITLE:"Conceptual Framework for Evaluating a Mode of Action"',
    'TITLE:"adverse outcome pathway" AND (TOPICS:"risk assessment")',
    'TITLE:"new approach methodologies" AND (TOPICS:"regulatory")',
    'TITLE:"probabilistic" AND TITLE:"dietary exposure" AND (JOURNAL:"EFSA journal")',
    'TITLE:"Communication of chemical risk assessment"',
    'TITLE:"dietary exposure assessment" AND TITLE:"guidance"',
    'TITLE:"total diet study" AND TOPICS:"exposure"',
    'TITLE:"acute reference dose" AND TITLE:"probabilistic"',
    'TITLE:"confirmation of metabolites" OR TITLE:"mass spectrometry" AND TITLE:"guideline"',
    'TITLE:"analytical quality control" AND TITLE:"mass spectrometry"',
    'TITLE:"identification confidence" AND TITLE:"mass spectrometry"',
    'TITLE:"residue definition" AND TITLE:"enforcement" AND TITLE:"risk assessment"',
]
TAGRULES["guides"] = TAGRULES["tox"] + TAGRULES["risk"] + TAGRULES["ms"]


QUERIES["guides"] += [
    'TITLE:"Ten years of Nontargeted" OR TITLE:"nontargeted identification" AND TITLE:"confidence levels"',
    'TITLE:"read-across" AND TITLE:"guidance" AND JOURNAL:"EFSA journal"',
    'TITLE:"Guidance on the use of the read-across approach"',
    'TITLE:"threshold of toxicological concern" AND JOURNAL:"EFSA journal"',
    'TITLE:"Problems and pitfalls in benchmark dose" OR TITLE:"benchmark dose" AND JOURNAL:"EFSA journal"',
    'TITLE:"Good Laboratory Practice" AND TITLE:"principles"',
    'TITLE:"adverse outcome pathway" AND TITLE:"developing and using"',
    'TITLE:"communication of uncertainty" AND TITLE:"guidance"',
    'TITLE:"Metabolomics Standards Initiative" OR TITLE:"minimum reporting standards" AND TITLE:"mass spectrometry"',
    'TITLE:"GPA rule set" OR TITLE:"good practice for mass spectrometry" OR TITLE:"sum of errors"',
    'TITLE:"confidence levels" AND TITLE:"high-resolution mass spectrometry"',
    'TITLE:"matrix effects" AND TITLE:"recommendations" AND TITLE:"mass spectrometry"',
    'TITLE:"suspect screening" AND TITLE:"guidance" AND TITLE:"high-resolution"',
    'TITLE:"food consumption" AND TITLE:"guidance" AND TITLE:"exposure assessment"',
    'TITLE:"probable daily intake" AND TITLE:"pesticide" AND TITLE:"guidance"',
    'TITLE:"toxicological relevance" AND TITLE:"enzyme induction"',
    'TITLE:"in vitro to in vivo extrapolation" AND TITLE:"regulatory"',
    'TITLE:"weight of evidence" AND JOURNAL:"EFSA journal" AND TITLE:"guidance"',
    'TITLE:"relatively simple and conservative methods" AND TITLE:"uncertainty"',
    'TITLE:"unacceptable variability" AND TITLE:"read-across"',
]

# ---------------------------------------------------------------- 会话 6 扩充检索式（新一轮新入库）
QUERIES["risk"] += [
    "PFAS per- and polyfluoroalkyl substances dietary exposure risk assessment",
    "microplastics dietary exposure human health risk",
    "mineral oil hydrocarbons MOSH MOAH food risk",
    "food contact materials migration risk assessment",
    "nitrate nitrite food exposure health risk",
    "acrylamide dietary exposure risk characterisation",
    "human biomonitoring HBM4EU internal exposure chemicals",
    "risk-benefit assessment food chemicals",
    "perchlorate exposure food risk assessment",
    "aluminium dietary exposure risk assessment",
    "methylmercury fish consumption risk assessment",
    "cadmium dietary exposure risk assessment",
]
QUERIES["tox"] += [
    "PFAS toxicokinetics half-life human biomonitoring",
    "developmental neurotoxicity in vitro test battery DNT",
    "skin sensitisation integrated testing strategy alternatives",
    "genotoxicity in vivo follow-up testing strategy aneugen",
    "immunotoxicity testing regulatory non-animal",
    "nanoplastics toxicity human health",
    "endocrine disrupting chemicals low dose effects",
    "toxicogenomics transcriptomics regulatory toxicology",
    "in vitro to in vivo extrapolation IVIVE quantitative",
    "botanical safety assessment toxicology constituent",
    "mixture toxicity cumulative assessment group component",
    "carcinogenicity classification IARC monograph evaluation",
]
QUERIES["ms"] += [
    "PFAS determination LC-MS/MS food water",
    "microplastics identification pyrolysis GC-MS Raman",
    "mineral oil hydrocarbons GCxGC determination food",
    "pesticide metabolites identification LC-HRMS",
    "ion mobility spectrometry metabolomics collision cross section",
    "data independent acquisition proteomics quantification",
    "single cell proteomics mass spectrometry",
    "metabolomics reporting standards reproducibility",
    "trace element speciation HPLC ICP-MS food",
    "food authentication stable isotope ratio mass spectrometry",
    "glyphosate AMPA determination LC-MS/MS",
    "mycotoxin biomarkers urine LC-MS/MS exposure",
]
QUERIES["guides"] += [
    'TITLE:"per- and polyfluoroalkyl substances" AND TITLE:"risk assessment"',
    'TITLE:"microplastics" AND TITLE:"risk assessment"',
    'TITLE:"mineral oil hydrocarbons" AND TITLE:"food"',
    'TITLE:"food contact materials" AND TITLE:"risk assessment"',
    'TITLE:"genotoxicity" AND TITLE:"testing strategy" AND JOURNAL:"EFSA journal"',
    'TITLE:"developmental neurotoxicity" AND TITLE:"guidance"',
    'TITLE:"skin sensitisation" AND TITLE:"guidance"',
    'TITLE:"harmonised" AND TITLE:"human health risk assessment"',
    'TITLE:"risk-benefit" AND TITLE:"food"',
    'TITLE:"nanomaterials" AND TITLE:"risk assessment" AND TITLE:"guidance"',
    'TITLE:"nitrate" AND TITLE:"nitrite" AND TITLE:"food"',
    'TITLE:"perchlorate" AND TITLE:"food"',
]

def get(url, tries=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=50) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                print("   fail", url[:80], e)
                return None
            time.sleep(2 + 2 * i)


def search(q, size=25):
    url = ("%s/search?query=%s%%20AND%%20OPEN_ACCESS:Y&pageSize=%d&resultType=core&format=json"
           % (API, urllib.parse.quote(q), size))
    b = get(url)
    if not b:
        return []
    return json.loads(b).get("resultList", {}).get("result", []) or []


def tags_for(title, theme):
    t = (title or "").lower()
    out = [tag for keys, tag in TAGRULES[theme] if any(k.lower() in t for k in keys)]
    return out or [theme]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-theme", type=int, default=16)
    ap.add_argument("--theme", nargs="*", default=list(QUERIES))
    a = ap.parse_args()
    os.makedirs(os.path.join(PDIR, "xml"), exist_ok=True)
    os.makedirs(os.path.join(PDIR, "txt"), exist_ok=True)
    idx_path = os.path.join(PDIR, "index.json")
    index = json.load(open(idx_path, encoding="utf-8")) if os.path.exists(idx_path) else []
    have = {e.get("pmcid") for e in index}
    for e in index:
        y = str(e.get("year") or "")
        e["year"] = int(y[:4]) if y[:4].isdigit() else None
    for theme in a.theme:
        n = 0
        for q in QUERIES[theme]:
            for rec in search(q):
                pmcid = rec.get("pmcid")
                if not pmcid or pmcid in have:
                    continue
                if rec.get("isOpenAccess") != "Y":
                    continue
                if not (rec.get("fullTextUrlList") or rec.get("pmcid")):
                    continue
                title = re.sub(r"\s+", " ", rec.get("title") or "")
                e = {
                    "pmcid": pmcid, "doi": rec.get("doi"), "pmid": rec.get("pmid"),
                    "title": title, "journal": (rec.get("journalInfo") or {}).get("journal", {}).get("title"),
                    "year": rec.get("pubYear"), "themes": [theme],
                    "tags": tags_for(title, theme),
                    "citedBy": rec.get("citedByCount"),
                    "url": "https://europepmc.org/article/PMC/" + pmcid,
                }
                xml = get("%s/%s/fullTextXML" % (API, pmcid))
                if not xml or len(xml) < 3000:
                    continue
                xp = os.path.join(PDIR, "xml", pmcid + ".xml")
                open(xp, "wb").write(xml)
                txt = re.sub(r"<[^>]+>", " ", xml.decode("utf-8", "ignore"))
                txt = re.sub(r"[ \t]+", " ", txt)
                tp = os.path.join(PDIR, "txt", pmcid + ".txt")
                open(tp, "w", encoding="utf-8").write(txt)
                e["xml"] = "papers/xml/%s.xml" % pmcid
                e["text"] = "papers/txt/%s.txt" % pmcid
                e["paras"] = len(re.findall(r"<p[ >]", xml.decode("utf-8", "ignore")))
                index.append(e); have.add(pmcid)
                json.dump(index, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                n += 1
                print("  [%s] %s %s | %s (%d 段)" % (theme, pmcid, e.get("year"), title[:62], e["paras"]), flush=True)
                if n >= a.per_theme:
                    break
                time.sleep(0.4)
            if n >= a.per_theme:
                break
        print("主题 %s 新增 %d 篇" % (theme, n))

    index.sort(key=lambda x: (x["themes"][0], -int(str(x.get("year") or 0)[:4] or 0)))
    json.dump(index, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    L = ["# 公共知识 · OA 文献库（EuropePMC，风险评估/毒理/质谱）\n",
         "> 共 %d 篇开放获取全文（JATS XML + 纯文本）。引用格式：`第一作者. 题名. 期刊 年份. DOI / PMCID.`\n"
         "> 全文检索：`grep -o '.\\{0,60\\}关键词.\\{0,60\\}' papers/txt/PMC*.txt`\n",
         "\n| 主题 | 标签 | 年份 | 题名 | DOI | PMCID | 段落 |", "|---|---|---|---|---|---|---|"]
    for e in index:
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            "/".join(e.get("themes") or ["-"]), ",".join(e.get("tags") or [])[:3], e.get("year"),
            (e.get("title") or "")[:80].replace("|", "/"), e.get("doi") or "-", e["pmcid"], e.get("paras")))
    open(os.path.join(PDIR, "INDEX.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("已写 index.json(%d) 与 INDEX.md" % len(index))


if __name__ == "__main__":
    main()
