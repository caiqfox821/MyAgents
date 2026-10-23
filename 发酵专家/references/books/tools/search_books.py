#!/usr/bin/env python3
"""
发酵电子书库全文检索工具
用法:
  python3 search_books.py "query" [更多词 ...] [--context 2] [--max 40] [--book 关键词]
  python3 search_books.py --list                 # 列出全部书目与文本路径
  python3 search_books.py --books "monod kLa"    # 仅统计各书命中数

说明:
  - 在 books/text/**/*.txt 上做不区分大小写的检索，支持多词 AND。
  - 输出 "书名 | 第N页 | 行内容"，第N页由分页符(\f)计数得到。
"""
import os, re, sys, argparse, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # books/
TEXTGLOB = os.path.join(ROOT, "text", "**", "*.txt")

def load(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def books():
    return sorted(glob.glob(TEXTGLOB, recursive=True))

def page_of(text, pos):
    return text.count("\f", 0, pos) + 1

def search(terms, context=0, maxhits=40, bookfilter=None, countonly=False, word=False):
    import re as _re
    terms_l = [t.lower() for t in terms]
    pats = [(_re.compile(r"\b" + _re.escape(t) + r"\b") if word else None) for t in terms_l]
    hits = []
    per_book = []
    for p in books():
        rel = os.path.relpath(p, ROOT)
        if bookfilter and bookfilter.lower() not in rel.lower():
            continue
        text = load(p)
        lines = text.split("\n")
        offs = []
        acc = 0
        for ln in lines:
            offs.append(acc); acc += len(ln) + 1
        c = 0
        for i, ln in enumerate(lines):
            l = ln.lower()
            if all((pats[k].search(l) if word else terms_l[k] in l) for k in range(len(terms_l))):
                c += 1
                if not countonly and len(hits) < maxhits:
                    pg = page_of(text, offs[i])
                    ctx = [lines[j].strip() for j in range(max(0, i-context), min(len(lines), i+context+1))]
                    hits.append((rel, pg, ln.strip(), ctx))
        if c:
            per_book.append((rel, c))
    return hits, per_book

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("terms", nargs="*")
    ap.add_argument("--context", type=int, default=0)
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--book", default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--books", action="store_true", help="仅输出各书命中统计")
    ap.add_argument("--word", action="store_true", help="整词匹配(正则\\b)")
    a = ap.parse_args()

    if a.list:
        print(f"文本文件（{len(books())}）:")
        for p in books():
            print(" ", os.path.relpath(p, ROOT))
        return
    if not a.terms:
        ap.print_help(); return

    hits, per_book = search(a.terms, a.context, a.max, a.book, countonly=a.books, word=a.word)
    term_s = " AND ".join(a.terms)
    if a.books:
        for rel, c in sorted(per_book, key=lambda x: -x[1]):
            print(f"{c:6d}  {rel}")
        return
    print(f"# 检索: {term_s}  (命中 {len(per_book)} 本 / 展示前 {len(hits)} 条)\n")
    cur = None
    for rel, pg, ln, ctx in hits:
        if rel != cur:
            print(f"\n=== {rel} ===")
            cur = rel
        print(f"  [p{pg}] {ln[:160]}")
        for c in ctx:
            if c and c != ln:
                print(f"        {c[:160]}")

if __name__ == "__main__":
    main()
