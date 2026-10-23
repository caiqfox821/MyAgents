# -*- coding: utf-8 -*-
"""
specmatch.similarity —— 相似度打分器（可插拔注册表）
===================================================

约定：每个打分函数签名 ``f(query, reference, **kw) -> (score, n_matched)``，
score ∈ [0, 1]（``match_factor`` 另提供 0–999 缩放）。所有函数都做**容差内峰对齐**。

内置打分器
----------
===============  =====================================================
名称             适用
===============  =====================================================
cosine_greedy    ESI/EI 通用起点（贪心 1:1 匹配）
cosine_hungarian 同上，最优匹配（需 scipy，缺失时回退贪心）
modified_cosine  含中性丢失对齐，找**类似物/同系物**
neutral_losses   只按中性丢失匹配
entropy          熵相似度（Li et al. 2021），**ESI MS² 首选**
weighted_cosine  m/z 加权余弦（抑制低质量噪声）
match_factor     EI 谱库风格加权点积（0–999）
intersect_mz     匹配峰占比（快速粗筛）
===============  =====================================================

扩展：``register("my_score", fn)`` 即可让全流程识别。
"""
import math

import numpy as np

SIMILARITIES = {}


def register(name, fn=None):
    """注册自定义打分器。可作装饰器：``@register("x")``。"""
    if fn is None:
        def _deco(f):
            SIMILARITIES[name] = f
            return f
        return _deco
    SIMILARITIES[name] = fn
    return fn


def get_similarity(name):
    if name not in SIMILARITIES:
        raise KeyError("未知打分器 %r；可用：%s" % (name, sorted(SIMILARITIES)))
    return SIMILARITIES[name]


def score(name, query, reference, **kw):
    """统一入口：返回带元信息的 dict。"""
    fn = get_similarity(name)
    s, n = fn(query, reference, **kw)
    return {"method": name, "score": float(s), "n_matched": int(n)}


# ---------------------------------------------------------------- 工具
def _peaks(spectrum):
    return spectrum.peaks[:, 0], spectrum.peaks[:, 1]


def _greedy_pairs(mz1, mz2, tol, order=None):
    """贪心 1:1 对齐，返回匹配对索引列表 [(i, j), ...]。"""
    if order is None:
        order = np.argsort(-mz1)
    used = np.zeros(len(mz2), dtype=bool)
    pairs = []
    for i in order:
        diff = np.abs(mz2 - mz1[i])
        diff[used] = np.inf
        j = int(np.argmin(diff))
        if diff[j] <= tol:
            used[j] = True
            pairs.append((int(i), j))
    return pairs


def _paired_score(mz1, i1, mz2, i2, pairs, mz_power=0.0, intensity_power=1.0):
    w1 = (mz1 ** mz_power) * (i1 ** intensity_power)
    w2 = (mz2 ** mz_power) * (i2 ** intensity_power)
    num = sum(w1[i] * w2[j] for i, j in pairs)
    den = math.sqrt(float(np.sum(w1 * w1)) * float(np.sum(w2 * w2)))
    return (num / den if den > 0 else 0.0), len(pairs)


# ---------------------------------------------------------------- 余弦族
def cosine_greedy(query, reference, mz_tol=0.01, mz_power=0.0, intensity_power=1.0):
    mz1, i1 = _peaks(query)
    mz2, i2 = _peaks(reference)
    if len(mz1) == 0 or len(mz2) == 0:
        return 0.0, 0
    order = np.argsort(-i1)                       # 强度大者优先匹配
    pairs = _greedy_pairs(mz1, mz2, mz_tol, order=order)
    return _paired_score(mz1, i1, mz2, i2, pairs, mz_power, intensity_power)


