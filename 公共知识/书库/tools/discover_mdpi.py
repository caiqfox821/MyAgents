#!/usr/bin/env python3
"""
公共知识 OA 书库 · MDPI Books 书目发现（风险评估 / 毒理 / 质谱 三主题）。
- 数据源: Crossref REST API（type:book, prefix:10.3390）
- 由 resource.primary.URL（https://www.mdpi.com/books/reprint/<id>）取 reprint id
  = mdpi-res.com/bookfiles/book/<id>/<slug>.pdf 的 id
- 用法: python3 tools/discover_mdpi.py            # 全部主题
        python3 tools/discover_mdpi.py risk       # 单主题
输出: sources_mdpi_raw.json
"""
import os, re, json, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "sources_mdpi_raw.json")
UA = "public-knowledge-lib/1.0 (mailto:lib@example.org)"

# ---------------------------------------------------------------- 三主题检索式
QUERIES = {
    "risk": [
        "food risk assessment", "dietary exposure assessment", "food safety hazards",
        "pesticide residues food", "veterinary drug residues", "mycotoxins food safety",
        "heavy metals in food", "food contaminants", "aflatoxin contamination",
        "acrylamide in food", "food additives safety", "microbiological food safety",
        "foodborne pathogens risk", "risk management food", "hazard analysis critical control point",
        "toxic metals cereal", "dioxins PCB food", "process contaminants food",
        "food contact materials migration", "total diet study",
    ],
    "tox": [
        "toxicology", "dose response toxicology", "in vitro toxicology",
        "alternative methods toxicology", "endocrine disrupting chemicals",
        "genotoxicity", "carcinogenicity", "hepatotoxicity", "nephrotoxicity",
        "nanotoxicology", "environmental toxicology", "oxidative stress toxicology",
        "reproductive toxicity", "developmental toxicity", "mechanism of action toxicity",
        "predictive toxicology", "computational toxicology", "adverse outcome pathway",
        "xenobiotic metabolism", "toxicokinetics",
    ],
    "ms": [
        "mass spectrometry", "LC-MS", "GC-MS", "high resolution mass spectrometry",
        "metabolomics", "lipidomics", "proteomics mass spectrometry",
        "food authentication mass spectrometry", "untargeted screening",
        "ion mobility spectrometry", "sample preparation mass spectrometry",
        "imaging mass spectrometry", "MALDI-TOF", "quantitative mass spectrometry",
        "mass spectrometry imaging food", "analytical chemistry food",
        "mycotoxin analysis", "pesticide residue analysis", "elemental speciation",
        "isotope dilution mass spectrometry",
    ],
}

# ---------------------------------------------------------------- 会话 6 扩充检索式（新主题）
QUERIES["risk"] += [
    "PFAS per- and polyfluoroalkyl substances food drinking water",
    "microplastics food human health risk",
    "mineral oil hydrocarbons MOSH MOAH food",
    "nitrate nitrite food drinking water",
    "perchlorate food exposure",
    "aluminium food exposure risk",
    "arsenic rice exposure risk",
    "methylmercury fish consumption",
    "risk benefit assessment food",
    "human biomonitoring exposure chemicals",
    "nanomaterials food safety",
    "exposome environmental health",
    "emerging contaminants food",
    "food fraud authenticity risk",
]
QUERIES["tox"] += [
    "PFAS perfluoroalkyl substance toxicity",
    "microplastic nanoplastic toxicity",
    "immunotoxicity",
    "developmental neurotoxicity",
    "skin sensitisation",
    "cancer hazard classification",
    "mixture toxicity chemicals",
    "toxicogenomics",
    "physiologically based pharmacokinetic modelling",
    "in vitro in vivo extrapolation",
    "systematic review toxicology",
    "botanical safety assessment",
    "mycotoxin toxicity",
    "neurotoxicity",
    "air pollution health toxicity",
    "heavy metal neurotoxicity",
    "food contact chemical toxicity",
    "hepatotoxicity mechanisms",
]
QUERIES["ms"] += [
    "PFAS analysis mass spectrometry",
    "microplastic analysis spectroscopy",
    "exposomics metabolomics",
    "human biomonitoring mass spectrometry",
    "foodomics",
    "data independent acquisition",
    "ambient ionization mass spectrometry",
    "single cell mass spectrometry",
    "multi-omics",
    "contaminant analysis food mass spectrometry",
    "liquid chromatography tandem mass spectrometry",
    "volatile organic compounds analysis",
    "mass spectrometry clinical diagnosis",
    "food metabolomics",
    "emerging contaminants mass spectrometry",
    "metabolomics data analysis",
]

