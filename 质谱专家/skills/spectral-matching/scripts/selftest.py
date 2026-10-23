#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自检 / 回归测试：验证 io、filters、similarity、search、report 全链路。

    python3 selftest.py            # 合成数据自检
    python3 selftest.py <peaks.csv>  # 额外用真实峰表（长表 CSV）跑一遍
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np                                             # noqa: E402
from specmatch import Spectrum, load_spectra, SpectralLibrary  # noqa: E402
from specmatch import filters as F                             # noqa: E402
from specmatch import similarity as SIM                        # noqa: E402
from specmatch import report as R                              # noqa: E402
from specmatch.io import save_msp, load_msp                    # noqa: E402

PASS, FAIL = [], []


def check(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, extra))


def synth(seed, n=40, mz_max=500.0):
    rnd = random.Random(seed)
    mz = sorted(rnd.uniform(50, mz_max) for _ in range(n))
    it = [max(1.0, 1000 * (0.3 + rnd.random())) for _ in range(n)]
    return Spectrum(mz=mz, intensities=it,
                    metadata={"compound_name": "C%d" % seed, "precursor_mz": mz_max + 21.0,
                              "ionmode": "POSITIVE", "adduct": "[M+H]+",
                              "inchikey": "AAAA%010d-N-1" % seed, "id": "S%d" % seed})


def perturb(s, seed, drop=0.15, jitter=0.25, shift=0.004, noise=4):
    rnd = random.Random(seed)
    p = []
    for m, i in s.peaks:
        if rnd.random() < drop:
            continue
        p.append((m + rnd.uniform(-shift, shift), i * (1 + rnd.uniform(-jitter, jitter))))
    for _ in range(noise):
        p.append((rnd.uniform(50, 500), rnd.uniform(1, 30)))
    q = s.copy_with_peaks(p)
    return F.normalize_intensities(q)


def main():
    print("== 1. IO 往返（MSP） ==")
    s = synth(1)
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_selftest.msp")
    save_msp([s], tmp)
    back = load_msp(tmp)[0]
    check("MSP 往返峰数一致", len(back) == len(s), "%d vs %d" % (len(back), len(s)))
    check("MSP 往返 m/z 一致", np.allclose(back.mz, s.mz))
    check("MSP 往返元数据一致", back.compound_name == s.compound_name and
          abs(back.precursor_mz - s.precursor_mz) < 1e-6)
    os.remove(tmp)

    print("== 2. 过滤器 ==")
    n = F.normalize_intensities(s)
    check("normalize_intensities → max=1", abs(float(n.peaks[:, 1].max()) - 1.0) < 1e-9)
    sub = F.select_by_mz(s, 100, 300)
    check("select_by_mz 生效", bool(np.all((sub.mz >= 100) & (sub.mz <= 300))) and len(sub) > 0)
    r = F.reduce_to_number_of_peaks(s, n_max=10)
    check("reduce_to_number_of_peaks → ≤10", len(r) <= 10, "got %d" % len(r))
    parsed = F.add_parent_mass(F.derive_ionmode(F.derive_adduct_from_name(
        Spectrum(peaks=s.peaks, metadata={"compound_name": "X [M+H]+", "precursor_mz": "521.0"}))))
    check("derive_adduct + parent_mass", parsed.adduct == "[M+H]+" and
          abs(parsed.get("parent_mass") - (521.0 - 1.007276)) < 1e-3)

    print("== 3. 相似度 ==")
    c, m = SIM.cosine_greedy(s, s)
    e, me = SIM.entropy(s, s)
    check("自比对 cosine=1", abs(c - 1.0) < 1e-9, "%.4f" % c)
    check("自比对 entropy=1", abs(e - 1.0) < 1e-6, "%.4f" % e)
    check("自比对 match_factor≈1", abs(SIM.match_factor(s, s)[0] - 1.0) < 1e-6)
    far = synth(99)
    check("无关谱 cosine 低", SIM.cosine_greedy(s, far)[0] < 0.3,
          "%.3f" % SIM.cosine_greedy(s, far)[0])
    for name in sorted(SIM.SIMILARITIES):
        ok = isinstance(SIM.get_similarity(name)(s, s)[0], float)
        check("打分器可用: %s" % name, ok)

    print("== 4. 检索排序 ==")
    lib_specs = [synth(i) for i in range(1, 6)]
    lib = SpectralLibrary(lib_specs)
    for qi in range(1, 6):
        q = perturb(lib_specs[qi - 1], seed=100 + qi)
        res = lib.query(q, methods=("entropy", "cosine_greedy"), top_n=3, precursor_ppm=50)
        top = res[0] if res else {}
        check("查询 C%d → 命中自身" % qi, top.get("library_id") == "S%d" % qi,
              "top=%s(%.3f)" % (top.get("library_id"), top.get("score_entropy", 0)))

    print("== 5. 报告与分级 ==")
    q = perturb(lib_specs[0], seed=7)
    res = lib.query(q, methods=("entropy",), top_n=1)
    lvl, why = R.schymanski_level(res[0]["score_entropy"], "entropy", res[0]["nmatched_entropy"])
    check("高匹配无标准品 → Level 2", lvl == 2, "level=%d" % lvl)
    check("标准品+RT → Level 1", R.schymanski_level(0.9, "entropy", 10,
          has_standard=True, rt_match=True)[0] == 1)
    md = R.to_markdown(q, res)
    check("生成 Markdown 报告", "谱库匹配报告" in md and "| rank |" in md)

    print("== 6. 后端能力 ==")
    from specmatch.backends import capabilities
    caps = capabilities()
    print("  " + ", ".join("%s=%s" % (k, v) for k, v in caps.items()
                           if k in ("python_version", "matchms", "ms_entropy", "pyteomics", "rdkit")))

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        print("== 7. 真实峰表：%s ==" % os.path.basename(sys.argv[1]))
        specs = load_spectra(sys.argv[1])
        check("载入真实谱表", len(specs) > 0, "%d 张" % len(specs))
        lib2 = SpectralLibrary(specs)
        for s2 in specs[:3]:
            res2 = lib2.query(s2, methods=("entropy",), top_n=1, precursor_ppm=None,
                              polarity=False)
            check("真实谱自命中: %s" % (s2.get("record") or s2.compound_name),
                  res2 and res2[0].get("library_id") == (s2.get("record") or s2.get("id")),
                  "%.3f" % (res2[0]["score_entropy"] if res2 else 0))

    print("\n结果：%d 通过 / %d 失败" % (len(PASS), len(FAIL)))
    if FAIL:
        print("失败项：%s" % ", ".join(FAIL))
        sys.exit(1)


if __name__ == "__main__":
    main()
