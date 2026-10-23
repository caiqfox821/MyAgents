# -*- coding: utf-8 -*-
"""生成 Rg1 / Rg3 的参考谱图 PNG（教学版单图、四记录叠加、Rg3 S/R 对比）。

    python3 plot_more.py
依赖 matplotlib（本机 3.5.3）。数据：peaks_all.csv
"""
import csv
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

g = defaultdict(list)
comp_of = {}
for r in csv.DictReader(open("peaks_all.csv", encoding="utf-8")):
    g[r["record"]].append((float(r["mz"]), float(r["relative_intensity"])))
    comp_of[r["record"]] = r["compound"]

RG1 = [
    ("MSBNK-RIKEN-PR307813", "[M+HCOO]- | NEG MS2 | QTOF CE 6V"),
    ("MSBNK-Univ_Toyama-TY000193", "[M+CH3COOH-H]- | NEG MS2 | IT-TOF"),
    ("MSBNK-Univ_Toyama-TY000020", "[M+CH3COOH-H]- | NEG MS1 | IT-TOF"),
    ("MSBNK-Univ_Toyama-TY000031", "[M+Na]+ | POS MS1 | IT-TOF"),
]
RG3 = [
    ("MSBNK-RIKEN-PR308546", "Rg3(S)  | [M-H]- | NEG MS2"),
    ("MSBNK-RIKEN-PR308678", "Rg3(S)  | [M+HCOO]- | NEG MS2"),
    ("MSBNK-RIKEN-PR308649", "Rg3(R)  | [M-H]- | NEG MS2"),
    ("MSBNK-RIKEN-PR308618", "Rg3(R)  | [M+HCOO]- | NEG MS2"),
]


def pct(rid):
    pk = sorted(g[rid])
    top = max(i for _, i in pk) or 1.0
    return [(m, i / top * 100) for m, i in pk]


def style(ax):
    ax.set_xlim(80, 940)
    ax.set_ylim(0, 120)
    ax.set_yticks([0, 50, 100])
    ax.grid(axis="x", ls=":", lw=0.4, alpha=0.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ---------- 1) Rg1 教学版单图 ----------
rid = "MSBNK-RIKEN-PR307813"
pk = pct(rid)
fig, ax = plt.subplots(figsize=(11, 5.2))
ax.vlines([m for m, _ in pk], 0, [i for _, i in pk], color="#1f5fa8", linewidth=1.3)
ax.scatter([m for m, _ in pk], [i for _, i in pk], s=4, color="#1f5fa8", zorder=3)
style(ax)
ax.set_ylabel("相对强度 (%)", fontsize=11)
ax.set_xlabel("m/z", fontsize=11)
ANN = {
    637.433: ("[M-H-Glc]-\n丢 1 个葡萄糖", "#b03030", 8),
    799.483: ("[M-H]-\n源内脱甲酸", "#b03030", -2),
    161.044: ("糖碎片", "#3a7d3a", 8),
    179.055: ("[Glc-H]-", "#3a7d3a", -14),
    638.439: ("同位素 M+1", "#777777", -16),
}
for m, (txt, col, dy) in ANN.items():
    d = dict(pk).get(m) or min(pk, key=lambda x: abs(x[0] - m))[1]
    ax.annotate("%.2f\n%s" % (m, txt), (m, d), textcoords="offset points",
                xytext=(0, dy), ha="center", fontsize=8.5, color=col)
ax.set_title("人参皂苷 Rg1 参考谱（%s）\n[M+HCOO]- | 负离子 MS2 | LC-ESI-QTOF | CE 6V" % rid,
             fontsize=11)
fig.tight_layout()
fig.savefig("Rg1_teaching_spectrum.png", dpi=150)
plt.close(fig)
print("wrote Rg1_teaching_spectrum.png")

# ---------- 2) Rg1 四记录叠加（瀑布式） ----------
fig, ax = plt.subplots(figsize=(11, 5.6))
step = 1.15
for k, (r_id, lab) in enumerate(RG1):
    base = k * step
    pk = pct(r_id)
    ax.vlines([m for m, _ in pk], base, [base + i / 100 * 0.95 for _, i in pk],
              color=plt.cm.tab10(k), linewidth=1.0)
    ax.text(945, base + 0.45, "%s\n%s" % (r_id.replace("MSBNK-", ""), lab),
            fontsize=7.5, va="center", color=plt.cm.tab10(k))
ax.set_xlim(80, 1150)
ax.set_ylim(-0.1, len(RG1) * step)
ax.set_yticks([])
ax.grid(axis="x", ls=":", lw=0.4, alpha=0.5)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.set_xlabel("m/z", fontsize=11)
ax.set_title("人参皂苷 Rg1 —— 4 条 MassBank 记录对比（不同加合物/电离方式）", fontsize=11)
fig.tight_layout()
fig.savefig("Rg1_overlay.png", dpi=150)
plt.close(fig)
print("wrote Rg1_overlay.png")

# ---------- 3) Rg3 (S/R) 对比 ----------
fig, axes = plt.subplots(4, 1, figsize=(10, 8.4), sharex=True)
for ax, (r_id, lab) in zip(axes, RG3):
    pk = pct(r_id)
    col = "#1f5fa8" if lab.startswith("Rg3(S)") else "#b03030"
    ax.vlines([m for m, _ in pk], 0, [i for _, i in pk], color=col, linewidth=1.0)
    ax.scatter([m for m, _ in pk], [i for _, i in pk], s=3, color=col, zorder=3)
    style(ax)
    ax.set_ylabel("相对强度\n(%)", fontsize=9)
    for m, i in sorted(pk, key=lambda x: -x[1])[:3]:
        ax.annotate("%.2f" % m, (m, i), textcoords="offset points", xytext=(0, 5),
                    ha="center", fontsize=7.5, color="#444")
    ax.set_title("%s   ·   %s" % (r_id, lab), fontsize=9, loc="left", pad=3, color=col)
axes[-1].set_xlabel("m/z", fontsize=10)
fig.suptitle("人参皂苷 Rg3 参考谱图（S/R 各 2 条）—— 观察 MS² 能否区分立体异构", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.965])
fig.savefig("Rg3_S_R_compare.png", dpi=150)
plt.close(fig)
print("wrote Rg3_S_R_compare.png")
