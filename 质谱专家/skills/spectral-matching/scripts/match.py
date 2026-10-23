#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一张（或多张）查询谱与本地库比对，输出 Top-N 命中 + 分数 + Schymanski 置信度级。

用法示例：
    # ESI MS2：熵相似度
    python3 match.py --query q.mgf --library library.msp --method entropy --mz-tol 0.02
    # GC-EI：匹配因子
    python3 match.py --query gc.msp --library ei_lib.msp --method match_factor --mz-tol 0.5
    # 查看可用后端
    python3 match.py --caps
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from specmatch.io import load_spectra                     # noqa: E402
from specmatch.search import SpectralLibrary              # noqa: E402
from specmatch import report as R                         # noqa: E402
from specmatch.backends import capabilities, matchms_available, make_matchms_scorer  # noqa: E402


def print_tsv(query, results):
    header, rows = R.rank_table(query, results)
    print("\t".join(header))
    for row in rows:
        print("\t".join("" if c is None else str(c) for c in row))


def main():
    ap = argparse.ArgumentParser(description="本地谱库比对")
    ap.add_argument("--query", help="查询谱（msp/mgf/csv/json，可含多张）")
    ap.add_argument("--library", help="参考库（msp/mgf/json）")
    ap.add_argument("--method", default="entropy",
                    help="打分器，逗号分隔：entropy,cosine_greedy,modified_cosine,"
                         "weighted_cosine,match_factor,neutral_losses,intersect_mz")
    ap.add_argument("--mz-tol", type=float, default=0.02, help="峰匹配容差 Da（EI 用 0.3–0.5）")
    ap.add_argument("--precursor-ppm", type=float, default=20.0, help="前体过滤 ppm（0=不过滤）")
    ap.add_argument("--adduct", default=None, help="限定加合物，如 [M-H]-")
    ap.add_argument("--no-polarity", action="store_true", help="不按极性过滤")
    ap.add_argument("--ce", default=None, help="限定碰撞能")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--min-score", type=float, default=0.0)
    ap.add_argument("--backend", choices=["native", "auto", "matchms"], default="auto",
                    help="打分实现：native=自带引擎；auto=有 matchms 则用官方实现；matchms=强制官方")
    ap.add_argument("--format", choices=["md", "tsv", "json"], default="md")
    ap.add_argument("--out", default=None, help="输出文件（默认打印到终端）")
    ap.add_argument("--caps", action="store_true", help="打印可用后端后退出")
    args = ap.parse_args()

    if args.caps:
        print(json.dumps(capabilities(), ensure_ascii=False, indent=2))
        return
    if not args.query or not args.library:
        ap.error("--query 与 --library 为必填（或使用 --caps）")

    lib = SpectralLibrary(load_spectra(args.library))
    queries = load_spectra(args.query)
    if not queries:
        print("查询谱为空。", file=sys.stderr)
        sys.exit(1)
    methods = [m.strip() for m in args.method.split(",") if m.strip()]

    scorer, backend_used = None, "native"
    if args.backend in ("auto", "matchms"):
        if matchms_available():
            scorer, backend_used = make_matchms_scorer(), "matchms"
        elif args.backend == "matchms":
            print("matchms 未安装，回退自带引擎（见 --caps）。", file=sys.stderr)
    print("# 打分后端：%s | 打分器：%s" % (backend_used, ",".join(methods)), file=sys.stderr)

    blocks = []
    for qi, q in enumerate(queries, 1):
        results = lib.query(
            q, methods=methods, mz_tol=args.mz_tol, top_n=args.top,
            min_score=args.min_score, precursor_ppm=(args.precursor_ppm or None),
            adduct=args.adduct, polarity=not args.no_polarity,
            collision_energy=args.ce, scorer=scorer)
        if args.format == "md":
            blocks.append(R.to_markdown(q, results))
        elif args.format == "tsv":
            print("### 查询 %d: %s" % (qi, q.compound_name or q.get("id") or ""))
            print_tsv(q, results)
        else:
            blocks.append({"query": q.metadata, "n_peaks": len(q), "results": [
                {k: v for k, v in r.items() if k != "spectrum"} for r in results]})

    if args.format == "json":
        text = json.dumps(blocks, ensure_ascii=False, indent=2)
    elif args.format == "md":
        text = "\n\n---\n\n".join(blocks)
    else:
        text = None
    if text:
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(text)
            print("已写出：%s" % args.out)
        else:
            print(text)


if __name__ == "__main__":
    main()
