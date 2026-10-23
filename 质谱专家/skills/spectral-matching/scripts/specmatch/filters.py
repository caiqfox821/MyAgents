# -*- coding: utf-8 -*-
"""
specmatch.filters —— 谱图清洗与元数据规范化
==========================================

每个过滤器签名 ``f(spectrum) -> Spectrum | None``（返回 ``None`` 表示丢弃该谱），
与 matchms 的过滤器约定一致。用 ``apply()`` 串成流水线，``default_filters()``
给出推荐的默认流程。
"""
import re

from .spectrum import Spectrum

# 常见加合物：(电荷数, 质量偏移)。parent = precursor * |z| - shift
ADDUCTS = {
    "[M+H]+": (1, 1.007276),
    "[M-H]-": (1, -1.007276),
    "[M+Na]+": (1, 22.989218),
    "[M+K]+": (1, 38.963158),
    "[M+NH4]+": (1, 18.033823),
    "[M+H-H2O]+": (1, -17.002740),
    "[M+2H]2+": (2, 2.014552),
    "[M+HCOO]-": (1, 44.997655),   # [M+FA-H]-
    "[M+FA-H]-": (1, 44.997655),
    "[M+CH3COO]-": (1, 59.013305),  # [M+Ac-H]-
    "[M+Ac-H]-": (1, 59.013305),
    "[M+Cl]-": (1, 34.968853),
    "[M+HCO3]-": (1, 60.992570),
}
_ADDUCT_ALIASES = {
    "M+H": "[M+H]+", "M-H": "[M-H]-", "M+NA": "[M+Na]+", "M+K": "[M+K]+",
    "M+NH4": "[M+NH4]+", "M+HCOO": "[M+HCOO]-", "M+FA-H": "[M+HCOO]-",
    "M+CH3COO": "[M+CH3COO]-", "M+AC-H": "[M+CH3COO]-", "M+CL": "[M+Cl]-",
    "M+H-H2O": "[M+H-H2O]+",
}
_INCHIKEY_RE = re.compile(r"^[A-Z]{14}-[A-Z]{10}-[A-Z]$")

_DROP_NAME_PATTERNS = (
    r"^N/?A$", r"^unknown.*$", r"^unidentified.*$", r"^no name.*$",
    r"^null$", r"^none$", r"^\d{2,7}-\d{2}-\d$",   # 纯 CAS 号
)


def _norm_adduct_str(text):
    if not text:
        return None
    t = text.strip().replace(" ", "")
    up = t.upper().replace("+1", "+").replace("-1", "-")
    if up in ADDUCTS:
        return up
    core = t.strip("[]").replace("-", "-").upper()
    return _ADDUCT_ALIASES.get(core) or _ADDUCT_ALIASES.get(core.replace("+", ""))


# ---------------------------------------------------------------- 元数据
def make_charge_int(s):
    if "charge" in s.metadata:
        raw = str(s.metadata["charge"]).strip()
        m = re.search(r"([+-]?\d+)", raw)
        s.metadata["charge"] = int(m.group(1)) if m else raw
    return s


def derive_adduct_from_name(s):
    if s.get("adduct"):
        s.set("adduct", _norm_adduct_str(s.get("adduct")) or s.get("adduct"))
        return s
    for key in ("compound_name", "name", "title"):
        m = re.search(r"\[([^\]]*M[^\]]*)\]\s*([+-])", s.get(key) or "")
        if m:
            a = _norm_adduct_str("[%s]%s" % (m.group(1), m.group(2)))
            if a:
                s.set("adduct", a)
                return s
    return s


def derive_ionmode(s):
    if s.get("ionmode"):
        im = str(s.get("ionmode")).upper()
        s.metadata["ionmode"] = "POSITIVE" if im.startswith(("P", "+")) else (
            "NEGATIVE" if im.startswith(("N", "-")) else im)
        return s
    ad = s.get("adduct") or ""
    if ad.endswith("+"):
        s.set("ionmode", "POSITIVE")
    elif ad.endswith("-"):
        s.set("ionmode", "NEGATIVE")
    elif s.get("charge"):
        try:
            s.set("ionmode", "POSITIVE" if int(s.get("charge")) >= 0 else "NEGATIVE")
        except (TypeError, ValueError):
            pass
    return s


def correct_charge(s):
    if not s.get("charge") and s.get("ionmode"):
        s.set("charge", 1 if s.get("ionmode") == "POSITIVE" else -1)
    return s


def add_parent_mass(s):
    """由 precursor_mz + adduct 反推中性分子质量。"""
    pm = s.precursor_mz
    if pm is None:
        return s
    ad = _norm_adduct_str(s.get("adduct"))
    if ad and ad in ADDUCTS:
        z, shift = ADDUCTS[ad]
    elif s.get("ionmode") == "NEGATIVE":
        z, shift = 1, -1.007276
    else:
        z, shift = 1, 1.007276
    s.set("parent_mass", round(pm * abs(z) - shift, 6))
    return s


