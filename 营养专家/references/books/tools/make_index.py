#!/usr/bin/env python3
"""
生成食品加工电子书库编目: catalog.json、INDEX.md、toc/<sub>/<book>.md
数据来源: sources_mdpi.json（MDPI OA）+ sources_public_domain.json（Archive.org 公共领域）
用法: python3 tools/make_index.py
"""
import os, re, json, subprocess, glob
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # books/
TEXT = os.path.join(ROOT, "text")

FIX = {
    "AgroFood": "Agro-Food", "CerealBased": "Cereal-Based", "FoodGrade": "Food-Grade",
    "UltrasoundAssisted": "Ultrasound-Assisted", "DataDriven": "Data-Driven",
    "HydrogelDerived": "Hydrogel-Derived", "NonThermal": "Non-Thermal",
    "emFermentationem": "Fermentation", "emProcessesem": "Processes",
    "emCosmeticsem": "Cosmetics",
}


def pretty(t):
    for a, b in FIX.items():
        t = t.replace(a, b)
    return t


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
        if re.match(r"^\s*(Contents|Table of Contents)\s*$", ln, re.I):
            block = [l.rstrip() for l in lines[i + 1:i + 90]]
            out = [b for b in block if b.strip()][:70]
            if out:
                return out, "Contents"
    ch = [ln.strip() for ln in lines if re.match(r"^\s*(CHAPTER|Chapter)\s+[IVXLC0-9]", ln)][:50]
    if ch:
        return ch, "Chapters"
    num = [ln.strip() for ln in lines if re.match(r"^\s*\d+(\.\d+){0,2}\s+[A-Z][A-Za-z]", ln) and len(ln.strip()) < 90][:50]
    if num:
        return num, "Sections"
    return [], "none"


def load_entries():
    entries = []
    mp = os.path.join(ROOT, "sources_mdpi.json")
    if os.path.exists(mp):
        for e in json.load(open(mp, encoding="utf-8")):
            entries.append({
                "file": e["file"], "sub": "mdpi", "title": pretty(e["url_title"].replace("_", " ")),
                "year": e.get("year"), "publisher": "MDPI", "license": "CC BY 4.0",
                "source": ("https://doi.org/" + e["doi"]) if e.get("doi") else "https://www.mdpi.com/books",
                "tags": e.get("tags", []), "pdf_isbn": e.get("pdf_isbn"), "doi": e.get("doi"),
            })
    pp = os.path.join(ROOT, "sources_public_domain.json")
    if os.path.exists(pp):
        for e in json.load(open(pp, encoding="utf-8")):
            entries.append({
                "file": e["file"], "sub": "public_domain", "title": e["title"], "year": e.get("year"),
                "publisher": "Archive.org", "license": "Public Domain",
                "source": f"https://archive.org/details/{e['id']}", "tags": e.get("tags", []),
                "author": e.get("author"),
            })
    fp = os.path.join(ROOT, "sources_fao.json")
    if os.path.exists(fp):
        for e in json.load(open(fp, encoding="utf-8")):
            entries.append({
                "file": e["file"], "sub": "fao", "title": e["title"], "year": e.get("year"),
                "publisher": "FAO", "license": "© FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO）",
                "source": f"https://www.fao.org/3/{e['doc_id']}/{e['doc_id']}.pdf", "tags": e.get("tags", []),
            })
    return entries


