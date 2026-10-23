# -*- coding: utf-8 -*-
"""
specmatch.io —— 谱图读写
=======================

覆盖 matchms 常用格式：**MSP / MGF / JSON / CSV**。
mzML / mzXML 需 pyteomics（见 ``backends.py``），未安装时给出明确提示。

CSV 支持两种形态：
  * **长表**（本库惯用）：每行 = 一个峰，附 ``record/compound/ion_mode/adduct/ms_level`` 等列；
  * **宽表**：仅 ``mz,intensity`` 两列（单张谱）。
"""
import csv
import json
import os
import re

import numpy as np

from .spectrum import Spectrum

# MSP 键名 -> 内部元数据键
_MSP_FIELDS = {
    "name": "compound_name",
    "id": "id",
    "library_id": "id",
    "record": "record",
    "db#": "id",
    "db": "library",
    "exactmass": "exact_mass",
    "spectrum_type": "spectrum_type",
    "splash": "splash",
    "precursormz": "precursor_mz",
    "precursor_mz": "precursor_mz",
    "precursor_type": "adduct",
    "precursortype": "adduct",
    "adduct": "adduct",
    "ion_mode": "ionmode",
    "ionmode": "ionmode",
    "ionization": "ionmode",
    "collision_energy": "collision_energy",
    "collisionenergy": "collision_energy",
    "formula": "formula",
    "inchikey": "inchikey",
    "inchi": "inchi",
    "smiles": "smiles",
    "cas#": "casno",
    "casno": "casno",
    "compound_class": "compound_class",
    "retention_time": "retention_time",
    "retentiontime": "retention_time",
    "instrument": "instrument",
    "instrument_type": "instrument",
    "library": "library",
    "num_peaks": "_num_peaks",
}

_LOG_COLS = {"mz", "intensity", "relative_intensity", "rel", "abundance"}
_META_HINT = re.compile(r"^[A-Za-z][A-Za-z0-9_ #\-]*$")

# CSV 列名 -> 内部元数据键
_CSV_ALIAS = {
    "compound": "compound_name", "name": "compound_name", "title": "compound_name",
    "ion_mode": "ionmode", "ion mode": "ionmode", "ionization": "ionmode",
    "precursor_type": "adduct", "precursortype": "adduct",
    "collisionenergy": "collision_energy", "collision energy": "collision_energy",
    "retentiontime": "retention_time", "retention time": "retention_time",
}


def _harvest_comments(text, meta):
    """从 Comments 里提取 Adduct / CE 等常见片段。"""
    for pat, key in ((r"adduct[=:]\s*([^\s,;]+)", "adduct"),
                     (r"precursor_type[=:]\s*([^\s,;]+)", "adduct"),
                     (r"collision[_ ]?energy[=:]\s*([^\s,;]+)", "collision_energy"),
                     (r"inchikey[=:]\s*([A-Z\-]{20,30})", "inchikey")):
        m = re.search(pat, text, re.I)
        if m and key not in meta:
            meta[key] = m.group(1)


# ----------------------------------------------------------------------
# MSP
# ----------------------------------------------------------------------
def parse_msp_text(text, source=None):
    spectra, meta, peaks = [], {}, []

    def flush():
        if meta or peaks:
            m = dict(meta)
            m.pop("_num_peaks", None)
            s = Spectrum(peaks=peaks, metadata=m)
            if source:
                s.set("source", source)
            spectra.append(s)

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if meta or peaks:          # 空行 = 记录分隔（MSP 约定）
                flush()
                meta, peaks = {}, []
            continue
        if line.lower().startswith("name:") and peaks:
            flush()
            meta, peaks = {}, []
        head = line.split(":", 1)[0].strip()
        if ":" in line and _META_HINT.match(head):
            key, _, val = line.partition(":")
            k, v = key.strip().lower(), val.strip()
            if k == "num peaks":
                meta["_num_peaks"] = v
                continue
            if k in ("comments", "comment", "notes"):
                _harvest_comments(v, meta)
                continue
            meta[_MSP_FIELDS.get(k, key.strip())] = v
        else:
            parts = line.replace(",", " ").split()
            if len(parts) >= 2:
                try:
                    peaks.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    pass
    flush()
    return spectra


