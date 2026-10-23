#!/usr/bin/env python3
"""
下载 MDPI 开放获取（CC BY）食品加工相关电子书全本 PDF。
- 书源清单: sources_mdpi.json（由编目流程维护）
- PDF 直链规律: https://mdpi-res.com/bookfiles/book/<id>/<url_title>.pdf
- 用法: python3 tools/fetch_mdpi.py [--only 9983,4926] [--jobs 4]
"""
import os, json, subprocess, argparse, concurrent.futures, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # books/
MANIFEST = os.path.join(ROOT, "sources_mdpi.json")
CDN = "https://mdpi-res.com/bookfiles/{kind}/{id}/{title}.pdf"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def fetch(entry, outdir):
    bid = entry["id"]
    url = CDN.format(kind=entry.get("kind", "book"), id=bid, title=entry["url_title"])
    dest = os.path.join(outdir, entry["file"] + ".pdf")
    if os.path.exists(dest) and os.path.getsize(dest) > 100000:
        return (bid, "skip", os.path.getsize(dest))
    tmp = dest + ".part"
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "600", "-A", UA, "-o", tmp,
         "-w", "%{http_code} %{content_type} %{size_download}", url],
        capture_output=True, text=True)
    code, ctype, size = (r.stdout.strip().split() + ["", "", ""])[:3]
    if code == "200" and "pdf" in ctype:
        os.replace(tmp, dest)
        return (bid, "ok", int(size))
    if os.path.exists(tmp):
        os.remove(tmp)
    return (bid, "fail", f"{code} {ctype}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    entries = json.load(open(MANIFEST, encoding="utf-8"))
    if a.only:
        ids = set(a.only.split(","))
        entries = [e for e in entries if str(e["id"]) in ids]
    outdir = os.path.join(ROOT, "mdpi")
    os.makedirs(outdir, exist_ok=True)
    ok = fail = skip = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(fetch, e, outdir): e for e in entries}
        for f in concurrent.futures.as_completed(futs):
            e = futs[f]
            bid, st, info = f.result()
            if st == "ok":
                ok += 1
            elif st == "skip":
                skip += 1
            else:
                fail += 1
            print(f"[{st}] {bid} {e['file']} :: {info}", flush=True)
    print(f"\n完成: ok={ok} skip={skip} fail={fail} / 共 {len(entries)}")


if __name__ == "__main__":
    main()
