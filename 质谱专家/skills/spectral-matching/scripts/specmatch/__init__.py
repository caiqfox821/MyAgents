# -*- coding: utf-8 -*-
"""
specmatch —— 本地质谱谱库比对引擎
==================================

设计目标
--------
1. **自带完整能力**：不装任何第三方库（仅 numpy）即可完成
   读库 → 过滤 → 打分 → 排序 → 置信度分级 → 报告 全流程。
2. **向上兼容 matchms**：装了 matchms / ms_entropy / pyteomics 时，
   通过 ``backends`` 自动增强（mzML 读取、更多打分器），API 不变。
3. **保留更多可能性**：打分器是**注册表**（``similarity.SIMILARITIES``），
   用户可以注册自己的算法；库过滤是**候选过滤器**，可插拔。

快速上手
--------
>>> from specmatch import load_spectra, SpectralLibrary
>>> refs = load_spectra("library.msp")
>>> lib = SpectralLibrary(refs)
>>> results = lib.query(load_spectra("query.msp")[0], top_n=5)

命令行见同目录上一级的 ``build_index.py`` / ``match.py``。
"""
import os

__version__ = "1.0.0"

from .spectrum import Spectrum, ensure_spectrum            # noqa: E402
from .io import (                                           # noqa: E402
    load_spectra, load_msp, load_mgf, load_json, load_csv,
    save_msp, save_mgf, save_json,
)
from . import filters                                        # noqa: E402
from .similarity import SIMILARITIES, get_similarity, score  # noqa: E402
from .search import SpectralLibrary, match_query             # noqa: E402
from .backends import capabilities                           # noqa: E402
from . import report                                         # noqa: E402

__all__ = [
    "Spectrum", "ensure_spectrum",
    "load_spectra", "load_msp", "load_mgf", "load_json", "load_csv",
    "save_msp", "save_mgf", "save_json",
    "filters", "SIMILARITIES", "get_similarity", "score",
    "SpectralLibrary", "match_query", "capabilities", "report",
    "__version__",
]