def cosine_hungarian(query, reference, mz_tol=0.01, mz_power=0.0, intensity_power=1.0):
    mz1, i1 = _peaks(query)
    mz2, i2 = _peaks(reference)
    if len(mz1) == 0 or len(mz2) == 0:
        return 0.0, 0
    try:
        from scipy.optimize import linear_sum_assignment
    except Exception:
        return cosine_greedy(query, reference, mz_tol, mz_power, intensity_power)
    w1 = (mz1 ** mz_power) * (i1 ** intensity_power)
    w2 = (mz2 ** mz_power) * (i2 ** intensity_power)
    cost = np.zeros((len(mz1), len(mz2)))
    for a in range(len(mz1)):
        for b in range(len(mz2)):
            cost[a, b] = (w1[a] * w2[b]) if abs(mz1[a] - mz2[b]) <= mz_tol else 0.0
    r, c = linear_sum_assignment(-cost)
    pairs = [(int(a), int(b)) for a, b in zip(r, c) if cost[a, b] > 0]
    return _paired_score(mz1, i1, mz2, i2, pairs, mz_power, intensity_power)


def weighted_cosine(query, reference, mz_tol=0.01, mz_power=0.5, intensity_power=1.0):
    return cosine_greedy(query, reference, mz_tol, mz_power, intensity_power)


# ---------------------------------------------------------------- 修饰余弦
def modified_cosine(query, reference, mz_tol=0.01, mz_power=0.0, intensity_power=1.0):
    """中性丢失对齐：|mz1-mz2|<=tol 或 |(prec1-mz1)-(prec2-mz2)|<=tol 视为匹配。"""
    mz1, i1 = _peaks(query)
    mz2, i2 = _peaks(reference)
    if len(mz1) == 0 or len(mz2) == 0:
        return 0.0, 0
    pm1, pm2 = query.precursor_mz, reference.precursor_mz
    if pm1 is None or pm2 is None:
        return cosine_greedy(query, reference, mz_tol, mz_power, intensity_power)
    nl1 = pm1 - mz1
    nl2 = pm2 - mz2
    order = np.argsort(-i1)
    used = np.zeros(len(mz2), dtype=bool)
    pairs = []
    for i in order:
        ok = (~used) & ((np.abs(mz2 - mz1[i]) <= mz_tol) |
                        (np.abs(nl2 - nl1[i]) <= mz_tol))
        idx = np.where(ok)[0]
        if idx.size:
            j = int(idx[np.argmin(np.abs(mz2[idx] - mz1[i]))])
            used[j] = True
            pairs.append((int(i), j))
    return _paired_score(mz1, i1, mz2, i2, pairs, mz_power, intensity_power)


def neutral_losses(query, reference, mz_tol=0.01, mz_power=0.0, intensity_power=1.0):
    mz1, i1 = _peaks(query)
    mz2, i2 = _peaks(reference)
    pm1, pm2 = query.precursor_mz, reference.precursor_mz
    if pm1 is None or pm2 is None or len(mz1) == 0 or len(mz2) == 0:
        return 0.0, 0
    nl1, nl2 = pm1 - mz1, pm2 - mz2
    order = np.argsort(-i1)
    used = np.zeros(len(mz2), dtype=bool)
    pairs = []
    for i in order:
        ok = (~used) & (np.abs(nl2 - nl1[i]) <= mz_tol)
        idx = np.where(ok)[0]
        if idx.size:
            j = int(idx[np.argmin(np.abs(nl2[idx] - nl1[i]))])
            used[j] = True
            pairs.append((int(i), j))
    return _paired_score(mz1, i1, mz2, i2, pairs, mz_power, intensity_power)


# ---------------------------------------------------------------- 熵相似度
def _clean_spectrum(mz, inten, tol):
    """合并容差内峰（强度取大、m/z 依强度加权），再归一化到 sum=1。"""
    order = np.argsort(mz)
    mz, inten = mz[order], inten[order]
    out_mz, out_i = [], []
    for m, v in zip(mz, inten):
        if out_mz and m - out_mz[-1] <= tol:
            pm, pv = out_mz[-1], out_i[-1]
            tot = pv + v
            out_mz[-1] = (pm * pv + m * v) / tot if tot > 0 else pm
            out_i[-1] = max(pv, v)
        else:
            out_mz.append(m)
            out_i.append(v)
    a = np.array(out_i, dtype=float)
    s = a.sum()
    return np.array(out_mz, dtype=float), (a / s if s > 0 else a)