def load_msp(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return parse_msp_text(f.read(), source=os.path.basename(path))


def save_msp(spectra, path):
    order = ("compound_name", "precursor_mz", "ionmode", "adduct", "formula",
             "inchikey", "inchi", "smiles", "collision_energy", "retention_time",
             "instrument", "library")
    labels = {"compound_name": "Name", "precursor_mz": "PrecursorMZ",
              "ionmode": "Ion_mode", "adduct": "Precursor_type"}
    with open(path, "w", encoding="utf-8") as f:
        for s in spectra:
            m = s.metadata
            f.write("Name: %s\n" % (m.get("compound_name") or m.get("id") or "unknown"))
            if m.get("id"):
                f.write("ID: %s\n" % m["id"])
            if m.get("record") and m["record"] != m.get("id"):
                f.write("Record: %s\n" % m["record"])
            for k in order[1:]:
                if m.get(k) not in (None, ""):
                    f.write("%s: %s\n" % (labels.get(k, k), m[k]))
            f.write("Num Peaks: %d\n" % len(s))
            for mz, i in s.peaks:
                f.write("%.5f\t%.4f\n" % (mz, i))
            f.write("\n")
    return path


# ----------------------------------------------------------------------
# MGF
# ----------------------------------------------------------------------
def parse_mgf_text(text, source=None):
    spectra, meta, peaks, in_block = [], {}, [], False
    for raw in text.splitlines():
        line = raw.strip()
        if line.upper() == "BEGIN IONS":
            in_block, meta, peaks = True, {}, []
            continue
        if line.upper() == "END IONS":
            s = Spectrum(peaks=peaks, metadata=meta)
            if source:
                s.set("source", source)
            spectra.append(s)
            in_block = False
            continue
        if not in_block or not line:
            continue
        if "=" in line and not line[0].isdigit():
            k, _, v = line.partition("=")
            k = k.strip().upper()
            v = v.strip()
            if k == "PEPMASS":
                meta["precursor_mz"] = v.split()[0]
            elif k == "CHARGE":
                meta["charge"] = v
                meta["ionmode"] = "POSITIVE" if v.endswith("+") else (
                    "NEGATIVE" if v.endswith("-") else meta.get("ionmode"))
            elif k == "TITLE":
                meta["compound_name"] = v
            elif k in ("RTINSECONDS", "RTINMINUTES"):
                meta["retention_time"] = v
            elif k == "MSLEVEL":
                meta["ms_level"] = v
            else:
                meta[k.lower()] = v
        else:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    peaks.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    pass
    return spectra


def load_mgf(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return parse_mgf_text(f.read(), source=os.path.basename(path))


def save_mgf(spectra, path):
    with open(path, "w", encoding="utf-8") as f:
        for s in spectra:
            f.write("BEGIN IONS\n")
            f.write("TITLE=%s\n" % (s.compound_name or s.get("id") or "unknown"))
            if s.precursor_mz is not None:
                f.write("PEPMASS=%.5f\n" % s.precursor_mz)
            if s.get("ionmode"):
                f.write("IONMODE=%s\n" % s.get("ionmode"))
            if s.get("adduct"):
                f.write("ADDUCT=%s\n" % s.get("adduct"))
            if s.get("collision_energy"):
                f.write("COLLISIONENERGY=%s\n" % s.get("collision_energy"))
            if s.get("inchikey"):
                f.write("INCHIKEY=%s\n" % s.get("inchikey"))
            for mz, i in s.peaks:
                f.write("%.5f %.4f\n" % (mz, i))
            f.write("END IONS\n\n")
    return path


# ----------------------------------------------------------------------
# JSON
# ----------------------------------------------------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "spectra" in data:
        data = data["spectra"]
    out = []
    for d in data:
        md = dict(d.get("metadata", {}))
        for k, v in d.items():
            if k not in ("metadata", "peaks"):
                md.setdefault(k, v)
        out.append(Spectrum(peaks=d.get("peaks") or d.get("mz_intensity"), metadata=md))
    return out


def save_json(spectra, path, indent=None):
    payload = [{"metadata": s.metadata, "peaks": s.peaks.tolist()} for s in spectra]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=indent)
    return path


# ----------------------------------------------------------------------
# CSV（长表 / 宽表）
# ----------------------------------------------------------------------
def load_csv(path, intensity_col=None, mz_col="mz", encoding="utf-8"):
    with open(path, "r", encoding=encoding, errors="replace") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return []
    cols = rows[0].keys()
    if mz_col not in cols:
        return []
    if intensity_col is None:
        for c in ("intensity", "relative_intensity", "rel", "abundance"):
            if c in cols:
                intensity_col = c
                break
    meta_cols = [c for c in cols if c not in _LOG_COLS and c != mz_col]
    groups = {}
    for r in rows:
        key = tuple(r.get(c, "") for c in meta_cols)
        try:
            mz, it = float(r[mz_col]), float(r[intensity_col])
        except (TypeError, ValueError, KeyError):
            continue
        groups.setdefault(key, []).append((mz, it))
    out = []
    for key, peaks in groups.items():
        raw = dict(zip(meta_cols, key))
        md = {}
        for k, v in raw.items():
            if v == "":
                continue
            md[_CSV_ALIAS.get(k, k)] = v
        if md.get("record") and "id" not in md:
            md["id"] = md["record"]
        out.append(Spectrum(peaks=peaks, metadata=md))
    return out


# ----------------------------------------------------------------------
# 统一入口
# ----------------------------------------------------------------------
def load_spectra(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".msp" or ext == ".txt":
        return load_msp(path)
    if ext == ".mgf":
        return load_mgf(path)
    if ext == ".json":
        return load_json(path)
    if ext == ".csv":
        return load_csv(path)
    if ext in (".mzml", ".mzxml"):
        from . import backends
        return backends.load_mzml(path)
    raise ValueError("不支持的谱图格式: %s" % ext)


def save_spectra(spectra, path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".msp":
        return save_msp(spectra, path)
    if ext == ".mgf":
        return save_mgf(spectra, path)
    if ext == ".json":
        return save_json(spectra, path, indent=2)
    raise ValueError("不支持的导出格式: %s" % ext)
