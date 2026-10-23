#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 raw/ 下的原始谱图统一清洗成标准 MSP 库 + index.json。

用法：
    python3 build_index.py --raw ../references/谱库-人参/raw --out ../references/谱库-人参/index
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from specmatch.io import load_spectra, save_msp                  # noqa: E402
from specmatch import filters as F                               # noqa: E402

EXTS = (".msp", ".mgf", ".json", ".csv")


def find_files(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                for n in sorted(names):
                    if n.lower().endswith(EXTS):
                        files.append(os.path.join(root, n))
        else:
            files.append(p)
    return files


def _count(spectra, fn):
    out = {}
    for s in spectra:
        v = fn(s)
        if v:
            out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def main():
    ap = argparse.ArgumentParser(description="构建统一谱库 index")
    ap.add_argument("--raw", nargs="+", required=True, help="原始谱图目录/文件")
    ap.add_argument("--out", default=".", help="输出目录")
    ap.add_argument("--min-peaks", type=int, default=5)
    ap.add_argument("--mz-from", type=float, default=10.0)
    ap.add_argument("--mz-to", type=float, default=2000.0)
    ap.add_argument("--n-max", type=int, default=500)
    ap.add_argument("--no-filter", action="store_true")
    args = ap.parse_args()

    files = find_files(args.raw)
    spectra = []
    for f in files:
        try:
            got = load_spectra(f)
            spectra.extend(got)
            print("  + %-50s %d 谱" % (os.path.basename(f), len(got)))
        except Exception as e:
            print("  ! %s: %s" % (f, e))
    print("载入谱：%d（来自 %d 个文件）" % (len(spectra), len(files)))

    if not args.no_filter:
        pipeline = F.default_filters(min_peaks=args.min_peaks, mz_from=args.mz_from,
                                     mz_to=args.mz_to, n_max=args.n_max)
        spectra = F.apply_to_all(spectra, pipeline)
        print("清洗后保留：%d" % len(spectra))

    os.makedirs(args.out, exist_ok=True)
    msp_path = os.path.join(args.out, "library.msp")
    save_msp(spectra, msp_path)

    index = {
        "n_spectra": len(spectra),
        "n_compounds": len({s.skeleton for s in spectra if s.skeleton}),
        "polarity": _count(spectra, lambda s: s.ionmode),
        "adducts": _count(spectra, lambda s: s.adduct),
        "sources": _count(spectra, lambda s: s.get("source")),
        "spectra": [{
            "id": s.get("id") or s.get("record"), "compound": s.compound_name,
            "inchikey": s.inchikey, "precursor_mz": s.precursor_mz,
            "ionmode": s.ionmode, "adduct": s.adduct,
            "collision_energy": s.collision_energy, "n_peaks": len(s),
        } for s in spectra],
    }
    with open(os.path.join(args.out, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print("库：%s（%d 谱 / %d 化合物）" % (msp_path, index["n_spectra"], index["n_compounds"]))
    print("索引：%s" % os.path.join(args.out, "index.json"))


if __name__ == "__main__":
    main()
