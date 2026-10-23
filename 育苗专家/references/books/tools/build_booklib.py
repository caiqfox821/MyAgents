#!/usr/bin/env python3
"""通用 OA 电子书库构建器 (MDPI Books 为主)。见 books/README.md。"""
import os, re, sys, json, glob, argparse, subprocess, concurrent.futures
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
CDN_MDPI = "https://mdpi-res.com/bookfiles/{kind}/{id}/{slug}.pdf"
def slug_variants(title):
    v=[]
    for keep in (True,False):
        s=re.sub(r"[^A-Za-z0-9.]+" if keep else r"[^A-Za-z0-9]+","_",title)
        s=re.sub(r"_+","_",s).strip("_")
        if s not in v: v.append(s)
    a=re.sub(r"[^A-Za-z0-9]+","",title)
    if a not in v: v.append(a)
    return v
def stem(e): return e.get("file") or (slug_variants(e["title"])[0]+f"_{e['year']}")
def download(e,root):
    sub=e.get("sub","mdpi"); out=os.path.join(root,sub); os.makedirs(out,exist_ok=True)
    dest=os.path.join(out,stem(e)+".pdf")
    if os.path.exists(dest) and os.path.getsize(dest)>50000: return dest,"skip"
    urls=[]
    if e.get("pdf_url"): urls.append(e["pdf_url"])
    if e.get("id") and "MDPI" in e.get("publisher",""):
        slugs=[e["slug"]] if e.get("slug") else slug_variants(e["title"])
        kinds=[e["kind"]] if e.get("kind") else ["book","reprint","topic"]
        for s in slugs:
            for k in kinds:
                urls.append(CDN_MDPI.format(kind=k,id=e["id"],slug=s))
    for url in urls:
        tmp=dest+".part"
        r=subprocess.run(["curl","-sL","--max-time","600","-A",UA,"-o",tmp,"-w","%{http_code} %{content_type} %{size_download}",url],capture_output=True,text=True)
        code,ct,sz=(r.stdout.strip().split()+["","",""])[:3]
        if code=="200" and "pdf" in ct.lower():
            os.replace(tmp,dest); return dest,"ok"
        if os.path.exists(tmp): os.remove(tmp)
    return dest,"fail"
def extract(pdf,txt):
    if os.path.exists(txt) and os.path.getsize(txt)>1000: return True
    os.makedirs(os.path.dirname(txt),exist_ok=True)
    try:
        subprocess.run(["pdftotext","-layout",pdf,txt],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return os.path.exists(txt) and os.path.getsize(txt)>1000
    except Exception: return False
def pages(pdf):
    try:
        o=subprocess.check_output(["pdfinfo",pdf],stderr=subprocess.DEVNULL,text=True)
        m=re.search(r"^Pages:\s+(\d+)",o,re.M); return int(m.group(1)) if m else None
    except Exception: return None
def toc_of(t):
    L=t.split("\n")
    for i,ln in enumerate(L[:6000]):
        if re.match(r"^\s*(Contents|Table of Contents|CONTENTS)\s*$",ln):
            return [b.rstrip() for b in L[i+1:i+90] if b.strip()][:70],"Contents"
    ch=[x.strip() for x in L if re.match(r"^\s*(CHAPTER|Chapter)\s+[IVXLC0-9]",x)][:50]
    if ch: return ch,"Chapters"
    return [],"none"
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("books_dir"); ap.add_argument("manifest")
    ap.add_argument("--no-download",action="store_true"); ap.add_argument("--jobs",type=int,default=4)
    a=ap.parse_args(); root=os.path.abspath(a.books_dir)
    entries=json.load(open(a.manifest,encoding="utf-8"))
    if not a.no_download:
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
            fs={ex.submit(download,e,root):e for e in entries}
            for f in concurrent.futures.as_completed(fs):
                e=fs[f]; dest,st=f.result(); print(f"[{st}] {stem(e)}",flush=True)
    cat=[]
    for e in entries:
        s=stem(e); sub=e.get("sub","mdpi")
        pdf=os.path.join(root,sub,s+".pdf"); txt=os.path.join(root,"text",sub,s+".txt")
        if not os.path.exists(pdf): print("WARN 缺 PDF:",s); continue
        if not extract(pdf,txt): print("WARN 抽取失败:",s); continue
        text=open(txt,encoding="utf-8",errors="ignore").read(); tl,tk=toc_of(text)
        cat.append({"file":s,"sub":sub,"title":e["title"],"year":e["year"],"publisher":e.get("publisher",""),
            "license":e.get("license","OA"),"source":e.get("source",""),"tags":e.get("tags",[]),
            "pages":pages(pdf),"pdf":os.path.relpath(pdf,root),"text":os.path.relpath(txt,root),
            "toc":tl,"toc_kind":tk,"text_chars":len(text)})
        td=os.path.join(root,"toc",sub); os.makedirs(td,exist_ok=True)
        with open(os.path.join(td,s+".md"),"w",encoding="utf-8") as f:
            f.write(f"# {e['title']} ({e['year']}, {e.get('publisher','')})\n\n- 许可: {e.get('license','OA')}\n- 来源: {e.get('source','')}\n- 页数: {cat[-1]['pages']}\n- 全文: `{cat[-1]['text']}`\n- 标签: {', '.join(e.get('tags',[]))}\n\n## 目录 ({tk})\n\n")
            f.write("\n".join(f"- {l}" for l in tl) if tl else "（自动目录提取失败，请用全文检索工具）"); f.write("\n")
    json.dump(cat,open(os.path.join(root,"catalog.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    from collections import defaultdict
    bt=defaultdict(list)
    for e in cat:
        for t in e["tags"]: bt[t].append(e)
    nm={"mdpi":"MDPI Books（CC BY）","fao":"FAO 出版物（开放获取）","other":"其他开放获取"}
    L=[f"# 育苗电子书库 · 全文索引（INDEX）\n",f"> 共 **{len(cat)} 册**，合法开放获取（CC BY / OA）。\n",
       "## 一、如何使用（给育苗专家）\n","```bash",
       'python3 references/books/tools/search_books.py "germination" --context 1',
       'python3 references/books/tools/search_books.py "micropropagation" --books',
       'python3 references/books/tools/read_page.py Seed_Germination 45',
       "```","- 引用注明 编者、书名、出版社、年份、页码。\n","## 二、主题标签索引\n"]
    for t in sorted(bt):
        L.append(f"- **{t}**：" + "；".join(f"{e['title']}（{e['year']}）" for e in sorted(bt[t],key=lambda x:x["year"])))
    L.append("")
    for sub in sorted({e["sub"] for e in cat}):
        L.append(f"## {nm.get(sub,sub)}\n"); L.append("| 书名 | 年 | 页 | 全文 | 目录 | 来源 |"); L.append("|---|---|---|---|---|---|")
        for e in sorted([x for x in cat if x["sub"]==sub],key=lambda x:-x["year"]):
            L.append(f"| {e['title']} | {e['year']} | {e['pages'] or '-'} | `{e['text']}` | `toc/{e['sub']}/{e['file']}.md` | {e['source']} |")
        L.append("")
    L.append("---\n*新增电子书后运行 `python3 tools/build_booklib.py . <manifest>` 重建。*")
    open(os.path.join(root,"INDEX.md"),"w",encoding="utf-8").write("\n".join(L)+"\n")
    print(f"完成: catalog {len(cat)} 条")
if __name__=="__main__": main()
