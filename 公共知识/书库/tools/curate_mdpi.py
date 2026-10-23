#!/usr/bin/env python3
"""
从 sources_mdpi_raw.json 中挑出与「风险评估 / 毒理 / 质谱」三条线**直接相关**的书目，
输出 sources_mdpi.json（供 build_booklib.py 下载）。

两级判定（保守、可复核）：
1. REQUIRE[theme]：题名须同时含「核心对象」与「方法/危害关键词」（两段都要命中）
2. BLOCK：明显离题（地质/建筑/宗教/兽医临床/吸附材料/植物抗逆/土壤修复……）
3. 每主题配额 + 年份倒序（优先近 5 年）
用法: python3 tools/curate_mdpi.py [--dry] [--quota 20]
"""
import json, re, os, sys, html, argparse
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "sources_mdpi_raw.json")
OUT = os.path.join(ROOT, "sources_mdpi.json")

# ------------------------------------------------- 主题双段必现（对象 AND 方法/危害）
OBJ = {
    "risk": r"\b(food|foods|diet|dietary|nutrition|nutrient|milk|meat|cereal|grain|fruit|vegetab|"
            r"honey|wine|juice|tea|coffee|infant|breast ?milk|aquatic product|seafood|fish product|"
            r"agricultural product|spice|oil|fatty|egg|poultry product|dairy|agricultural produce|"
            r"pesticide|insecticid|mycotoxin|aflatoxin|residues?|veterdrug|antibiotic resid|"
            r"contaminants?|pathogens?|additives?|beverage|drinking water|tap water)\b",
    "tox": r"\b(chemical|chemicals|compound|compounds|drug|drugs|xenobiotic|mycotoxin|aflatoxin|"
           r"pesticide|heavy metal|cadmium|lead|arsenic|mercury|phthalate|bisphenol|bpa|dioxin|"
           r"pcbs?|particle|nanomaterial|nanoparticle|additive|preservative|contaminant|pollutant|"
           r"substance|agent|mycotoxins|acrylamide|patulin|veterdrug)\b",
    "ms": r"\b(food|foods|diet|plasma|serum|urine|blood|tissue|cell|cells|biological|clinical|"
          r"plant|natural product|metabolite|lipid|protein|peptide|mycotoxin|pesticide|"
          r"residue|drug|contaminant|environmental|sample|extract|speciation|element|biomedical|"
          r"pharmaceutical|dairy|meat|honey|wine|cereal|seafood|flavour|aroma|authenticit)\b",
}
METHOD = {
    "risk": r"(risk assess|risk analysis|risk charact|risk manage|exposure assess|exposure evaluation|"
            r"dietary exposure|intake|health risk|hazard|food safety|safety assess|contaminat|residue|"
            r"mycotoxin|aflatoxin|heavy metal|toxic metal|acrylamide|3-?mcpd|furan|pah|"
            r"food additive|food contact|migrat|microbiolog|foodborne|food borne|pathogen|"
            r"salmonella|listeria|surveillance|monitoring|total diet|haccp|hygiene|adverse|"
            r"tolerable|adi|rfd|margin of exposure|moe)",
    "tox": r"(toxicolog|toxicity|toxic|dose|dosing|noael|loael|benchmark|threshold|"
            r"genotox|mutagen|carcinogen|carcinogenic|mutagenic|endocrine|estrogen|androgen|"
            r"hepato|nephro|neurotoxic|reprotox|reproductive tox|developmental tox|teratogen|"
            r"immunotox|cytotox|oxidative stress|mechanism|mode of action|adverse outcome|"
            r"in silico|insilico|qsar|read-?across|ttc|threshold of toxicological|"
            r"in vitro|cell-?based|organoid|high-?throughput|alternative method|non-?animal|"
            r"toxicokine|toxicodynamic|adme|metabolism of|biotransformation|risk assess|"
            r"exposure|biomonitoring|health effect|hazard ident)",
    "ms": r"(mass spectrometr|lc-?ms|gc-?ms|hrms|orbitrap|q-?tof|maldi|esi|api-?ms|"
           r"ion mobility|chromatograph|metabolomic|lipidomic|proteomic|peptidomic|"
           r"molecular imaging f|f-?irm s|nir s?|spectroscop|sample preparation|extraction|"
           r"quenchers|quee?ch?ers|spe|sme|derivati|quantif|validation|method development|"
           r"non-?target|untargeted|screening|identification|elucidat|feature|"
           r"residue analysis|determination|trace analysis|analytical|speciation|icp)",
}
BLOCK = re.compile(
    r"\b(geotechn|geolog|landslide|earthquake|seismic|flood|drought|urban|city|cities|building|"
    r"architecture|climatic|climate change|carbon neutrality|religio|migration of people|ethnic|"
    r"cultural|tourism|heritage|invasions?|weed|bee keep|apitherapy|"
    r"adsorbent|adsorption|removal of|remediation|degradation of dye|catalyst|photocataly|"
    r"membrane fabrication|sensor fabrication|electrode|wearable|device engineering|"
    r"farmland|soil|sediment|groundwater|river|lake|wetland|marine ecosystem|coral|air quality|"
    r"atmospheric|wastewater|sewage|compost|biochar|fertilizer|irrigat|cropping system|"
    r"livestock|poultry farming|broiler|cattle|swine|pig|rumen|sheep|goat|aquaculture|shrimp farm|"
    r"veterinary|vet\b|dog|cat\b|equine|horse|animal feed|dairy cow|"
    r"plant defence|plant growth|plant breed|seed breed|horticult|postharvest|fruit fly|insect pest|"
    r"plant pathogen|crop disease|fungicide of plant|biocontrol|"
    r"immunotherap|chemotherap|radiotherap|clinical trial|surgery|surgical|dental|orthodont|"
    r"ophthalm|vaccine|epilept|autism|depress|anxiety|schizophren|alzheim|parkinson|stroke|"
    r"tumor microenvironment|cancer cell line treatment|leukem|lymphoma|melanom|"
    r"forensic|post-?mortem|addiction|alcohol use disorder|obesity surgery|"
    r"microbiome of gut disease|probiotic ferment|kefir|yoghurt production|"
    r"synthesis of nanoparticle|green synthesis|quantum dot|graphene|photovolta|solar|"
    r"hydrogen|battery|fuel cell|supercapacitor|concrete|asphalt|weld|corrosion|"
    r"machine vision of fruit|deep learning diagnostic|nlp|large language|"
    r"image-?based screening|clinical care|waste treatment|environmental management|"
    r"nutraceutical|cosmetic|marine bioactive|sustainable foods|supply chain|"
    r"extraction technologies|shelf-?life|storage and|"
    r"plant (response|defence|genetic)|abiotic stress|emerging pathogens|fight against pathogens|"
    r"ADP-ribosylation|molecular microbiology|bioinformatics|biogeograph|invasion|"
    r"natural products and their modifications|health promoting effects)", re.I)