def clean_compound_name(s):
    for key in ("compound_name", "name"):
        v = s.get(key)
        if not v:
            continue
        v = re.sub(r"^(name|title)\s*[:=]\s*", "", v.strip(), flags=re.I)
        v = re.sub(r"\s*(positive|negative|pos|neg)\s*(mode)?\s*$", "", v, flags=re.I)
        v = re.sub(r"\s*\[[^\]]*\]\s*[+-]?\s*$", "", v)      # 去掉尾部加合物
        v = re.sub(r"\s{2,}", " ", v).strip(" ;,.")
        if any(re.match(p, v, re.I) for p in _DROP_NAME_PATTERNS):
            v = v if key != "compound_name" else None
        if v:
            s.set(key, v)
    return s


def harmonize_inchikey(s):
    ik = s.get("inchikey")
    if not ik:
        return s
    ik = str(ik).strip().upper()
    s.set("inchikey", ik if _INCHIKEY_RE.match(ik) else None)
    if s.get("inchikey") is None:
        s.metadata.pop("inchikey", None)
    return s


def derive_formula_from_name(s):
    if s.get("formula"):
        return s
    m = re.search(r"([A-Z][a-z]?\d*){2,}", s.compound_name or "")
    if m and re.search(r"\d", m.group(0)):
        s.set("formula", m.group(0))
    return s


# ---------------------------------------------------------------- 峰表
def normalize_intensities(s):
    if len(s) == 0:
        return s
    mx = float(s.peaks[:, 1].max())
    if mx > 0:
        return s.copy_with_peaks(s.peaks / [1.0, mx])
    return s


def select_by_mz(s, mz_from=0.0, mz_to=10000.0):
    p = s.peaks
    p = p[(p[:, 0] >= mz_from) & (p[:, 0] <= mz_to)]
    return s.copy_with_peaks(p)


def select_by_intensity(s, intensity_from=0.0, intensity_to=1e12):
    p = s.peaks
    p = p[(p[:, 1] >= intensity_from) & (p[:, 1] <= intensity_to)]
    return s.copy_with_peaks(p)


def select_by_relative_intensity(s, intensity_from=0.0, intensity_to=1.0):
    if len(s) == 0:
        return s
    mx = float(s.peaks[:, 1].max()) or 1.0
    rel = s.peaks[:, 1] / mx
    return s.copy_with_peaks(s.peaks[(rel >= intensity_from) & (rel <= intensity_to)])


def reduce_to_number_of_peaks(s, n_max=200, n_required=1, min_relative_intensity=0.0):
    if len(s) <= n_max and min_relative_intensity == 0.0:
        return s
    mx = float(s.peaks[:, 1].max()) or 1.0
    keep = s.peaks[(s.peaks[:, 1] / mx) >= min_relative_intensity]
    if keep.shape[0] < n_required:
        keep = s.peaks
    if keep.shape[0] > n_max:
        idx = keep[:, 1].argsort()[::-1][:n_max]
        keep = keep[np_sort(idx)]
    return s.copy_with_peaks(keep)


def np_sort(idx):
    import numpy as np
    return np.sort(idx)


def require_precursor_mz(s):
    return s if s.precursor_mz is not None else None


def require_minimum_number_of_peaks(s, n_required=10):
    return s if len(s) >= n_required else None


# ---------------------------------------------------------------- 流水线
def default_filters(require_precursor=False, min_peaks=10,
                    mz_from=10.0, mz_to=1000.0, n_max=200):
    """推荐的默认清洗流程（顺序敏感）。"""
    pipeline = [
        make_charge_int,
        derive_adduct_from_name,
        derive_ionmode,
        correct_charge,
        clean_compound_name,
        harmonize_inchikey,
        add_parent_mass,
        lambda s: select_by_mz(s, mz_from, mz_to),
        lambda s: reduce_to_number_of_peaks(s, n_max=n_max, n_required=1,
                                            min_relative_intensity=0.0),
        normalize_intensities,
    ]
    if require_precursor:
        pipeline.append(require_precursor_mz)
    pipeline.append(lambda s: require_minimum_number_of_peaks(s, n_required=min_peaks))
    return pipeline


def apply(spectrum, pipeline):
    """依次执行过滤器；任一返回 None 则整体丢弃。"""
    s = spectrum
    for f in pipeline:
        if s is None:
            return None
        s = f(s)
    return s


def apply_to_all(spectra, pipeline):
    out = []
    for s in spectra:
        r = apply(s, pipeline)
        if r is not None:
            out.append(r)
    return out