def main():
    catalog = []
    for e in load_entries():
        sub, stem = e["sub"], e["file"]
        pdf = os.path.join(ROOT, sub, stem + ".pdf")
        txt = os.path.join(TEXT, sub, stem + ".txt")
        e["pages"] = pages(pdf) if os.path.exists(pdf) else None
        e["pdf"] = os.path.relpath(pdf, ROOT) if os.path.exists(pdf) else None
        e["text"] = os.path.relpath(txt, ROOT) if os.path.exists(txt) else None
        if os.path.exists(txt):
            text = open(txt, encoding="utf-8", errors="ignore").read()
            tl, tk = toc_of(text)
        else:
            tl, tk = [], "none"
        e["toc"], e["toc_kind"] = tl, tk
        catalog.append(e)
        tocdir = os.path.join(ROOT, "toc", sub)
        os.makedirs(tocdir, exist_ok=True)
        with open(os.path.join(tocdir, stem + ".md"), "w", encoding="utf-8") as f:
            f.write(f"# {e['title']} ({e.get('year') or 'n.d.'}, {e['publisher']})\n\n")
            if e.get("author"):
                f.write(f"- 作者: {e['author']}\n")
            f.write(f"- 许可: {e['license']}\n- 来源: {e['source']}\n- 页数: {e['pages']}\n"
                    f"- 全文: `{e['text']}`\n- PDF: `{e['pdf']}`\n- 标签: {', '.join(e['tags'])}\n\n## 目录 ({tk})\n\n")
            f.write("\n".join(f"- {l}" for l in tl) if tl else "（自动目录提取失败，请用全文检索工具搜索）")
            f.write("\n")

    with open(os.path.join(ROOT, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"catalog.json 写入 {len(catalog)} 条")

    bytag = defaultdict(list)
    for e in catalog:
        for t in e["tags"]:
            bytag[t].append(e)

    L = []
    L.append("# 食品加工电子书库 · 全文索引（INDEX）\n")
    L.append(f"> 共 **{len(catalog)} 册/篇**，均为合法开放获取（MDPI CC BY / FAO 开放获取 / Archive.org 公共领域）。")
    L.append("> PDF 存于 `mdpi/`、`fao/`、`public_domain/`；**全文文本**在 `text/<分区>/<书名>.txt`；**目录**在 `toc/<分区>/<书名>.md`；结构化元数据 `catalog.json`。\n")
    L.append("## 一、如何使用（给食品加工专家）\n")
    L.append("```bash")
    L.append("# 全文检索（多词 AND，返回 书|页码|原文）")
    L.append('python3 references/books/tools/search_books.py "spray drying" --context 1')
    L.append('python3 references/books/tools/search_books.py "high pressure processing" --word --max 20')
    L.append("# 各书命中统计（找哪本书讲得最多）")
    L.append('python3 references/books/tools/search_books.py "encapsulation" --books')
    L.append("# 仅在某本书内检索")
    L.append('python3 references/books/tools/search_books.py "extrusion" --book Grain_Processing')
    L.append("# 命中页码后，按页读取原文")
    L.append('python3 references/books/tools/read_page.py Food_Gels 120')
    L.append('python3 references/books/tools/read_page.py Plant_Protein 45 60')
    L.append("```")
    L.append("- 检索到要点后，读取 `toc/<分区>/<书名>.md` 定位章节，再读取对应 `text/...txt` 的页码附近原文引用。")
    L.append("- 引用时注明：书/章标题、编者或作者、出版社、年份、许可与页码。\n")
    L.append("## 二、主题标签索引\n")
    for tag in sorted(bytag):
        titles = "；".join(f"{e['title']}（{e.get('year') or 'n.d.'}）" for e in sorted(bytag[tag], key=lambda x: -(x.get("year") or 0)))
        L.append(f"- **{tag}**：{titles}")
    L.append("")
    subs = [("mdpi", "MDPI Books（CC BY，可自由再分发）"),
            ("fao", "FAO 出版物（开放获取，多为 CC BY-NC-SA 3.0 IGO）"),
            ("public_domain", "公共领域 / 历史经典（Archive.org）")]
    for sub, name in subs:
        items = [e for e in catalog if e["sub"] == sub]
        if not items:
            continue
        L.append(f"## {name}\n")
        L.append("| 书名 | 年 | 页 | 许可 | 全文 | 目录 | 来源 |")
        L.append("|---|---|---|---|---|---|---|")
        for e in sorted(items, key=lambda x: -(x.get("year") or 0)):
            L.append(f"| {e['title']} | {e.get('year') or '-'} | {e['pages'] or '-'} | {e['license']} | "
                     f"`{e['text'] or '-'}` | `toc/{e['sub']}/{e['file']}.md` | {e['source']} |")
        L.append("")
    L.append("---")
    L.append("*由食品加工专家维护；新增电子书请更新 `sources_*.json` 后运行 `python3 tools/make_index.py` 重建索引。*")
    with open(os.path.join(ROOT, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("INDEX.md 已生成")


if __name__ == "__main__":
    main()