# 主题 -> 标签推断
TAGRULES = {
    "risk": [
        (("risk assessment", "risk analysis", "hazard"), "风险评估"),
        (("exposure", "dietary intake", "consumption"), "暴露评估"),
        (("pesticide", "insecticid", "herbicid"), "农药残留"),
        (("veterinary", "antibiotic residue", "drug residue"), "兽药残留"),
        (("mycotoxin", "aflatoxin", "ochratoxin", "fusarium", "patulin"), "真菌毒素"),
        (("heavy metal", "toxic metal", "lead", "cadmium", "arsenic", "mercury"), "重金属"),
        (("acrylamide", "furan", "3-mcpd", "paH", "process contaminant"), "加工污染物"),
        (("additive", "sweetener", "colourant", "emulsifier"), "食品添加剂"),
        (("pathogen", "salmonella", "listeria", "microbiol", "foodborne"), "微生物危害"),
        (("food contact", "migration", "packaging"), "食品接触材料"),
        (("haccp", "critical control", "hygiene", "safety management"), "HACCP 与体系"),
        (("dioxin", "PCB", "POP", "persistent organic"), "持久性污染物"),
    ],
    "tox": [
        (("dose response", "benchmark dose", "BMD", "noael", "toxicity testing"), "剂量-反应"),
        (("in vitro", "alternative method", "non-animal", "NAM", "organoid", "cell-based"), "体外与替代方法"),
        (("endocrine", "EDC"), "内分泌干扰"),
        (("genotox", "mutagen", "comet", "micronucleus", "AMES"), "遗传毒性"),
        (("cancer", "carcinogen", "tumour", "tumor"), "致癌性"),
        (("liver", "hepato"), "肝毒性"),
        (("kidney", "renal", "nephro"), "肾毒性"),
        (("nano",), "纳米毒理"),
        (("reproduc", "develop", "embryo", "gestation", "terat"), "生殖发育毒理"),
        (("mechanism", "pathway", "AOP", "mode of action"), "毒作用机制/AOP"),
        (("predict", "computational", "in silico", "SAR", "read-across", "TTC"), "计算毒理"),
        (("metabolism", "metabolic", "xenobiotic", "toxicokine", "ADME"), "毒代与代谢"),
        (("environment", "ecotox", "pollutant", "pesticide tox"), "环境与生态毒理"),
        (("oxidative", "inflamm"), "氧化应激与炎症"),
    ],
    "ms": [
        (("LC-MS", "liquid chromatography", "HPLC", "UPLC"), "LC-MS"),
        (("GC-MS", "gas chromatography", "headspace"), "GC-MS"),
        (("high resolution", "HRMS", "Orbitrap", "Q-TOF", "FT-ICR"), "高分辨质谱"),
        (("MALDI",), "MALDI-TOF"),
        (("imaging", "MSI"), "质谱成像"),
        (("metabolom",), "代谢组学"),
        (("lipidom",), "脂质组学"),
        (("proteom", "peptidom"), "蛋白质组学"),
        (("ion mobility",), "离子迁移谱"),
        (("sample preparation", "extraction", "SPE", "dispersive"), "样品前处理"),
        (("authentication", "traceab", "adulterat", "origin"), "食品真实性鉴定"),
        (("screening", "untargeted", "non-target", "unknown"), "非靶向筛查"),
        (("quantit", "MRM", "SRM", "isotope dilution", "validation"), "定量与验证"),
        (("mycotoxin", "aflatoxin"), "毒素分析"),
        (("pesticide", "residue"), "农残分析"),
        (("speciation", "ICP", "elemental", "metallomic"), "元素形态分析"),
    ],
}

# 明显离题的排除词（跨主题共用）
BLOCK = re.compile(r"\b(astronom|cosmolog|galaxy|quantum comput|photovolta|solar cell|"
                   r"wind tunnel|turbine|concrete|reinforc|steel structure|bridge|"
                   r"robot|autonomous vehicle|drone|5G|antenna|cryptograph|"
                   r"blockchain|deep learning in education|e-learning|"
                   r"orthoped|dental|periodont|ophthalm|surgic|transplant|"
                   r"archaeolog|linguistic|literature review of fiction|"
                   r"tourism|hospitality|sport coaching|finance|accounting|marketing|"
                   r"supply chain of retail|urban planning|architecture|landscape|"
                   r"insect taxonomy|plant breeding field trial|crop breeding)\b", re.I)


def tags_for(title, theme):
    t = title.lower()
    out = [tag for keys, tag in TAGRULES[theme] if any(k.lower() in t for k in keys)]
    return out or [theme]


def slug(title):
    s = re.sub(r"[^A-Za-z0-9.]+", "_", title)
    return re.sub(r"_+", "_", s).strip("_")


def crossref(query, rows=120):
    url = ("https://api.crossref.org/works?filter=type:book,prefix:10.3390"
           "&rows=%d&select=DOI,title,ISBN,published,resource&query.bibliographic=%s"
           % (rows, urllib.parse.quote(query)))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)["message"]["items"]
        except Exception as e:
            print("  retry", query, e)
            time.sleep(3)
    return []


def main():
    themes = sys.argv[1:] or list(QUERIES)
    seen = {}
    for theme in themes:
        for q in QUERIES.get(theme, []):
            items = crossref(q)
            for it in items:
                doi = it.get("DOI")
                res = (it.get("resource", {}) or {}).get("primary", {}) or {}
                m = re.search(r"/books/reprint/(\d+)", res.get("URL", "") or "")
                if not m:
                    continue
                title = (it.get("title") or ["?"])[0].strip()
                if BLOCK.search(title):
                    continue
                year = (it.get("published", {}).get("date-parts", [[None]])[0] or [None])[0]
                prev = seen.get(doi)
                if prev:
                    if theme not in prev["themes"]:
                        prev["themes"].append(theme)
                        prev["tags"] += [t for t in tags_for(title, theme) if t not in prev["tags"]]
                    continue
                seen[doi] = {
                    "id": m.group(1),
                    "url_title": slug(title),
                    "file": f"{slug(title)}_{year}" if year else slug(title),
                    "year": year, "doi": doi, "title": title,
                    "themes": [theme],
                    "tags": tags_for(title, theme),
                }
            print(f"  [{theme}] {q!r:38} 累计 {len(seen)}", flush=True)
            time.sleep(0.8)
    entries = sorted(seen.values(), key=lambda e: -(e.get("year") or 0))
    json.dump(entries, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nsources_mdpi_raw.json 写入 {len(entries)} 册（去重后）")
    from collections import Counter
    print("主题分布:", dict(Counter(t for e in entries for t in e["themes"])))


if __name__ == "__main__":
    main()
