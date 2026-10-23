#!/usr/bin/env python3
"""
下载 FAO 开放获取食品加工出版物 PDF（FAO 文档库，多数为 CC BY-NC-SA / 免费使用）。
- 清单: sources_fao.json
- 直链: https://www.fao.org/3/<doc_id>/<doc_id>.pdf
- 用法: python3 tools/fetch_fao.py [--only id1,id2] [--jobs 4]
"""
import os, json, subprocess, argparse, concurrent.futures

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # books/
MANIFEST = os.path.join(ROOT, "sources_fao.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def fetch(entry, outdir):
    did = entry["doc_id"]
    url = f"https://www.fao.org/3/{did}/{did}.pdf"
    dest = os.path.join(outdir, entry["file"] + ".pdf")
    if os.path.exists(dest) and os.path.getsize(dest) > 50000:
        return (did, "skip", os.path.getsize(dest))
    tmp = dest + ".part"
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "900", "--retry", "2", "--retry-delay", "3",
         "-A", UA, "-o", tmp, "-w", "%{http_code} %{content_type} %{size_download}", url],
        capture_output=True, text=True)
    code, ctype, size = (r.stdout.strip().split() + ["", "", ""])[:3]
    if code in ("200", "206") and "pdf" in ctype and os.path.getsize(tmp) > 50000:
        # 校验为完整 PDF（尾部含 %%EOF）
        with open(tmp, "rb") as f:
            f.seek(max(0, os.path.getsize(tmp) - 2048))
            tail = f.read()
        if b"%%EOF" in tail:
            os.replace(tmp, dest)
            return (did, "ok", int(size))
    if os.path.exists(tmp):
        os.remove(tmp)
    return (did, "fail", f"{code} {ctype} {size}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    entries = json.load(open(MANIFEST, encoding="utf-8"))
    if a.only:
        ids = set(a.only.split(","))
        entries = [e for e in entries if e["doc_id"] in ids]
    outdir = os.path.join(ROOT, "fao")
    os.makedirs(outdir, exist_ok=True)
    ok = fail = skip = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(fetch, e, outdir): e for e in entries}
        for f in concurrent.futures.as_completed(futs):
            e = futs[f]
            did, st, info = f.result()
            if st == "ok":
                ok += 1
            elif st == "skip":
                skip += 1
            else:
                fail += 1
            print(f"[{st}] {did} {e['file']} :: {info}", flush=True)
    print(f"\n完成: ok={ok} skip={skip} fail={fail} / 共 {len(entries)}")


if __name__ == "__main__":
    main()
