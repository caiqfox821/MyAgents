# -*- coding: utf-8 -*-
"""绘制人参皂苷 Rg1 的 MassBank 参考谱图（4 条记录，中文标注 + 峰值注释）。

    python3 plot_rg1.py            # 出 PNG + 终端打印 ASCII 概览
仅依赖 matplotlib（本机 3.5.3）。
"""
import csv
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

CSV = "peaks_all.csv"
OUT = "Rg1_mass_spectra_annotated.png"

# (记录号, 加合物/电离说明)
SPECS = [
    ("MSBNK-RIKEN-PR307813", "[M+HCOO]- | 负离子 MS2 | LC-ESI-QTOF | CE 6V"),
    ("MSBNK-Univ_Toyama-TY000193", "[M+CH3COOH-H]- | 负离子 MS2 | LC-ESI-IT-TOF"),
    ("MSBNK-Univ_Toyama-TY000020", "[M+CH3COOH-H]- | 负离子 MS1 | LC-ESI-IT-TOF"),
    ("MSBNK-Univ_Toyama-TY000031", "[M+Na]+ | 正离子 MS1 | LC-ESI-IT-TOF"),
]

g = defaultdict(list)
for r in csv.DictReader(open(CSV, encoding="utf-8")):
    if r["compound"] == "Rg1":
        g[r["record"]].append((float(r["mz"]), float(r["relative_intensity"])))


def ascii_plot(pk, width=64, height=10, lo=80, hi=940):
    """在终端用块字符画一张粗略棒图。"""
    top = max(i for _, i in pk)
    cols = [0.0] * width
    for m, i in pk:
        if lo <= m <= hi:
            c = int((m - lo) / (hi - lo) * (width - 1))
            cols[c] = max(cols[c], i / top)
    lines = []
    for row in range(height, 0, -1):
        thr = row / height
        lines.append("".join("█" if h >= thr else " " for h in cols))
    lines.append("└" + "─" * width)
    lines.append(" m/z %d%s%d" % (lo, " " * (width - len(str(lo)) - len(str(hi)) - 6), hi))
    return "\n".join(lines)


fig, axes = plt.subplots(len(SPECS), 1, figsize=(10, 8.6), sharex=True)
for ax, (rid, lab) in zip(axes, SPECS):
    pk = sorted(g[rid])
    top = max(i for _, i in pk)
    mzs = [m for m, _ in pk]
    rel = [i / top * 100 for _, i in pk]
    ax.vlines(mzs, 0, rel, color="#1f5fa8", linewidth=1.0)
    ax.scatter(mzs, rel, s=3, color="#1f5fa8", zorder=3)
    ax.set_xlim(80, 940)
    ax.set_ylim(0, 118)
    ax.set_yticks([0, 50, 100])
    ax.set_ylabel("相对强度\n(%)", fontsize=9)
    ax.grid(axis="x", ls=":", lw=0.4, alpha=0.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for m, i in sorted(((m, i / top * 100) for m, i in pk), key=lambda x: -x[1])[:4]:
        ax.annotate("%.2f" % m, (m, i), textcoords="offset points", xytext=(0, 5),
                    ha="center", fontsize=7.5, color="#b03030")
    ax.set_title("%s   ·   %s" % (rid, lab), fontsize=9, loc="left", pad=3)

axes[-1].set_xlabel("m/z", fontsize=10)
fig.suptitle("人参皂苷 Rg1（C42H72O14，M = 800.49）—— MassBank 参考谱图（4 条记录）",
             fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.965])
fig.savefig(OUT, dpi=150)
print("wrote", OUT)

# 终端概览：主记录（RIKEN [M+HCOO]- MS2）
main = "MSBNK-RIKEN-PR307813"
print("\n主谱：%s  [M+HCOO]- MS2 CE 6V" % main)
print(ascii_plot(g[main]))
