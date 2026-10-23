#!/usr/bin/env python3
"""
营养专家 OA 书库构建器（MDPI Books / WHO / FAO / 其他）。
- 支持 MDPI（由 reprint id 拼 mdpi-res CDN 直链，多 slug/kind 变体重试）
- 支持通用 pdf_url（WHO IRIS bitstream / FAO / 其他），带完整性校验与断点续传重试
- 抽取全文（pdftotext -layout）、自动目录、生成 catalog.json / INDEX.md / toc/

用法:
  python3 tools/build_booklib.py . sources_mdpi.json sources_who.json sources_fao.json
  python3 tools/build_booklib.py . sources_mdpi.json --no-download
"""
import os, re, sys, json, glob, argparse, subprocess, concurrent.futures

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
CDN_MDPI = "https://mdpi-res.com/bookfiles/{kind}/{id}/{slug}.pdf"


def slug_variants(title):
    v = []
    for keep in (True, False):
        s = re.sub(r"[^A-Za-z0-9.]+" if keep else r"[^A-Za-z0-9]+", "_", title)
        s = re.sub(r"_+", "_", s).strip("_")
        if s and s not in v:
            v.append(s)
    # MDPI 真实规则：连字符/破折号/斜杠等标点**直接删除**，仅空白转下划线
    # 实证：Chromatography–Mass Spectrometry… → ChromatographyMass_Spectrometry_…（topic/13221）
    #       State-of-the-Art… → StateoftheArt_Environmental_Chemicals…（book/9932）
    d = re.sub(r"\s+", "_", title.strip())
    d = re.sub(r"[^A-Za-z0-9_]", "", d)
    d = re.sub(r"_+", "_", d).strip("_")
    if d and d not in v:
        v.insert(0, d)
    a = re.sub(r"[^A-Za-z0-9]+", "", title)
    if a and a not in v:
        v.append(a)
    # MDPI 常去掉虚词（the/and/of/in/on/for/with/to/a/at）
    STOP = r"the|and|of|in|on|for|with|to|a|at|an"
    base = re.sub(r"[^A-Za-z0-9]+", "_", title)
    base = re.sub(r"_+", "_", base).strip("_")
    sw = re.sub(rf"(?i)(?<=_)({STOP})(?=_|$)", "", base)
    sw = re.sub(r"_+", "_", sw).strip("_")
    if sw and sw not in v:
        v.append(sw)
    return v


def stem(e):
    return e.get("file") or (slug_variants(e["title"])[0] + (f"_{e['year']}" if e.get("year") else ""))


def valid_pdf(path):
    if not os.path.exists(path) or os.path.getsize(path) < 50000:
        return False
    try:
        with open(path, "rb") as f:
            f.seek(-4096, 2)
            tail = f.read()
        if b"%%EOF" not in tail:
            return False
    except Exception:
        return False
    r = subprocess.run(["pdfinfo", path], capture_output=True, text=True)
    return r.returncode == 0 and bool(re.search(r"Pages:\s+[1-9]", r.stdout))


def urls_for(e):
    urls = []
    if e.get("pdf_url"):
        urls.append(e["pdf_url"])
    if e.get("id") and ("MDPI" in (e.get("publisher") or "") or e.get("sub") == "mdpi"):
        slugs = [e["slug"]] if e.get("slug") else ([e["url_title"]] if e.get("url_title") else []) + slug_variants(e["title"])
        kinds = [e["kind"]] if e.get("kind") else ["book", "reprint", "topic"]
        for s in slugs:
            for k in kinds:
                urls.append(CDN_MDPI.format(kind=k, id=e["id"], slug=s))
    return urls


def download(e, root):
    sub = e.get("sub", "mdpi")
    out = os.path.join(root, sub)
    os.makedirs(out, exist_ok=True)
    dest = os.path.join(out, stem(e) + ".pdf")
    if valid_pdf(dest):
        return dest, "skip"
    if os.path.exists(dest):
        os.remove(dest)
    for url in urls_for(e):
        part = dest + ".part"
        ok = False
        for _ in range(3):
            subprocess.run(["curl", "-sL", "--http1.1", "-C", "-", "--noproxy", "*",
                            "--max-time", "300",
                            "-A", UA, "-o", part, "-w", "%{http_code}", url],
                           capture_output=True, text=True)
            if valid_pdf(part):
                ok = True
                break
        if ok:
            os.replace(part, dest)
            return dest, "ok"
        if os.path.exists(part):
            os.remove(part)
    return dest, "fail"