def ok(e, theme):
    t = re.sub(r"<[^>]+>", " ", html.unescape(e["title"]))  # 去 em 标签与实体
    t = " ".join(t.lower().split())
    return (re.search(OBJ[theme], t) and re.search(METHOD[theme], t)
            and not BLOCK.search(t)), t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--quota", type=int, default=20)
    a = ap.parse_args()
    raw = json.load(open(RAW, encoding="utf-8"))
    picked, by_theme, seen_id = [], defaultdict(int), set()
    for e in raw:
        cand = [th for th in ("risk", "tox", "ms") if th in (e.get("themes") or [])]
        good = [th for th in cand if ok(e, th)[0]]
        if not good:
            continue
        theme = next((th for th in good if by_theme[th] < a.quota), None)
        if not theme or e["id"] in seen_id:
            continue
        seen_id.add(e["id"])
        by_theme[theme] += 1
        e2 = dict(e)
        e2["title"] = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(e["title"]))).strip()
        e2["select_theme"] = theme
        e2.setdefault("publisher", "MDPI")
        e2.setdefault("license", "CC BY 4.0")
        e2.setdefault("sub", "mdpi")
        e2.setdefault("source", "https://doi.org/%s" % e["doi"])
        picked.append(e2)

    picked.sort(key=lambda x: -(x.get("year") or 0))
    print("候选 %d -> 选入 %d；主题分布 %s" % (len(raw), len(picked), dict(by_theme)))
    for p in picked:
        print("  %6s %s [%s] %s" % (p["id"], p.get("year"), p["select_theme"], p["title"][:80]))
    if not a.dry:
        json.dump(picked, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("\n已写 %s" % OUT)


if __name__ == "__main__":
    main()
