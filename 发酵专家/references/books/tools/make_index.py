#!/usr/bin/env python3
"""
生成发酵电子书库编目: catalog.json、INDEX.md、toc/<sub>/<book>.md
用法: python3 tools/make_index.py
"""
import os, re, json, subprocess, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # books/
TEXT = os.path.join(ROOT, "text")

# filename_stem: (中文/英文标题, 年份, 出版方, 许可, 来源URL, 主题标签[], 分区)
CAT = {
 # IntechOpen
 "Fermentation_Processes_2017": ("Fermentation Processes", 2017, "IntechOpen", "CC BY 3.0", "https://www.intechopen.com/books/5305", ["发酵工艺","菌种","动力学建模"], "intechopen"),
 "Brewing_Technology_2017": ("Brewing Technology", 2017, "IntechOpen", "CC BY 3.0", "https://www.intechopen.com/books/5967", ["传统酿造","啤酒"], "intechopen"),
 "New_Advances_on_Fermentation_Processes_2019": ("New Advances on Fermentation Processes", 2019, "IntechOpen", "CC BY 3.0", "https://www.intechopen.com/books/8244", ["发酵工艺","生物制造"], "intechopen"),
 "Fermentation_Processes_Benefits_and_Risks_2021": ("Fermentation - Processes, Benefits and Risks", 2021, "IntechOpen", "CC BY 3.0", "https://www.intechopen.com/books/9709", ["发酵工艺","食品安全"], "intechopen"),
 "Distillation_Innovative_Applications_and_Modeling_2017": ("Distillation - Innovative Applications and Modeling", 2017, "IntechOpen", "CC BY 3.0", "https://www.intechopen.com/books/5452", ["下游分离","蒸馏"], "intechopen"),
 "Distillation_Processes_2021": ("Distillation Processes - From Solar and Membrane Distillation", 2021, "IntechOpen", "CC BY 3.0", "https://www.intechopen.com/books/10995", ["下游分离","膜分离","蒸馏"], "intechopen"),
 "Enzyme_Inhibitors_and_Activators_2017": ("Enzyme Inhibitors and Activators", 2017, "IntechOpen", "CC BY 3.0", "https://www.intechopen.com/books/5540", ["酶工程","生物催化"], "intechopen"),
 "Probiotics_and_Prebiotics_in_Human_Nutrition_and_Health_2016": ("Probiotics and Prebiotics in Human Nutrition and Health", 2016, "IntechOpen", "CC BY 3.0", "https://www.intechopen.com/books/5193", ["益生菌","营养"], "intechopen"),
 "Bioethanol_Technologies_2020": ("Bioethanol Technologies", 2020, "IntechOpen", "CC BY 3.0", "https://www.intechopen.com/books/10379", ["生物乙醇","生物制造"], "intechopen"),
 # MDPI
 "Wine_Fermentation_2019": ("Wine Fermentation", 2019, "MDPI", "CC BY", "https://www.mdpi.com/books/pdfview/book/1190", ["传统酿造","葡萄酒"], "mdpi"),
 "Brewing_and_Craft_Beer_2019": ("Brewing and Craft Beer", 2019, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-03921-490-7", ["传统酿造","啤酒"], "mdpi"),
 "Polyphenolic_Compounds_in_Wine_and_Beer_2023": ("Polyphenolic Compounds in Wine and Beer", 2023, "MDPI", "CC BY", "https://www.mdpi.com/books/pdfview/book/6554", ["传统酿造","风味化学"], "mdpi"),
 "Bioprocess_Monitoring_and_Control_2020": ("Bioprocess Monitoring and Control", 2020, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-03936-933-1", ["工业发酵","过程控制","PAT"], "mdpi"),
 "Recent_Advances_Biocatalysis_and_Metabolic_Engineering_2019": ("Recent Advances in Biocatalysis and Metabolic Engineering for Biomanufacturing", 2019, "MDPI", "CC BY", "https://www.mdpi.com/books/pdfview/book/1569", ["代谢工程","生物催化","生物制造"], "mdpi"),
 "Modern_Technologies_Fermentation_Quality_2020": ("Modern Technologies and Their Influence in Fermentation Quality", 2020, "MDPI", "CC BY", "https://www.mdpi.com/books/pdfview/book/2285", ["发酵工艺","动力学建模"], "mdpi"),
 "Advances_in_Industrial_and_Environmental_Microbiology_2021": ("Advances in Industrial and Environmental Microbiology", 2021, "MDPI", "CC BY", "https://www.mdpi.com/books/pdfview/book/4600", ["工业发酵","环境微生物"], "mdpi"),
 "New_Insights_into_Food_Fermentation_2022": ("New Insights into Food Fermentation", 2022, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-0365-3919-5", ["食品发酵","菌种"], "mdpi"),
 "Digital_Technologies_on_Beverage_Fermentation_2022": ("Implementation of Digital Technologies on Beverage Fermentation", 2022, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-0365-3656-9", ["工业发酵","过程控制","饮料"], "mdpi"),
 "Advances_in_Microbial_Fermentation_Processes_2022": ("Advances in Microbial Fermentation Processes", 2022, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-0365-4010-8", ["发酵工艺","生物制造"], "mdpi"),
 "Fermentation_Processes_2025": ("Fermentation Processes", 2025, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-7258-5112-6", ["发酵工艺"], "mdpi"),
 "Fermentation_Technology_in_Animal_Nutrition_2024": ("Application of Fermentation Technology in Animal Nutrition", 2024, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-7258-2770-1", ["发酵饲料","生物制造"], "mdpi"),
 "Starter_Cultures_2nd_Edition_2026": ("Development and Application of Starter Cultures, 2nd Edition", 2026, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-7258-8454-4", ["发酵剂","菌种","食品发酵"], "mdpi"),
 "Recent_Advances_Lactic_Acid_Bacteria_2026": ("Recent Advances in Lactic Acid Bacteria and Metabolite for Food Quality", 2026, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-7258-7521-4", ["乳酸菌","菌种","食品发酵"], "mdpi"),
 "Prebiotics_and_Probiotics_2018": ("Prebiotics and Probiotics", 2018, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-03897-169-6", ["益生菌","营养"], "mdpi"),
 "Probiotics_and_Prebiotics_in_Pediatrics_2019": ("Probiotics and Prebiotics in Pediatrics", 2019, "MDPI", "CC BY", "https://www.mdpi.com/books/pdfview/book/1290", ["益生菌","营养"], "mdpi"),
 "Membrane_Distillation_2017": ("Membrane Distillation", 2017, "MDPI", "CC BY", "https://www.mdpi.com/books/pdfview/book/335", ["膜分离","下游分离"], "mdpi"),
 "Membrane_Distillation_Process_2021": ("Membrane Distillation Process", 2021, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-0365-1211-2", ["膜分离","下游分离"], "mdpi"),
 "Membrane_Materials_Bioseparation_Downstream_2026": ("Application of Membrane Materials in Bioseparation and Downstream Processing", 2026, "MDPI", "CC BY", "https://doi.org/10.3390/books978-3-7258-6773-8", ["膜分离","下游分离"], "mdpi"),
 # public domain
 "The_Principles_and_Practice_of_Brewing_1907": ("The Principles and Practice of Brewing (Sykes)", 1907, "Archive.org", "Public Domain", "https://archive.org/details/principlespracti00syke", ["传统酿造","历史经典"], "public_domain"),
 "The_Chemistry_of_Sake-Brewing_1881": ("The Chemistry of Sake-Brewing (Atkinson)", 1881, "Archive.org", "Public Domain", "https://archive.org/details/chemistryofsakeb00atki", ["传统酿造","清酒","历史经典"], "public_domain"),
 "Curiosities_of_Ale_and_Beer_1889": ("The Curiosities of Ale & Beer (Bickerdyke)", 1889, "Archive.org", "Public Domain", "https://archive.org/details/curiositiesofale00bick", ["传统酿造","啤酒","历史经典"], "public_domain"),
 "Micro-organisms_and_Fermentation_1900": ("Micro-organisms and Fermentation (Jorgensen)", 1900, "Archive.org", "Public Domain", "https://archive.org/details/microorganismsfe00jrrich", ["菌种","发酵工艺","历史经典"], "public_domain"),
 "Bacterial_Fermentations_1956": ("Bacterial Fermentations (Barker)", 1956, "Archive.org/BHL", "Public Domain", "https://archive.org/details/bacterialferment00bark", ["菌种","代谢","历史经典"], "public_domain"),
 # other
 "Industrial_Microbiology_in_the_Production_of_Organic_Compounds_2024": ("Industrial Microbiology in the Production of Organic Compounds", 2024, "BSP", "Open Access", "https://www.bspublications.com/", ["工业发酵","生物制造","有机化合物"], "other"),
}

def pages(pdf):
    try:
        out = subprocess.check_output(["pdfinfo", pdf], stderr=subprocess.DEVNULL, text=True)
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        return int(m.group(1)) if m else None
    except Exception:
        return None

def toc_of(text):
    """尽量抽取目录: 优先独立 'Contents' 块; 否则 CHAPTER/Chapter 标题; 再否则编号章节。"""
    lines = text.split("\n")
    # 1) Contents block
    for i, ln in enumerate(lines[:4000]):
        if re.match(r"^\s*(Contents|Table of Contents)\s*$", ln, re.I):
            block = [l.rstrip() for l in lines[i+1:i+80]]
            return [b for b in block if b.strip()][:60], "Contents"
    # 2) CHAPTER headings
    ch = [ln.strip() for ln in lines if re.match(r"^\s*(CHAPTER|Chapter)\s+[IVXLC0-9]", ln)][:40]
    if ch:
        return ch, "Chapters"
    # 3) numbered headings
    num = [ln.strip() for ln in lines if re.match(r"^\s*\d+(\.\d+){0,2}\s+[A-Z][A-Za-z]", ln) and len(ln.strip()) < 80][:40]
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
        entry = {
            "file": stem, "sub": sub, "title": title, "year": year, "publisher": pub,
            "license": lic, "source": url, "tags": tags, "pages": pg,
            "pdf": os.path.relpath(pdf, ROOT) if os.path.exists(pdf) else None,
            "text": os.path.relpath(txt, ROOT), "toc": tlines, "toc_kind": tkind,
        }
        catalog.append(entry)
        # per-book TOC file
        tocdir = os.path.join(ROOT, "toc", sub)
        os.makedirs(tocdir, exist_ok=True)
        with open(os.path.join(tocdir, stem + ".md"), "w", encoding="utf-8") as f:
            f.write(f"# {title} ({year}, {pub})\n\n")
            f.write(f"- 许可: {lic}\n- 来源: {url}\n- 页数: {pg}\n- 全文: `{entry['text']}`\n- PDF: `{entry['pdf']}`\n- 标签: {', '.join(tags)}\n\n## 目录 ({tkind})\n\n")
            f.write("\n".join(f"- {l}" for l in tlines) if tlines else "（自动目录提取失败，请用全文检索工具）")
            f.write("\n")

    with open(os.path.join(ROOT, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"catalog.json 写入 {len(catalog)} 条")

    # 标签索引
    from collections import defaultdict
    bytag = defaultdict(list)
    for e in catalog:
        for t in e["tags"]:
            bytag[t].append(e)

    subs = [("intechopen", "IntechOpen（CC BY）"), ("mdpi", "MDPI Books（CC BY）"),
            ("public_domain", "公共领域 / 历史经典"), ("other", "其他开放获取")]
    L = []
    L.append("# 发酵电子书库 · 全文索引（INDEX）\n")
    L.append(f"> 共 **{len(catalog)} 册**，全部为合法开放获取（CC BY / 公共领域）。")
    L.append("> PDF 存于各分区目录；**全文文本**在 `text/<分区>/<书名>.txt`；**目录**在 `toc/<分区>/<书名>.md`；结构化元数据 `catalog.json`。\n")
    L.append("## 一、如何使用（给发酵专家）\n")
    L.append("```bash")
    L.append("# 全文检索（多词 AND，返回 书|页码|原文）")
    L.append('python3 references/books/tools/search_books.py "Monod" --context 1')
    L.append('python3 references/books/tools/search_books.py "kLa" --word --max 20')
    L.append("# 各书命中统计（找哪本书讲得最多）")
    L.append('python3 references/books/tools/search_books.py "solid-state fermentation" --books')
    L.append("# 仅在某本书内检索")
    L.append('python3 references/books/tools/search_books.py "downstream" --book Distillation')
    L.append("# 命中页码后，按页读取原文")
    L.append('python3 references/books/tools/read_page.py Jorgensen 120')
    L.append('python3 references/books/tools/read_page.py Membrane_Distillation 45 50')
    L.append("```")
    L.append("- 检索到要点后，读取 `toc/<分区>/<书名>.md` 定位章节，再读取对应 `text/...txt` 的页码附近原文引用。")
    L.append("- 引用时注明：作者/编者、书名、出版社、年份、许可与页码。\n")
    L.append("## 二、主题标签索引\n")
    for tag in sorted(bytag):
        titles = "；".join(f"{e['title']}（{e['year']}）" for e in sorted(bytag[tag], key=lambda x: x["year"]))
        L.append(f"- **{tag}**：{titles}")
    L.append("")
    for sub, name in subs:
        items = [e for e in catalog if e["sub"] == sub]
        if not items:
            continue
        L.append(f"## {name}\n")
        L.append("| 书名 | 年 | 页 | 许可 | 全文 | 目录 | 来源 |")
        L.append("|---|---|---|---|---|---|---|")
        for e in sorted(items, key=lambda x: -x["year"]):
            toc = f"`toc/{e['sub']}/{e['file']}.md`"
            L.append(f"| {e['title']} | {e['year']} | {e['pages'] or '-'} | {e['license']} | `{e['text']}` | {toc} | {e['source']} |")
        L.append("")
    L.append("---")
    L.append("*由发酵专家维护；新增电子书请运行 `python3 tools/make_index.py` 重建索引并登记。*")
    with open(os.path.join(ROOT, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("INDEX.md 已生成")

if __name__ == "__main__":
    main()
