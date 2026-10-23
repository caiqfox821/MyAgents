# -*- coding: utf-8 -*-
"""
specmatch.search —— 谱库检索
============================

核心原则（务必遵守）：
    1. **先候选过滤，再打分**：前体 m/z（ppm）＋ 极性 ＋ 加合物 ＋ 碰撞能，
       跨条件比对得到的分数没有意义。
    2. **可多打分器并行**：默认 ``entropy``（ESI）或 ``match_factor``（EI）。
    3. 输出**确定性表格**，便于人工复核与回归测试。
"""
import re

import numpy as np

from .similarity import get_similarity

_NUM_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def _num(x):
    """尽力转为 float：直接失败时从字符串中提取首个数字。

    用于 ``6V`` / ``20 eV`` / ``35%`` 这类带单位的碰撞能字段——
    旧实现遇到 ``"6V"`` 直接返回 None，导致 CE 过滤被静默跳过。
    """
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        pass
    m = _NUM_RE.search(str(x))
    return float(m.group(0)) if m else None


def _norm_adduct(x):
    """加合物归一化：优先走 filters 的规范表，退化时用小写去空格比较。"""
    if not x:
        return None
    try:
        from .filters import _norm_adduct_str
        norm = _norm_adduct_str(x)
        if norm:
            return norm
    except Exception:
        pass
    return str(x).strip().replace(" ", "").lower()


def ce_close(a, b, tol_da=0.0, rel=0.25):
    """碰撞能比较：容忍 rel 相对差或 tol_da 绝对差。"""
    a, b = _num(a), _num(b)
    if a is None or b is None:
        return True
    if a == b:
        return True
    span = max(abs(a), abs(b))
    return abs(a - b) <= max(tol_da, rel * span)


class SpectralLibrary(object):
    """一张可检索的参考谱库。"""

    def __init__(self, spectra):
        self.spectra = list(spectra)
        # 轻量索引：骨架 / 极性
        self._by_skeleton = {}
        for s in self.spectra:
            self._by_skeleton.setdefault(s.skeleton, []).append(s)

    def __len__(self):
        return len(self.spectra)

    @classmethod
    def from_files(cls, paths):
        from .io import load_spectra
        out = []
        for p in paths:
            out.extend(load_spectra(p))
        return cls(out)

    # ------------------------------------------------------------ 候选过滤
    def candidates(self, query, precursor_ppm=20.0, adduct=None, polarity=True,
                   collision_energy=None, ce_tol=0.25, use_skeleton=False):
        q_pm = query.precursor_mz
        pool = self.spectra
        if use_skeleton and query.skeleton:
            pool = self._by_skeleton.get(query.skeleton, [])
        out = []
        for r in pool:
            if polarity and query.ionmode and r.ionmode and query.ionmode != r.ionmode:
                continue
            # 加合物过滤：**仅当显式传入 adduct 时启用**，且要求记录加合物与之
            # 归一化后相等（记录缺加合物 → 排除）。
            # 修复：旧写法把"过滤值"与"查询加合物"并列做 `not in`，当二者相同
            # （即最常见用法）时条件恒假 → 过滤静默失效。
            if adduct:
                if _norm_adduct(r.adduct) != _norm_adduct(adduct):
                    continue
            if collision_energy is not None and not ce_close(
                    collision_energy, r.collision_energy, rel=ce_tol):
                continue
            if precursor_ppm is not None and q_pm is not None:
                if r.precursor_mz is None:
                    continue      # 有 ppm 过滤时，缺前体的记录不可比 → 排除
                if abs(q_pm - r.precursor_mz) / q_pm * 1e6 > precursor_ppm:
                    continue
            out.append(r)
        return out

    # ------------------------------------------------------------ 检索
    def query(self, query, methods=("entropy",), mz_tol=0.02, top_n=10,
              min_score=0.0, precursor_ppm=20.0, adduct=None, polarity=True,
              collision_energy=None, ce_tol=0.25, use_skeleton=False,
              candidate_spectra=None, scorer=None, **kw):
        cands = candidate_spectra if candidate_spectra is not None else self.candidates(
            query, precursor_ppm=precursor_ppm, adduct=adduct, polarity=polarity,
            collision_energy=collision_energy, ce_tol=ce_tol, use_skeleton=use_skeleton)
        fns = [(m, get_similarity(m)) for m in methods]
        rows = []
        for r in cands:
            rec = {"library_id": r.get("id") or r.get("library_id") or r.get("record"),
                   "compound": r.compound_name,
                   "inchikey": r.inchikey,
                   "adduct": r.adduct, "ionmode": r.ionmode,
                   "collision_energy": r.collision_energy,
                   "precursor_mz": r.precursor_mz,
                   "spectrum": r}
            for m, fn in fns:
                if scorer is not None:
                    s, n = scorer(query, r, m, mz_tol)
                else:
                    s, n = fn(query, r, mz_tol=mz_tol, **kw)
                rec["score_" + m] = float(s)
                rec["nmatched_" + m] = int(n)
            rows.append(rec)
        primary = "score_" + methods[0]
        rows = [x for x in rows if x.get(primary, 0.0) >= min_score]
        rows.sort(key=lambda x: -x.get(primary, 0.0))
        for i, x in enumerate(rows[:top_n], 1):
            x["rank"] = i
        return rows[:top_n]


def match_query(query, library, **kw):
    """单查询便捷函数：library 可为 SpectralLibrary 或谱列表。"""
    if not isinstance(library, SpectralLibrary):
        library = SpectralLibrary(library)
    return library.query(query, **kw)
