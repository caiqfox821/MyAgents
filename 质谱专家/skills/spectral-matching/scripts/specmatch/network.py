# -*- coding: utf-8 -*-
"""
specmatch.network —— 谱相似度网络（分子网络雏形）
===============================================

在库内部两两打分，超过阈值即连边，并做连通分量聚类。
对应 matchms.networking / GNPS 分子网络的**最小可用版**（无可视化，输出边表 + 簇）。
"""
from .similarity import get_similarity


def build_network(spectra, method="modified_cosine", threshold=0.7, mz_tol=0.02,
                  top_k=None, require_same_polarity=True, **kw):
    fn = get_similarity(method)
    n = len(spectra)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = spectra[i], spectra[j]
            if require_same_polarity and a.ionmode and b.ionmode and a.ionmode != b.ionmode:
                continue
            s, m = fn(a, b, mz_tol=mz_tol, **kw)
            if s >= threshold:
                edges.append({"source": a.get("id") or i, "target": b.get("id") or j,
                              "score": round(float(s), 4), "n_matched": int(m)})
    if top_k:
        best = {}
        for e in edges:
            best.setdefault(e["source"], []).append(e)
        keep = set()
        for src, lst in best.items():
            for e in sorted(lst, key=lambda x: -x["score"])[:top_k]:
                keep.add((e["source"], e["target"]))
        edges = [e for e in edges if (e["source"], e["target"]) in keep]
    clusters = _components(n, spectra, edges)
    return {"method": method, "threshold": threshold, "edges": edges, "clusters": clusters}


def _components(n, spectra, edges):
    idx = {s.get("id") or i: i for i, s in enumerate(spectra)}
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for e in edges:
        if e["source"] in idx and e["target"] in idx:
            union(idx[e["source"]], idx[e["target"]])
    groups = {}
    for i, s in enumerate(spectra):
        groups.setdefault(find(i), []).append(s.compound_name or s.get("id") or i)
    return [g for g in groups.values() if len(g) > 1]
