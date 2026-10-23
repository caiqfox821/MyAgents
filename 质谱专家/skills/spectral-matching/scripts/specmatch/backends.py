# -*- coding: utf-8 -*-
"""
specmatch.backends —— 可选增强后端
=================================

装了以下库时**自动增强**，没装也不影响核心功能（纯 Python 兜底）：

  * ``matchms``   —— 完整的导入/过滤/打分生态（本引擎 API 与之互通）
  * ``ms_entropy`` —— 高速熵相似度（大库检索）
  * ``pyteomics`` —— mzML / mzXML 读取
  * ``rdkit``     —— 由 SMILES 生成 InChIKey / 分子指纹

用 ``capabilities()`` 查看当前可用情况。
"""
import os
import sys


def _ver(mod):
    try:
        return getattr(mod, "__version__", "ok")
    except Exception:
        return None


def _try(name):
    try:
        return __import__(name)
    except Exception:
        return None


def capabilities():
    ms = _try("matchms")
    me = _try("ms_entropy")
    py = _try("pyteomics")
    rd = _try("rdkit")
    return {
        "python": sys.executable,
        "python_version": "%d.%d.%d" % sys.version_info[:3],
        "matchms": _ver(ms) if ms else None,
        "ms_entropy": "ok" if me else None,
        "pyteomics": _ver(py) if py else None,
        "rdkit": _ver(rd) if rd else None,
        "note": ("核心功能（MSP/MGF/JSON/CSV + 8 种打分）无需任何第三方库；"
                 "matchms/ms_entropy/pyteomics 为可选增强。"),
    }


# ------------------------------------------------------------------ mzML
def load_mzml(path):
    """用 pyteomics 读 mzML/mzXML，返回 Spectrum 列表（MS2 且带前体者优先）。"""
    try:
        from pyteomics import mzml as _mzml
    except Exception:
        raise RuntimeError(
            "读取 mzML 需要 pyteomics。请用技能自带脚本 setup_env.sh 建好环境，"
            "或先转成 MSP/MGF（MS-DIAL / MZmine / msconvert）。")
    from .spectrum import Spectrum
    spectra = []
    with _mzml.MzML(path) as reader:
        for spec in reader:
            ms_level = spec.get("ms level")
            if ms_level not in (2, None):
                continue
            mz = spec.get("m/z array")
            it = spec.get("intensity array")
            if mz is None or it is None or len(mz) == 0:
                continue
            md = {"id": spec.get("id"), "ms_level": ms_level,
                  "retention_time": spec.get("scanList", {}).get("scan", [{}])[0].get("scan start time")}
            for pi in spec.get("precursorList", {}).get("precursor", []):
                ion = pi.get("selectedIonList", {}).get("selectedIon", [{}])[0]
                md["precursor_mz"] = ion.get("selected ion m/z")
                if "charge state" in ion:
                    md["charge"] = ion["charge state"]
            spectra.append(Spectrum(mz=mz, intensities=it, metadata=md))
    return spectra


# ------------------------------------------------------------- matchms 桥
# matchms 0.33 的相似度函数命名
_MATCHMS_METHODS = {
    "cosine_greedy": "CosineGreedy",
    "cosine_hungarian": "CosineHungarian",
    "modified_cosine": "ModifiedCosineGreedy",
    "modified_cosine_hungarian": "ModifiedCosineHungarian",
    "neutral_losses": "NeutralLossesCosine",
    "intersect_mz": "IntersectMz",
}


def matchms_available():
    return _try("matchms") is not None


def _quiet_matchms():
    """matchms 对缺失 precursor_mz 会刷 WARNING；检索场景下压到 ERROR。"""
    import logging
    for name in ("matchms", "matchms.Spectrum", "matchms.Fragments",
                 "matchms.filtering", "matchms.similarity"):
        logging.getLogger(name).setLevel(logging.ERROR)


def to_matchms(spectrum):
    import numpy as np
    _quiet_matchms()
    from matchms import Spectrum as MSSpectrum
    md = dict(spectrum.metadata)
    return MSSpectrum(mz=np.asarray(spectrum.peaks[:, 0], dtype=float),
                      intensities=np.asarray(spectrum.peaks[:, 1], dtype=float),
                      metadata=md)


def _matchms_sim(method, mz_tol, mz_power=0.0, intensity_power=1.0):
    from matchms import similarity as S
    name = _MATCHMS_METHODS.get(method, method)
    cls = getattr(S, name)
    for kw in ({"tolerance": mz_tol, "mz_power": mz_power, "intensity_power": intensity_power},
               {"tolerance": mz_tol},
               {}):
        try:
            return cls(**kw)
        except TypeError:
            continue
    return cls()


def matchms_cosine(query, reference, mz_tol=0.01, method="cosine_greedy",
                   mz_power=0.0, intensity_power=1.0):
    """用 matchms 官方实现打分（需 matchms）。返回 (score, n_matched)。"""
    sim = _matchms_sim(method, mz_tol, mz_power, intensity_power)
    res = sim.pair(to_matchms(reference), to_matchms(query))
    return float(res["score"]), int(res["matches"])


def make_matchms_scorer(native_fallback=True):
    """返回一个 scorer 回调，供 SpectralLibrary.query(scorer=...) 使用。

    matchms 支持的打分器走官方实现；其余（如 entropy / match_factor）回退到自带引擎。
    """
    def _scorer(query, reference, method, mz_tol):
        if method in _MATCHMS_METHODS:
            try:
                return matchms_cosine(query, reference, mz_tol=mz_tol, method=method)
            except Exception:
                if not native_fallback:
                    raise
        from .similarity import get_similarity
        return get_similarity(method)(query, reference, mz_tol=mz_tol)
    return _scorer


# ---------------------------------------------------------- ms_entropy 桥
def ms_entropy_search(query_peaks, library_spectra, mz_tol=0.02):
    """用 ms_entropy 的 FlashEntropySearch 做高速检索。

    library_spectra: [{"precursor_mz":..., "peaks":[[mz,i],...], "id":...}, ...]
    返回 [[(index, score, matched_peaks), ...], ...]
    """
    from ms_entropy import FlashEntropySearch
    es = FlashEntropySearch()
    es.build_index(library_spectra, max_ms2_tolerance_in_da=mz_tol)
    return es.search(query_peaks, ms2_tolerance_in_da=mz_tol)
