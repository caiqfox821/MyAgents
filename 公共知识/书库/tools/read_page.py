#!/usr/bin/env python3
"""
按页读取某本电子书的原文（配合 search_books.py 定位页码后使用）。
用法:
  python3 read_page.py <书名关键词> <起始页> [结束页]
  python3 read_page.py Jorgensen 120
  python3 read_page.py Membrane_Distillation 45 50
说明: 以分页符(\f)切页; 输出 "第N页" 标记。可用 --grep 词 仅打印命中页附近。
"""
import os, re, sys, glob, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def find_books(key):
    hits = []
    for p in sorted(glob.glob(os.path.join(ROOT, "text", "**", "*.txt"), recursive=True)):
        if key.lower() in os.path.relpath(p, ROOT).lower():
            hits.append(p)
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key")
    ap.add_argument("start", type=int)
    ap.add_argument("end", type=int, nargs="?")
    a = ap.parse_args()
    end = a.end or a.start
    books = find_books(a.key)
    if not books:
        print("未找到匹配书:", a.key); sys.exit(1)
    if len(books) > 1:
        print("匹配到多本，请用更精确关键词：")
        for b in books:
            print("  ", os.path.relpath(b, ROOT))
        sys.exit(2)
    path = books[0]
    with open(path, encoding="utf-8", errors="ignore") as f:
        pages = f.read().split("\f")
    print(f"# {os.path.relpath(path, ROOT)} （共 {len(pages)} 页）")
    for i in range(a.start - 1, min(end, len(pages))):
        print(f"\n========== 第 {i+1} 页 ==========")
        print(re.sub(r"\n{3,}", "\n\n", pages[i].strip()))

if __name__ == "__main__":
    main()