def _entropy(p):
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))


def entropy(query, reference, mz_tol=0.02, **kw):
    """熵相似度（Li et al. 2021 定义的自实现；生产建议用 ms_entropy 复核）。"""
    mz1, i1 = _peaks(query)
    mz2, i2 = _peaks(reference)
    if len(mz1) == 0 or len(mz2) == 0:
        return 0.0, 0
    mz1, p1 = _clean_spectrum(mz1, i1, mz_tol)
    mz2, p2 = _clean_spectrum(mz2, i2, mz_tol)
    used = np.zeros(len(mz2), dtype=bool)
    mixed_mz, mixed_p = [], []
    n_matched = 0
    for k in range(len(mz1)):
        diff = np.abs(mz2 - mz1[k])
        diff[used] = np.inf
        j = int(np.argmin(diff))
        if diff[j] <= mz_tol:
            used[j] = True
            n_matched += 1
            mixed_mz.append(mz1[k])
            mixed_p.append(p1[k] + p2[j])
        else:
            mixed_mz.append(mz1[k])
            mixed_p.append(p1[k])
    for j in range(len(mz2)):
        if not used[j]:
            mixed_mz.append(mz2[j])
            mixed_p.append(p2[j])
    mixed = np.array(mixed_p, dtype=float)
    mixed = mixed / mixed.sum()
    hq, hr, hm = _entropy(p1), _entropy(p2), _entropy(mixed)
    if hq + hr == 0:
        return 1.0, n_matched
    val = 1.0 - (2.0 * hm - hq - hr) / (hq + hr)
    return max(0.0, min(1.0, val)), n_matched


# ---------------------------------------------------------------- EI 匹配因子
def match_factor(query, reference, mz_tol=0.5, mz_power=0.5, intensity_power=1.0):
    """EI 谱库风格加权点积。返回 (score01, n_matched)；乘 999 得 NIST 风格 MF。

    注意：这是**近似实现**（未复刻 NIST MS Search 的全部经验权重），
    用于排序可靠，绝对分值须以 NIST/AMDIS 为准。
    """
    mz1, i1 = _peaks(query)
    mz2, i2 = _peaks(reference)
    if len(mz1) == 0 or len(mz2) == 0:
        return 0.0, 0
    bins = np.rint(np.concatenate([mz1, mz2])).astype(int)
    lo, hi = bins.min(), bins.max()
    n = hi - lo + 1
    v1 = np.zeros(n)
    v2 = np.zeros(n)
    for m, v in zip(mz1, i1):
        v1[int(round(m)) - lo] = max(v1[int(round(m)) - lo], v)
    for m, v in zip(mz2, i2):
        v2[int(round(m)) - lo] = max(v2[int(round(m)) - lo], v)
    masses = np.arange(lo, hi + 1, dtype=float)
    w = masses ** mz_power
    a, b = w * v1 ** intensity_power, w * v2 ** intensity_power
    den = math.sqrt(float(np.sum(a * a)) * float(np.sum(b * b)))
    s = float(np.sum(a * b) / den) if den > 0 else 0.0
    return s, int(np.count_nonzero(v1 * v2))


# ---------------------------------------------------------------- 其它
def intersect_mz(query, reference, mz_tol=0.01, **kw):
    mz1, _ = _peaks(query)
    mz2, _ = _peaks(reference)
    if len(mz1) == 0:
        return 0.0, 0
    n = 0
    for m in mz1:
        if np.min(np.abs(mz2 - m)) <= mz_tol:
            n += 1
    return n / float(len(mz1)), n


for _name, _fn in [
    ("cosine_greedy", cosine_greedy), ("cosine_hungarian", cosine_hungarian),
    ("modified_cosine", modified_cosine), ("neutral_losses", neutral_losses),
    ("entropy", entropy), ("weighted_cosine", weighted_cosine),
    ("match_factor", match_factor), ("intersect_mz", intersect_mz),
]:
    register(_name, _fn)
