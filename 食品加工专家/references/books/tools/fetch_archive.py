#!/usr/bin/env python3
"""
下载 Archive.org 公共领域（Public Domain）食品加工历史经典 PDF。
- 清单: sources_public_domain.json
- 直链: https://archive.org/download/<id>/<id>.pdf
- 用法: python3 tools/fetch_archive.py [--only id1,id2]
"""
import os, json, subprocess, argparse, concurrent.futures

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # books/
MANIFEST = os.path.join(ROOT, "sources_public_domain.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def fetch(entry, outdir):
    ident = entry["id"]
    url = f"https://archive.org/download/{ident}/{ident}.pdf"
    dest = os.path.join(outdir, entry["file"] + ".pdf")
    if os.path.exists(dest) and os.path.getsize(dest) > 50000:
        return (ident, "skip", os.path.getsize(dest))
    tmp = dest + ".part"
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "600", "-A", UA, "-o", tmp,
         "-w", "%{http_code} %{content_type} %{size_download}", url],
        capture_output=True, text=True)
    code, ctype, size = (r.stdout.strip().split() + ["", "", ""])[:3]
    if code == "200" and "pdf" in ctype and os.path.getsize(tmp) > 50000:
        os.replace(tmp, dest)
        return (ident, "ok", int(size))
    if os.path.exists(tmp):
        os.remove(tmp)
    return (ident, "fail", f"{code} {ctype}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    entries = json.load(open(MANIFEST, encoding="utf-8"))
    if a.only:
        ids = set(a.only.split(","))
        entries = [e for e in entries if e["id"] in ids]
    outdir = os.path.join(ROOT, "public_domain")
    os.makedirs(outdir, exist_ok=True)
    ok = fail = skip = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(fetch, e, outdir): e for e in entries}
        for f in concurrent.futures.as_completed(futs):
            e = futs[f]
            ident, st, info = f.result()
            if st == "ok":
                ok += 1
            elif st == "skip":
                skip += 1
            else:
                fail += 1
            print(f"[{st}] {ident} {e['file']} :: {info}", flush=True)
    print(f"\n完成: ok={ok} skip={skip} fail={fail} / 共 {len(entries)}")


if __name__ == "__main__":
    main()