def extract(pdf, txt):
    if os.path.exists(txt) and os.path.getsize(txt) > 1000:
        return True
    os.makedirs(os.path.dirname(txt), exist_ok=True)
    try:
        subprocess.run(["pdftotext", "-layout", pdf, txt], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return os.path.exists(txt) and os.path.getsize(txt) > 1000
    except Exception:
        return False


def pages(pdf):
    try:
        o = subprocess.check_output(["pdfinfo", pdf], stderr=subprocess.DEVNULL, text=True)
        m = re.search(r"^Pages:\s+(\d+)", o, re.M)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def toc_of(t):
    L = t.split("\n")
    for i, ln in enumerate(L[:6000]):
        if re.match(r"^\s*(Contents|Table of Contents|CONTENTS)\s*$", ln):
            return [b.rstrip() for b in L[i + 1:i + 90] if b.strip()][:70], "Contents"
    ch = [x.strip() for x in L if re.match(r"^\s*(CHAPTER|Chapter)\s+[IVXLC0-9]", x)][:50]
    if ch:
        return ch, "Chapters"
    num = [x.strip() for x in L if re.match(r"^\s*\d+(\.\d+){0,2}\s+[A-Z][A-Za-z]", x) and len(x.strip()) < 90][:50]
    if num:
        return num, "Sections"
    return [], "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("books_dir")
    ap.add_argument("manifests", nargs="+")
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    root = os.path.abspath(a.books_dir)
    entries = []
    for mf in a.manifests:
        entries += json.load(open(mf, encoding="utf-8"))
    print(f"清单合计 {len(entries)} 册")

    if not a.no_download:
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
            fs = {ex.submit(download, e, root): e for e in entries}
            for f in concurrent.futures.as_completed(fs):
                e = fs[f]
                dest, st = f.result()
                print(f"[{st}] {stem(e)}", flush=True)

    cat = []
    for e in entries:
        s = stem(e)
        sub = e.get("sub", "mdpi")
        pdf = os.path.join(root, sub, s + ".pdf")
        txt = os.path.join(root, "text", sub, s + ".txt")
        if not valid_pdf(pdf):
            print("WARN 无效/缺 PDF:", s)
            continue
        if not extract(pdf, txt):
            print("WARN 抽取失败:", s)
            continue
        text = open(txt, encoding="utf-8", errors="ignore").read()
        tl, tk = toc_of(text)
        cat.append({"file": s, "sub": sub, "title": e["title"], "year": e.get("year"),
                    "publisher": e.get("publisher", ""), "license": e.get("license", "OA"),
                    "source": e.get("source", ""), "tags": e.get("tags", []),
                    "pages": pages(pdf), "pdf": os.path.relpath(pdf, root),
                    "text": os.path.relpath(txt, root), "toc": tl, "toc_kind": tk,
                    "text_chars": len(text)})
        td = os.path.join(root, "toc", sub)
        os.makedirs(td, exist_ok=True)
        with open(os.path.join(td, s + ".md"), "w", encoding="utf-8") as f:
            f.write(f"# {e['title']} ({e.get('year') or 'n.d.'}, {e.get('publisher','')})\n\n"
                    f"- 许可: {e.get('license','OA')}\n- 来源: {e.get('source','')}\n"
                    f"- 页数: {cat[-1]['pages']}\n- 全文: `{cat[-1]['text']}`\n"
                    f"- 标签: {', '.join(e.get('tags',[]))}\n\n## 目录 ({tk})\n\n")
            f.write("\n".join(f"- {l}" for l in tl) if tl else "（自动目录提取失败，请用全文检索工具）")
            f.write("\n")

    json.dump(cat, open(os.path.join(root, "catalog.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    from collections import defaultdict
    bt = defaultdict(list)
    for e in cat:
        for t in e["tags"]:
            bt[t].append(e)
    nm = {"mdpi": "MDPI Books（CC BY 4.0）",
          "who": "WHO 指南/报告（开放获取）",
          "fao": "FAO / Codex 出版物（开放获取）",
          "efsa": "EFSA 指南与科学意见（开放获取）",
          "guides": "其他权威机构指南（WHO/FAO/EFSA/EPA/IPCS/ICH/EC/OECD）",
          "public_domain": "公共领域 / 历史经典"}
    L = [f"# 公共知识书库 · 全文索引（风险评估 / 毒理 / 质谱）\n",
         f"> 共 **{len(cat)} 册/篇**，均为合法开放获取（MDPI CC BY / WHO·FAO·EFSA 开放获取 / 公共领域）。\n",
         "## 一、如何使用（各专家通用）\n", "```bash",
         'python3 公共知识/书库/tools/search_books.py "benchmark dose" --context 1',
         'python3 公共知识/书库/tools/search_books.py "MRM" --books',
         'python3 公共知识/书库/tools/read_page.py Mass_Spectrometry 60',
         "```",
         "- 引用注明 编者、书名/机构、出版社、年份、许可与页码（书库物理页码）。\n",
         "## 二、主题标签索引\n"]
    for t in sorted(bt):
        L.append(f"- **{t}**：" + "；".join(
            f"{x['title']}（{x['year'] or 'n.d.'}）" for x in sorted(bt[t], key=lambda y: -(y["year"] or 0))))
    L.append("")
    for sub in sorted({e["sub"] for e in cat}):
        L.append(f"## {nm.get(sub, sub)}\n")
        L.append("| 书名 | 年 | 页 | 许可 | 全文 | 目录 | 来源 |")
        L.append("|---|---|---|---|---|---|---|")
        for e in sorted([x for x in cat if x["sub"] == sub], key=lambda x: -(x["year"] or 0)):
            L.append(f"| {e['title']} | {e['year'] or '-'} | {e['pages'] or '-'} | {e['license']} | "
                     f"`{e['text']}` | `toc/{e['sub']}/{e['file']}.md` | {e['source']} |")
        L.append("")
    L.append("---\n*新增电子书后运行 `python3 tools/build_booklib.py . <manifest...>` 重建。*")
    open(os.path.join(root, "INDEX.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"完成: catalog {len(cat)} 条")


if __name__ == "__main__":
    main()
