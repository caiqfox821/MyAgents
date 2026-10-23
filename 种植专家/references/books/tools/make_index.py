#!/usr/bin/env python3
"""生成种植电子书库编目: catalog.json、INDEX.md、toc/<sub>/<book>.md"""
import os, re, json, subprocess, glob
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = os.path.join(ROOT, "text")

CAT = {
 # ---------------- 水稻 rice ----------------
 "Rice_Almanac_4th_Edition_2013": ("Rice Almanac, 4th Edition", 2013, "IRRI / Archive.org", "Open Access", "https://archive.org/details/RiceAlmanac", ["水稻","综合","种质","生产统计"], "rice"),
 "Rice_Improvement_2021": ("Rice Improvement: Physiological, Molecular and Breeding Perspectives", 2021, "Springer (OA)", "CC BY", "https://doi.org/10.1007/978-3-030-66530-2", ["水稻","育种","生理"], "rice"),
 "Sustainable_Rice_Straw_Management_2019": ("Sustainable Rice Straw Management", 2019, "Springer (OA)", "CC BY", "https://doi.org/10.1007/978-3-030-32373-8", ["水稻","秸秆","循环利用"], "rice"),
 "Rice_Crop_Current_Developments_2018": ("Rice Crop - Current Developments", 2018, "IntechOpen", "CC BY", "https://www.intechopen.com/books/6366", ["水稻","栽培","综合"], "rice"),
 "Rice_Germplasm_Genetics_and_Improvement_2014": ("Rice - Germplasm, Genetics and Improvement", 2014, "IntechOpen", "CC BY", "https://www.intechopen.com/books/3554", ["水稻","种质","遗传育种"], "rice"),
 "Molecular_Breeding_and_Germplasm_Improvement_of_Rice_2025": ("Molecular Breeding and Germplasm Improvement of Rice", 2025, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-7258-3009-1", ["水稻","分子育种","种质"], "rice"),
 "Field_Water_Management_and_Irrigation_Rice_Training_Guide": ("Field Water Management and Irrigation for Improved Rice Systems: A Training Guide", 2021, "CGIAR/AfricaRice", "Open Access", "https://cgspace.cgiar.org/", ["水稻","水分管理","灌溉","培训"], "rice"),
 "Mechanized_Rice_Seeder_Technical_Manual": ("Technical Manual on Mechanized Rice Seeder Utilization", 2021, "CGIAR", "Open Access", "https://cgspace.cgiar.org/", ["水稻","机械化","直播","装备"], "rice"),
 "Rice_Straw_Management_Technical_Manual": ("Technical Manual: Rice Straw Management towards Circular Economy and Low Emission", 2021, "CGIAR", "Open Access", "https://cgspace.cgiar.org/", ["水稻","秸秆","循环经济"], "rice"),
 "Pictorial_Guide_Rice_Diseases_and_Pests": ("Pictorial Guide for the Identification of Rice Diseases and Pests", 2021, "CGIAR", "Open Access", "https://cgspace.cgiar.org/", ["水稻","病虫害","图鉴","绿色防控"], "rice"),
 "Sustainable_Insect_Pest_Management_Rice_SubSaharan_Africa": ("Sustainable Insect Pest Management Options for Rice Production in Sub-Saharan Africa", 2021, "CGIAR", "Open Access", "https://cgspace.cgiar.org/", ["水稻","虫害","绿色防控"], "rice"),
 "Natural_Biological_Control_African_Rice_Gall_Midge_IITA": ("Natural Biological Control of African Rice Gall Midge (IITA Research Guide 37)", 1994, "IITA", "Open Access", "https://cgspace.cgiar.org/", ["水稻","生物防治","虫害"], "rice"),
 "Growing_Upland_Rice_in_Nigeria": ("Growing Upland Rice in Nigeria (Commercial Crop Production Guide)", 2020, "USAID/Guide", "Open Access", "https://cgspace.cgiar.org/", ["水稻","旱稻","栽培指南"], "rice"),
 "Stem_Borers_of_Cereal_Crops_in_Africa": ("Stem Borers of Cereal Crops in Africa and Their Management", 2021, "IntechOpen", "CC BY", "https://www.intechopen.com/", ["水稻","虫害","螟虫"], "rice"),
 # ---------------- 水稻 rice · 2026-10 新增 ----------------
 "Molecular_Research_in_Rice_2020": ("Molecular Research in Rice", 2020, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/2941", ["水稻","分子育种","种质"], "rice"),
 "Genetics_in_Rice_2020": ("Genetics in Rice", 2020, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/2807", ["水稻","遗传育种","基因组"], "rice"),
 "Molecular_Research_in_Rice_Agronomically_Important_Traits_2_0_2022": ("Molecular Research in Rice: Agronomically Important Traits 2.0", 2022, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/6479", ["水稻","分子育种","农艺性状"], "rice"),
 "Gene_Mining_and_Germplasm_Innovation_Rice_2025": ("Gene Mining and Germplasm Innovation for the Important Traits in Rice", 2025, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/10932", ["水稻","基因挖掘","种质创新"], "rice"),
 "Exploiting_the_Rice_Germplasm_Health_Promoting_Foods_2024": ("Exploiting the Rice Germplasm for Health-Promoting and Value-Added Foods", 2024, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/10118", ["水稻","种质","功能食品"], "rice"),
 "Closing_Rice_Yield_Gaps_in_Asia_2023": ("Closing Rice Yield Gaps in Asia", 2023, "Springer (OA)", "CC BY", "https://doi.org/10.1007/978-3-031-37947-5", ["水稻","产量差","可持续农业"], "rice"),
 "Rice_Green_Revolution_in_Sub_Saharan_Africa_2023": ("Rice Green Revolution in Sub-Saharan Africa", 2023, "Springer (OA)", "CC BY", "https://doi.org/10.1007/978-981-19-8046-6", ["水稻","非洲","发展"], "rice"),
 "Recent_Advances_in_Rice_Research_2020": ("Recent Advances in Rice Research", 2020, "IntechOpen", "CC BY", "https://www.intechopen.com/books/9669", ["水稻","栽培","综合"], "rice"),
 "ORYZA_Simulation_Modules_Rice_Production_1994": ("ORYZA Simulation Modules for Potential and Nitrogen Limited Rice Production", 1994, "Wageningen (WUR)", "Open Access", "https://edepot.wur.nl/297741", ["水稻","生长模型","模拟","氮素"], "rice"),
 "Nitrogen_Management_in_Irrigated_Rice_1995": ("Nitrogen Management Studies in Irrigated Rice", 1995, "Wageningen (WUR)", "Open Access", "https://edepot.wur.nl/344761", ["水稻","氮肥","水肥","模型"], "rice"),
 "Water_wise_Rice_Production_2002": ("Water-wise Rice Production", 2002, "IRRI", "Open Access", "https://ageconsearch.umn.edu/record/281822", ["水稻","节水","水分管理","灌溉"], "rice"),
 "A_Practical_Field_Guide_to_Weeds_of_Rice_in_Asia_2010": ("A Practical Field Guide to Weeds of Rice in Asia", 2010, "IRRI", "Open Access", "https://ageconsearch.umn.edu/record/164472", ["水稻","杂草","图鉴","植保"], "rice"),
 "Nutrient_Management_Rainfed_Lowland_Rice_Lao_PDR_2001": ("Nutrient Management in Rainfed Lowland Rice in the Lao PDR", 2001, "IRRI", "Open Access", "https://ageconsearch.umn.edu/record/281826", ["水稻","养分管理","雨养","施肥"], "rice"),
 "Rice_Cultivation_Handbook_2024": ("Rice Cultivation Handbook", 2024, "CGIAR / AfricaRice", "Open Access", "https://cgspace.cgiar.org/items/e76a7d69-0b2e-4b92-96c3-adc21721f654", ["水稻","栽培指南","综合"], "rice"),
 # ---------------- 其他作物/综合 crops ----------------
 "Sustainable_Crop_Production_2019": ("Sustainable Crop Production", 2019, "IntechOpen", "CC BY", "https://www.intechopen.com/books/9345", ["综合栽培","可持续农业","肥水"], "crops"),
 "Sustainable_Crop_Production_Recent_Advances_2022": ("Sustainable Crop Production - Recent Advances", 2022, "IntechOpen", "CC BY", "https://www.intechopen.com/books/11357", ["综合栽培","可持续农业"], "crops"),
 "Crop_Production_Technologies_2012": ("Crop Production Technologies", 2012, "IntechOpen", "CC BY", "https://www.intechopen.com/books/597", ["综合栽培","技术"], "crops"),
 "Global_Wheat_Production_2018": ("Global Wheat Production", 2018, "IntechOpen", "CC BY", "https://www.intechopen.com/books/6776", ["小麦","粮食作物","栽培"], "crops"),
 "Abiotic_Stress_in_Plants_2020": ("Abiotic Stress in Plants", 2020, "IntechOpen", "CC BY", "https://www.intechopen.com/books/10363", ["逆境胁迫","抗旱","抗盐"], "crops"),
 "Advances_in_Cereal_Crops_Breeding_2021": ("Advances in Cereal Crops Breeding", 2021, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-0365-2651-5", ["育种","粮食作物"], "crops"),
 "Abiotic_Stress_of_Crops_2026": ("Abiotic Stress of Crops: Molecular Genetics and Genomic Perspectives", 2026, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-7258-6813-1", ["逆境胁迫","分子育种"], "crops"),
 "Integrated_Pest_Management_in_Horticulture_2025": ("Integrated Pest Management in Horticulture", 2025, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-7258-3710-6", ["植保","IPM","园艺作物"], "crops"),
 "Soil_Fertility_Plant_Nutrition_and_Nutrient_Management_2026": ("Soil Fertility, Plant Nutrition and Nutrient Management", 2026, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-7258-8644-9", ["土壤肥力","植物营养","施肥"], "crops"),
 "Field_Crop_Production_in_Tropical_Africa_1991": ("Field Crop Production in Tropical Africa", 1991, "CTA / CGIAR", "Open Access", "https://cgspace.cgiar.org/", ["综合栽培","热带农业","粮食作物"], "crops"),
 "Introduction_to_Crop_Production_2023": ("Introduction to Crop Production", 2023, "Zenodo", "Open Access", "https://zenodo.org/record/8400944", ["综合栽培","教材"], "crops"),
 # ---------------- 其他作物/综合 crops · 2026-10 新增 ----------------
 "Soil_Fertility_Plant_Nutrition_Sustainable_Cropping_2026": ("Soil Fertility and Plant Nutrition for Sustainable Cropping Systems", 2026, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/12848", ["土壤肥力","植物营养","可持续农业"], "crops"),
 "Crop_Nutrient_Requirements_Advanced_Fertilizer_Management_2024": ("Crop Nutrient Requirements and Advanced Fertilizer Management Strategies", 2024, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/9034", ["施肥","养分管理","植物营养"], "crops"),
 "Integrated_Soil_Management_2025": ("Integrated Soil Management", 2025, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/11236", ["土壤管理","土壤健康","综合栽培"], "crops"),
 "Biological_Pest_Control_in_Agroecosystems_2025": ("Biological Pest Control in Agroecosystems", 2025, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/11248", ["生物防治","植保","绿色防控"], "crops"),
 "Plant_Fungal_Diseases_and_Crop_Protection_2025": ("Plant Fungal Diseases and Crop Protection", 2025, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/11024", ["病害","真菌","植保"], "crops"),
 "New_Insights_into_Pathogen_Insect_Pest_and_Weed_Control_2024": ("New Insights into Pathogen, Insect Pest, and Weed Control in Field and Greenhouse Cropping Systems", 2024, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/9196", ["病虫草害","植保","综合"], "crops"),
 "Agricultural_Crops_Subjected_to_Drought_and_Salinity_Stress_2025": ("Agricultural Crops Subjected to Drought and Salinity Stress", 2025, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/11204", ["逆境胁迫","抗旱","抗盐"], "crops"),
 "Conservation_Agricultural_Practices_Improving_Crop_Production_2025": ("Conservation Agricultural Practices for Improving Crop Production and Quality", 2025, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/10710", ["保护性耕作","综合栽培","土壤健康"], "crops"),
 "Advances_in_Crop_Molecular_Breeding_and_Genetics_2025": ("Advances in Crop Molecular Breeding and Genetics", 2025, "MDPI", "CC BY", "https://www.mdpi.com/books/reprint/10478", ["分子育种","遗传育种","作物改良"], "crops"),
}

def pages(pdf):
    try:
        out = subprocess.check_output(["pdfinfo", pdf], stderr=subprocess.DEVNULL, text=True)
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        return int(m.group(1)) if m else None
    except Exception:
        return None

def toc_of(text):
    lines = text.split("\n")
    for i, ln in enumerate(lines[:6000]):
        if re.match(r"^\s*(Contents|Table of Contents|CONTENTS)\s*$", ln):
            block = [l.rstrip() for l in lines[i+1:i+90]]
            return [b for b in block if b.strip()][:70], "Contents"
    ch = [ln.strip() for ln in lines if re.match(r"^\s*(CHAPTER|Chapter)\s+[IVXLC0-9]", ln)][:50]
    if ch:
        return ch, "Chapters"
    num = [ln.strip() for ln in lines if re.match(r"^\s*\d+(\.\d+){0,2}\s+[A-Z][A-Za-z]", ln) and len(ln.strip()) < 90][:50]
    if num:
        return num, "Sections"
    return [], "none"

def main():
    catalog = []
    for txt in sorted(glob.glob(os.path.join(TEXT, "**", "*.txt"), recursive=True)):
        stem = os.path.splitext(os.path.basename(txt))[0]
        sub = os.path.relpath(os.path.dirname(txt), TEXT)
        meta = CAT.get(stem)
        if not meta:
            print("WARN 未编目:", stem); continue
        title, year, pub, lic, url, tags, cat = meta
        pdf = os.path.join(ROOT, sub, stem + ".pdf")
        pg = pages(pdf) if os.path.exists(pdf) else None
        with open(txt, encoding="utf-8", errors="ignore") as f:
            text = f.read()
        tlines, tkind = toc_of(text)
        catalog.append({"file": stem, "sub": sub, "title": title, "year": year,
            "publisher": pub, "license": lic, "source": url, "tags": tags, "pages": pg,
            "pdf": os.path.relpath(pdf, ROOT) if os.path.exists(pdf) else None,
            "text": os.path.relpath(txt, ROOT), "toc": tlines, "toc_kind": tkind,
            "text_chars": len(text)})
        tocdir = os.path.join(ROOT, "toc", sub); os.makedirs(tocdir, exist_ok=True)
        with open(os.path.join(tocdir, stem + ".md"), "w", encoding="utf-8") as f:
            f.write(f"# {title} ({year}, {pub})\n\n- 许可: {lic}\n- 来源: {url}\n- 页数: {pg}\n- 全文: `{catalog[-1]['text']}`\n- PDF: `{catalog[-1]['pdf']}`\n- 标签: {', '.join(tags)}\n\n## 目录 ({tkind})\n\n")
            f.write("\n".join(f"- {l}" for l in tlines) if tlines else "（自动目录提取失败，请用全文检索工具）")
            f.write("\n")
    with open(os.path.join(ROOT, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"catalog.json {len(catalog)} 条")

    bytag = defaultdict(list)
    for e in catalog:
        for t in e["tags"]:
            bytag[t].append(e)
    subs = [("rice", "水稻专题（Rice）"), ("crops", "其他作物 / 综合农学（Crops & General）")]
    L = ["# 种植电子书库 · 全文索引（INDEX）\n",
         f"> 共 **{len(catalog)} 册**，合法开放获取（CC BY / OA）。水稻 **{len([e for e in catalog if e['sub']=='rice'])} 册**。",
         "> **全文文本** `text/<分区>/<书名>.txt`；**目录** `toc/<分区>/<书名>.md`；元数据 `catalog.json`。\n",
         "## 一、如何使用（给种植专家）\n", "```bash",
         'python3 references/books/tools/search_books.py "nitrogen" --context 1',
         'python3 references/books/tools/search_books.py "rice blast" --books        # 哪本书讲得最多',
         'python3 references/books/tools/search_books.py "transplanting" --book rice  # 限定水稻分区',
         'python3 references/books/tools/read_page.py Rice_Almanac 120               # 按页读原文',
         "```",
         "- 命中 `书|页码|原文` 后读 `toc/` 定位章节、`text/` 页码附近引用；引用注明 作者/编者、书名、出版社、年份、页码。\n",
         "## 二、主题标签索引\n"]
    for tag in sorted(bytag):
        titles = "；".join(f"{e['title']}（{e['year']}）" for e in sorted(bytag[tag], key=lambda x: x["year"]))
        L.append(f"- **{tag}**：{titles}")
    L.append("")
    for sub, name in subs:
        items = [e for e in catalog if e["sub"] == sub]
        if not items: continue
        L.append(f"## {name}\n")
        L.append("| 书名 | 年 | 页 | 全文 | 目录 | 来源 |")
        L.append("|---|---|---|---|---|---|")
        for e in sorted(items, key=lambda x: -x["year"]):
            L.append(f"| {e['title']} | {e['year']} | {e['pages'] or '-'} | `{e['text']}` | `toc/{e['sub']}/{e['file']}.md` | {e['source']} |")
        L.append("")
    L.append("---\n*由种植专家维护；新增电子书后运行 `python3 tools/make_index.py` 重建。*")
    with open(os.path.join(ROOT, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("INDEX.md 已生成")

if __name__ == "__main__":
    main()
