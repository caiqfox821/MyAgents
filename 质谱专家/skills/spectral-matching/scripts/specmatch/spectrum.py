# -*- coding: utf-8 -*-
"""
specmatch.spectrum —— 数据模型
==============================

``Spectrum`` = 峰表（N×2 float 的 (m/z, intensity) 数组）+ 元数据 dict。
语义与 ``matchms.Spectrum`` 的常用部分对齐，便于在有 matchms 时无缝互通。
"""
import numpy as np

_MZ, _I = 0, 1


def as_peaks(peaks):
    """把任意 (N,2) 输入规整为按 m/z 升序、去除非法/非正强度的 float 数组。"""
    a = np.asarray(peaks, dtype=float)
    if a.size == 0:
        return np.zeros((0, 2), dtype=float)
    if a.ndim != 2 or a.shape[1] != 2:
        raise ValueError("peaks 必须为 N×2 的 (m/z, intensity) 数组")
    a = a[np.isfinite(a).all(axis=1)]
    a = a[a[:, _I] > 0]
    return a[np.argsort(a[:, _MZ], kind="mergesort")]


class Spectrum(object):
    """一张质谱（峰表 + 元数据）。"""

    def __init__(self, mz=None, intensities=None, metadata=None, peaks=None):
        if peaks is not None:
            self.peaks = as_peaks(peaks)
        elif mz is not None and intensities is not None:
            self.peaks = as_peaks(list(zip(mz, intensities)))
        else:
            self.peaks = np.zeros((0, 2), dtype=float)
        self.metadata = dict(metadata or {})

    # ---------------- 元数据 ----------------
    def get(self, key, default=None):
        return self.metadata.get(key, default)

    def set(self, key, value):
        self.metadata[key] = value
        return self

    def clone(self):
        return Spectrum(peaks=self.peaks.copy(), metadata=dict(self.metadata))

    def copy_with_peaks(self, peaks):
        return Spectrum(peaks=peaks, metadata=dict(self.metadata))

    # ---------------- 常用属性 ----------------
    @property
    def mz(self):
        return self.peaks[:, _MZ]

    @property
    def intensities(self):
        return self.peaks[:, _I]

    @property
    def precursor_mz(self):
        try:
            return float(self.get("precursor_mz"))
        except (TypeError, ValueError):
            return None

    @property
    def ionmode(self):
        return self.get("ionmode")

    @property
    def adduct(self):
        return self.get("adduct")

    @property
    def precursor_type(self):
        return self.get("adduct")

    @property
    def collision_energy(self):
        return self.get("collision_energy")

    @property
    def inchikey(self):
        return self.get("inchikey")

    @property
    def skeleton(self):
        ik = self.get("inchikey") or ""
        return ik.split("-")[0] if ik else None

    @property
    def compound_name(self):
        return self.get("compound_name") or self.get("name")

    def __len__(self):
        return int(self.peaks.shape[0])

    def __repr__(self):
        return "<Spectrum %r peaks=%d precursor_mz=%s>" % (
            self.compound_name or self.get("id") or "?", len(self), self.precursor_mz)


def ensure_spectrum(obj):
    """把 dict / Spectrum 统一成 Spectrum。"""
    if isinstance(obj, Spectrum):
        return obj
    if isinstance(obj, dict):
        md = {k: v for k, v in obj.items() if k != "peaks"}
        return Spectrum(peaks=obj.get("peaks"), metadata=md)
    raise TypeError("无法识别的谱对象: %r" % type(obj))
