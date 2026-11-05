#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五级递进固态发酵（SSF）动力学模型引擎
=====================================
归属：发酵专家私有技能（solid-state-fermentation）

建模对象：好氧固态发酵（制曲、产酶、产酸、制酒）。
递进主线是 SSF 的**物理瓶颈链**：空间容量 → 水活度 → 传热 → 传质 → 混菌。

> 纤维质物料（青贮、堆肥、果渣饲料）的转化模型是**另一个技能**
> `lignocellulose-conversion`，不要混用。

双入口
------
入口一 · 模型预测计算：list / params / simulate / profile / control
入口二 · 案例 Demo 演示：demo

纪律约定（照《五级模型方程与案例》文档执行）
---------------------------------------------
1. 只实现 Scale 1–5 文档给出的方程、参数与案例；不新增任何动力学机制。
2. 模型必须由用户手动指定 --scale（1..5），脚本不擅自替用户选型。
3. 文档未给出的数值一律使用明确标注的“演示默认值”，可用 --set key=value 覆盖；
   这些默认值只用于让方程可数值求解，不构成新的动力学假设。

浓度基准
--------
SSF 用“单位干基质量分数” g/g DM，不是 g/L。
换算：含水率 w（湿基）时，1 g 干基对应 w/(1-w) g 水。

参数覆盖
--------
--set key=value 可重复，例如： --set mu_max=0.15 --set H=10 --set aw=0.97
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np

try:
    from scipy.integrate import solve_ivp
except Exception:  # pragma: no cover
    solve_ivp = None


# ---------------------------------------------------------------------------
# 一、模型面板与案例参数
# ---------------------------------------------------------------------------

SCALES = {
    1: "基础分批 SSF 模型（Logistic 空间限制 + Luedeking–Piret 产物）",
    2: "水活度限制 SSF 模型（a_w 线性抑制生长）",
    3: "传热限制 SSF 模型（代谢产热 − 散热，温度反馈抑制）",
    4: "传质限制 SSF 模型（床层深度 → 有效供氧下降，O₂ 限制）",
    5: "混菌共发酵 SSF 模型（霉菌糖化 + 酵母发酵，乙醇抑制）",
}

# 真实示范案例（来自文档）
CASES = {
    1: {
        "organism": "米曲霉 Aspergillus oryzae",
        "ascii": "A. oryzae",
        "system": "麸皮制曲，含水率 60%，初始 pH 6.0；产物：中性蛋白酶",
        "params": {"mu_max": 0.10, "Xm": 0.30, "Yxs": 0.50, "ms": 0.005,
                   "alpha": 1.2, "beta": 0.01,
                   "S0": 1.00, "X0": 0.01, "P0": 0.0},
        "assumed": ["S0", "X0", "P0"],
        "tend": 48.0,
        "result": ("48 h 时 X=0.242、S=0.511、P=0.327；菌体趋近 Xm 后产物仍继续累积（β 项）；"
                   "底物全程有余量（S 仅从 1.00 降到 0.51）——限制来自空间而非底物。"),
    },
    2: {
        "organism": "黑曲霉 Aspergillus niger",
        "ascii": "A. niger",
        "system": "麸皮 + 蔗糖，a_w=0.95；产物：果胶酶",
        "params": {"mu_max": 0.12, "Xm": 0.28, "Yxs": 0.45, "ms": 0.006,
                   "alpha": 0.8, "beta": 0.02,
                   "aw": 0.95, "aw_min": 0.80,
                   "S0": 1.00, "X0": 0.01, "P0": 0.0},
        "assumed": ["aw", "S0", "X0", "P0"],
        "tend": 60.0,
        "result": ("a_w 从 0.99 降到 0.90，f_aw 从 0.95 降到 0.50，比生长速率近似腰斩；"
                   "含水率是比较器：过高结块缺氧，过低抑制生长，存在最优窗口。"),
    },
    3: {
        "organism": "里氏木霉 Trichoderma reesei",
        "ascii": "T. reesei",
        "system": "麸皮 + 秸秆，含水率 65%，填充床 15 cm；产物：纤维素酶",
        "params": {"mu_max": 0.12, "Xm": 0.30, "Yxs": 0.45, "ms": 0.006,
                   "alpha": 0.9, "beta": 0.02,
                   "aw": 0.96, "aw_min": 0.80,
                   "Tmin": 5.0, "Topt": 28.0, "Tmax": 42.0,
                   "YQ": 2.0e4, "hA": 6.0, "Ceff": 3.5,
                   "Tamb": 30.0, "T0": 30.0,
                   "S0": 1.00, "X0": 0.01, "P0": 0.0},
        "assumed": ["mu_max", "Xm", "Yxs", "ms", "alpha", "beta",
                    "aw", "aw_min", "Tamb", "T0", "S0", "X0", "P0"],
        "tend": 72.0,
        "result": ("72 h 时床温峰值 39.2 ℃（ΔT≈9 K），f_T 降至约 0.38，X 仅 0.174、P=0.266；"
                   "体系呈「热自限制」：继续削弱散热（hA 由 6 减到 3）温度只升到约 40.3 ℃，但 X 掉到 0.107"
                   "——温度上升有限、产率损失显著，这是 SSF 放大最典型的困境。"),
    },
    4: {
        "organism": "黑曲霉 Aspergillus niger",
        "ascii": "A. niger",
        "system": "麸皮 + 糖蜜，含水率 60%，静态床层 30 cm，通风 0.5 vvm；产物：柠檬酸",
        "params": {"mu_max": 0.12, "Xm": 0.28, "Yxs": 0.45, "ms": 0.006,
                   "alpha": 0.8, "beta": 0.02,
                   "aw": 0.95, "aw_min": 0.80,
                   "Tmin": 5.0, "Topt": 30.0, "Tmax": 45.0,
                   "YQ": 2.0e4, "hA": 6.0, "Ceff": 3.5,
                   "Tamb": 30.0, "T0": 30.0,
                   "kLa0": 3.2, "Href": 4.0, "H": 30.0,
                   "O2star": 0.02, "KO2": 0.006, "Yox": 0.7, "mO2": 0.003,
                   "O20": 0.02,
                   "S0": 1.00, "X0": 0.01, "P0": 0.0},
        "assumed": ["mu_max", "Xm", "Yxs", "ms", "alpha", "beta",
                    "aw", "aw_min", "Tmin", "Topt", "Tmax", "YQ", "hA", "Ceff",
                    "Tamb", "T0", "O20", "S0", "X0", "P0"],
        "tend": 72.0,
        "result": ("H=30 cm 时 kLa_eff=0.38 h⁻¹，最低氧降到 0.0090 g/g DM，f_O2≈0.60——"
                   "四成生长能力被缺氧吃掉，72 h 终点 P=0.215；床层降到 5 cm，kLa_eff=1.42、"
                   "f_O2≈0.74、P=0.233。床层加深不改变终点容量，但拖慢一切。"),
    },
    5: {
        "organism": "米曲霉 A. oryzae（糖化）+ 酿酒酵母 S. cerevisiae（发酵）",
        "ascii": "A. oryzae + S. cerevisiae",
        "system": "蒸煮高粱/大米，含水率 60%，初始 pH 5.5；产物：乙醇",
        "params": {"mu1": 0.10, "Xm1": 0.25,
                   "khkE": 0.02, "Ks": 0.15, "Ygs": 0.85,
                   "mu2": 0.25, "KG": 0.005, "Xm2": 0.10, "Yxg": 0.45, "mG": 0.002,
                   "Ypg": 0.45, "bp": 0.03, "Pcrit": 0.12,
                   "S0": 0.70, "G0": 0.005, "X10": 0.01, "X20": 0.002, "P0": 0.0},
        "assumed": ["S0", "G0", "X10", "X20", "P0"],
        "tend": 120.0,
        "result": ("120 h 终点 X1=0.250、X2=0.057、S=0.360、G=0.0015、P=0.074。"
                   "① 还原糖全程不累积（糖化限速，淀粉利用率约 49%，对应固态白酒的 60%–70% 区间）；"
                   "② 乙醇抑制全程按 (1-P/Pcrit) 打折，放开 Pcrit 后 P 升到 0.092（抑制代价约 20%）；"
                   "③ 0–30 h P 仅 0.006（霉菌建酶），30–120 h 稳步累积——「前缓、中挺、后缓落」。"),
    },
}

CONTROL_NOTES = {
    1: ("容量限制型：以 Xm 为设计目标（孔隙率、含水率、装料量），"
        "产物靠 β 项在稳定期继续累积，放料时机看产物而非菌体。"),
    2: ("水活度型：含水率是比较器，存在最优窗口（约 50%–65%）；"
        "过高结块缺氧、过低抑制生长；用 aw 在线/离线监测替代含水率。"),
    3: ("传热型：ΔT_max≈Y_Q·(μXm/4)/h_A，床层越厚 h_A 越小；"
        "优先降床层，其次强制通风带走热量，再次翻料；通风首先是为散热，其次才是供氧。"),
    4: ("传质型：kLa_eff=kLa0/(1+H/Href) 对 H 双曲衰减，降床层是最高杠杆；"
        "用出口 CO₂ 或床层压差做在线替代量；翻料等于周期性重置 H 与孔隙率。"),
    5: ("混菌型：控制“糖化–发酵”节奏——前期保证霉菌建酶（温度/水分/供氧），"
        "后期控温防乙醇抑制与酸败；续糟/配糟调节入窖酸度与初始糖。"),
}

CONTROL_CASE = {
    "scale": 4,
    "goal": "维持床层氧供给，使产物合成接近浅床水平",
    "cv": "床层有效氧浓度 O₂（或出口 CO₂ 浓度作为替代量）",
    "mv": "通风量、床层高度 H、翻料/搅拌频次",
    "phenomenon": "H 增大 → kLa_eff 按 1/(1+H/Href) 衰减 → f_O2 下降 → 产率塌陷",
    "strategy": ("① 降床层是最高杠杆（双曲衰减，线性增益最大）；"
                 "② 通风优先用于带走热量，其次才是供氧；"
                 "③ 用出口 CO₂ 或床层压差做在线替代量，避免插电极测氧；"
                 "④ 翻料等于周期性重置 H 与孔隙率，是静态床层的必要操作。"),
}


# ---------------------------------------------------------------------------
# 二、动力学方程（严格取自文档）
# ---------------------------------------------------------------------------

def f_aw(p):
    """水活度线性抑制因子，端点归一化。"""
    denom = 1.0 - p["aw_min"]
    if denom <= 0:
        return 1.0
    return max(0.0, (p["aw"] - p["aw_min"]) / denom)


def f_temp(T, p):
    """Rosso 基数温度模型（CTMI）：Topt 处为 1，Tmin/Tmax 处为 0。"""
    Tmin, Topt, Tmax = p["Tmin"], p["Topt"], p["Tmax"]
    if T <= Tmin or T >= Tmax:
        return 0.0
    num = (T - Tmax) * (T - Tmin) ** 2
    den = (Topt - Tmin) * ((Topt - Tmin) * (T - Topt)
                           - (Topt - Tmax) * (Topt + Tmin - 2.0 * T))
    if den == 0:
        return 0.0
    return max(0.0, num / den)


def f_o2(O2, p):
    """氧限制因子（Monod 型）。"""
    return max(0.0, O2) / (p["KO2"] + max(0.0, O2))


def kla_eff(p):
    """有效氧传递系数：随床层深度双曲衰减。"""
    return p["kLa0"] / (1.0 + p["H"] / p["Href"])


def _logistic_mu(X, Xm, mu_max):
    if X >= Xm:
        return 0.0
    return mu_max * (1.0 - X / Xm)


def rhs_scale1(t, y, p):
    X, S, P = y
    mu = _logistic_mu(X, p["Xm"], p["mu_max"])
    dX = mu * X
    dS = -(1.0 / p["Yxs"]) * dX - p["ms"] * X
    dP = p["alpha"] * dX + p["beta"] * X
    return [dX, dS, dP]


def rhs_scale2(t, y, p):
    X, S, P = y
    mu = _logistic_mu(X, p["Xm"], p["mu_max"] * f_aw(p))
    dX = mu * X
    dS = -(1.0 / p["Yxs"]) * dX - p["ms"] * X
    dP = p["alpha"] * dX + p["beta"] * X
    return [dX, dS, dP]


def rhs_scale3(t, y, p):
    X, S, P, T = y
    mu = _logistic_mu(X, p["Xm"], p["mu_max"] * f_aw(p) * f_temp(T, p))
    dX = mu * X
    dS = -(1.0 / p["Yxs"]) * dX - p["ms"] * X
    dP = p["alpha"] * dX + p["beta"] * X
    dT = (p["YQ"] * dX - p["hA"] * (T - p["Tamb"])) / p["Ceff"]
    return [dX, dS, dP, dT]


def rhs_scale4(t, y, p):
    X, S, P, O2, T = y
    mu = _logistic_mu(X, p["Xm"],
                      p["mu_max"] * f_aw(p) * f_temp(T, p) * f_o2(O2, p))
    dX = mu * X
    dS = -(1.0 / p["Yxs"]) * dX - p["ms"] * X
    dP = p["alpha"] * dX + p["beta"] * X
    dO2 = kla_eff(p) * (p["O2star"] - O2) - (1.0 / p["Yox"]) * dX - p["mO2"] * X
    dT = (p["YQ"] * dX - p["hA"] * (T - p["Tamb"])) / p["Ceff"]
    return [dX, dS, dP, dO2, dT]


def rhs_scale5(t, y, p):
    X1, X2, S, G, P = y
    # 霉菌（糖化主体）
    mu1 = _logistic_mu(X1, p["Xm1"], p["mu1"])
    dX1 = mu1 * X1
    # 糖化：酶量正比于霉菌生物量，Monod 型饱和
    vh = p["khkE"] * X1 * max(0.0, S) / (p["Ks"] + max(0.0, S))
    dS = -vh
    # 酵母：受还原糖限制 + 乙醇产物抑制
    p_inhib = max(0.0, 1.0 - P / p["Pcrit"])
    mu2 = (p["mu2"] * max(0.0, G) / (p["KG"] + max(0.0, G))
           * max(0.0, 1.0 - X2 / p["Xm2"]) * p_inhib)
    dX2 = mu2 * X2
    # 乙醇：Luedeking–Piret（生长偶联 + 非生长偶联），整体受乙醇抑制约束
    prod = (p["Ypg"] * dX2 + p["bp"] * X2) * p_inhib
    dP = prod
    # 还原糖：糖化供给 − 生长消耗 − 维持 − 产乙醇消耗
    dG = (vh * p["Ygs"] - (1.0 / p["Yxg"]) * dX2 - p["mG"] * X2
          - prod / p["Ypg"])
    return [dX1, dX2, dS, dG, dP]


RHS = {1: rhs_scale1, 2: rhs_scale2, 3: rhs_scale3, 4: rhs_scale4, 5: rhs_scale5}


STATE_NAMES = {
    1: ["X", "S", "P"],
    2: ["X", "S", "P"],
    3: ["X", "S", "P", "T"],
    4: ["X", "S", "P", "O2", "T"],
    5: ["X1", "X2", "S", "G", "P"],
}


def initial_state(scale, p):
    if scale == 1:
        return [p["X0"], p["S0"], p["P0"]]
    if scale == 2:
        return [p["X0"], p["S0"], p["P0"]]
    if scale == 3:
        return [p["X0"], p["S0"], p["P0"], p["T0"]]
    if scale == 4:
        return [p["X0"], p["S0"], p["P0"], p["O20"], p["T0"]]
    if scale == 5:
        return [p["X10"], p["X20"], p["S0"], p["G0"], p["P0"]]
    raise ValueError("scale 必须为 1..5")


# ---------------------------------------------------------------------------
# 三、数值工具
# ---------------------------------------------------------------------------

def merge_params(scale, overrides):
    p = dict(CASES[scale]["params"])
    for k, v in (overrides or {}).items():
        p[k] = v
    return p


def simulate(scale, p, t_end, y0=None, n=400):
    """返回 (t, Y)。全部 Scale 用自适应求解器（LSODA）。"""
    if solve_ivp is None:
        raise RuntimeError("需要 scipy 才能求解")
    if y0 is None:
        y0 = initial_state(scale, p)
    sol = solve_ivp(RHS[scale], [0.0, t_end], y0, args=(p,), method="LSODA",
                    rtol=1e-8, atol=1e-10, dense_output=True,
                    max_step=t_end / 200.0)
    t = np.linspace(0.0, t_end, n)
    Y = sol.sol(t)
    Y = np.clip(Y, 0.0, None)
    return t, Y


def peak_temperature(scale, p, t_end):
    if scale not in (3, 4):
        return None
    t, Y = simulate(scale, p, t_end)
    return float(np.max(Y[3 if scale == 3 else 4]))


def min_oxygen(scale, p, t_end):
    if scale != 4:
        return None
    t, Y = simulate(scale, p, t_end)
    return float(np.min(Y[3]))


# ---------------------------------------------------------------------------
# 四、绘图
# ---------------------------------------------------------------------------

def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def plot_timeseries(scale, t, Y, p, out_path, title=None):
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.set_ylabel("X / P (g/g DM)")
    ax2 = None

    if scale == 5:
        ax.plot(t, Y[0], label="X1 mold (g/g DM)", color="#1f77b4")
        ax.plot(t, Y[1], label="X2 yeast (g/g DM)", color="#9467bd")
        ax.plot(t, Y[4], label="P ethanol (g/g DM)", color="#ff7f0e")
        ax2 = ax.twinx()
        ax2.plot(t, Y[2], label="S starch (g/g DM)", color="#2ca02c", ls="--")
        ax2.plot(t, Y[3], label="G reducing sugar (g/g DM)", color="#8c564b", ls=":")
        ax2.set_ylabel("S / G (g/g DM)")
    elif scale == 4:
        ax.plot(t, Y[0], label="X biomass (g/g DM)", color="#1f77b4")
        ax.plot(t, Y[2], label="P product (g/g DM)", color="#ff7f0e")
        ax2 = ax.twinx()
        ax2.plot(t, Y[3], label="O2 (g/g DM)", color="#17becf", ls="-.")
        ax2.plot(t, Y[4], label="T (degC)", color="#d62728", ls="--")
        ax2.set_ylabel("O2 (g/g DM) / T (degC)")
    elif scale == 3:
        ax.plot(t, Y[0], label="X biomass (g/g DM)", color="#1f77b4")
        ax.plot(t, Y[2], label="P product (g/g DM)", color="#ff7f0e")
        ax2 = ax.twinx()
        ax2.plot(t, Y[3], label="T (degC)", color="#d62728", ls="--")
        ax2.set_ylabel("T (degC)")
    else:
        ax.plot(t, Y[0], label="X biomass (g/g DM)", color="#1f77b4")
        ax.plot(t, Y[2], label="P product (g/g DM)", color="#ff7f0e")
        ax2 = ax.twinx()
        ax2.plot(t, Y[1], label="S substrate (g/g DM)", color="#2ca02c", ls="--")
        ax2.set_ylabel("S (g/g DM)")

    ax.set_xlabel("time (h)")
    ax.grid(alpha=0.3)
    h1, l1 = ax.get_legend_handles_labels()
    if ax2 is None:
        ax.legend(h1, l1, loc="best", fontsize=8)
    else:
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, loc="best", fontsize=8)
    ax.set_title(title or f"Scale {scale} solid-state fermentation")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_depth_scan(scale, rows, out_path):
    """rows: list of (x, peak_T, min_O2, final_P)，x = Scale4 的 H / Scale3 的 hA"""
    plt = _mpl()
    xs = [r[0] for r in rows]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if scale == 3:
        ax.plot(xs, [r[1] for r in rows], "o-", color="#d62728", label="peak T (degC)")
        ax.axhline(28.0, color="#2ca02c", ls="--", lw=1, label="Topt = 28 degC")
        ax.set_xlabel("effective heat-removal coefficient hA (J/(g*h*K))")
        ax.set_ylabel("peak bed temperature (degC)")
        ax.grid(alpha=0.3)
        ax.legend(loc="best", fontsize=8)
    else:
        ax.plot(xs, [r[2] for r in rows], "o-", color="#17becf", label="min O2 (g/g DM)")
        ax.set_xlabel("bed height H (cm)")
        ax.set_ylabel("minimum O2 (g/g DM)")
        ax2 = ax.twinx()
        ax2.plot(xs, [r[3] for r in rows], "s--", color="#ff7f0e", label="final P")
        ax2.set_ylabel("final product P (g/g DM)")
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, loc="best", fontsize=8)
        ax.grid(alpha=0.3)
    ax.set_title(f"Scale {scale} | sensitivity scan")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 五、文本输出
# ---------------------------------------------------------------------------

PARAM_ORDER = {
    1: ["mu_max", "Xm", "Yxs", "ms", "alpha", "beta", "S0", "X0", "P0"],
    2: ["mu_max", "Xm", "Yxs", "ms", "alpha", "beta", "aw", "aw_min", "S0", "X0"],
    3: ["mu_max", "Xm", "Yxs", "ms", "alpha", "beta", "aw", "aw_min",
        "Tmin", "Topt", "Tmax", "YQ", "hA", "Ceff", "Tamb", "T0", "S0", "X0"],
    4: ["mu_max", "Xm", "Yxs", "ms", "alpha", "beta", "aw", "aw_min",
        "Tmin", "Topt", "Tmax", "YQ", "hA", "Ceff", "Tamb", "T0",
        "kLa0", "Href", "H", "O2star", "KO2", "Yox", "mO2", "O20", "S0", "X0"],
    5: ["mu1", "Xm1", "khkE", "Ks", "Ygs", "mu2", "KG", "Xm2", "Yxg", "mG",
        "Ypg", "bp", "Pcrit", "S0", "G0", "X10", "X20", "P0"],
}


def fmt_params(scale, p):
    keys = PARAM_ORDER[scale]
    parts = []
    for k in keys:
        if k in p:
            v = p[k]
            parts.append(f"{k}={v:g}" if abs(v) < 1e5 else f"{k}={v:.3g}")
    # 每行 6 个，便于阅读
    lines = []
    for i in range(0, len(parts), 6):
        lines.append("  " + "  ".join(parts[i:i + 6]))
    return "\n".join(lines)


def print_control(scale):
    print(f"Scale {scale}｜{SCALES[scale]}")
    print(f"控制要点：{CONTROL_NOTES[scale]}")
    if scale == CONTROL_CASE["scale"]:
        c = CONTROL_CASE
        print("-" * 60)
        print("文档「过程控制实际案例（通用示范）」：")
        print(f"  目标：{c['goal']}")
        print(f"  被控变量：{c['cv']}")
        print(f"  操纵变量：{c['mv']}")
        print(f"  现象：{c['phenomenon']}")
        print(f"  策略：{c['strategy']}")


# ---------------------------------------------------------------------------
# 六、命令实现
# ---------------------------------------------------------------------------

def cmd_list(_a):
    print("模型选择面板（必须手动指定 --scale 1..5）：")
    for k in sorted(SCALES):
        print(f"  Scale {k}：{SCALES[k]}")
    print("\n案例：")
    for k in sorted(CASES):
        print(f"  Scale {k}：{CASES[k]['organism']}")
        print(f"            {CASES[k]['system']}")
    print("\n浓度基准：g/g 干基质（DM），不是 g/L。")
    print("纤维质物料（青贮/堆肥/果渣饲料）请用技能 lignocellulose-conversion。")


def cmd_params(a):
    p = merge_params(a.scale, a.set)
    print(f"Scale {a.scale}｜{SCALES[a.scale]}")
    print(f"案例：{CASES[a.scale]['organism']}")
    print(f"体系：{CASES[a.scale]['system']}")
    print("参数：")
    print(fmt_params(a.scale, p))
    assumed = CASES[a.scale]["assumed"]
    if assumed:
        print(f"演示默认值（文档未给定，可 --set 覆盖）：{', '.join(assumed)}")
    if a.scale == 2:
        print(f"当前 f_aw = {f_aw(p):.3f}")
    if a.scale in (3, 4):
        print(f"当前 f_T(T0) = {f_temp(p['T0'], p):.3f}")
    if a.scale == 4:
        print(f"当前 kLa_eff = {kla_eff(p):.3f} h⁻¹（kLa0={p['kLa0']:g}, H={p['H']:g} cm）")


def cmd_simulate(a):
    p = merge_params(a.scale, a.set)
    t, Y = simulate(a.scale, p, a.tend)
    print(f"Scale {a.scale}｜{SCALES[a.scale]} — 仿真 {a.tend:g} h")
    print("参数：")
    print(fmt_params(a.scale, p))
    names = STATE_NAMES[a.scale]
    n = len(t)
    idx = np.unique(np.linspace(0, n - 1, min(11, n)).astype(int))
    header = "  t(h)   " + "".join(f"{nm:>10s}" for nm in names)
    print(header)
    for i in idx:
        vals = "".join(f"{v:10.4f}" for v in Y[:, i])
        print(f"  {t[i]:6.2f} {vals}")
    yend = Y[:, -1]
    print(f"终点 (t={t[-1]:.2f} h)："
          + ", ".join(f"{nm}={v:.4f}" for nm, v in zip(names, yend)))

    if a.scale in (3, 4):
        Tpk = float(np.max(Y[3 if a.scale == 3 else 4]))
        print(f"峰值床温 T_max = {Tpk:.2f} ℃（Topt={p['Topt']:g}, Tmax={p['Tmax']:g}）")
        if Tpk >= p["Tmax"]:
            print("结论：床层温度触及 Tmax，生长被热抑制完全阻断——必须降床层/强制通风/翻料。")
        elif Tpk > p["Topt"] + 3:
            print("结论：床层显著偏离 Topt，产率受损；建议加强散热。")
        else:
            print("结论：床温接近 Topt，传热不是限制因素。")
    if a.scale == 4:
        O2min = float(np.min(Y[3]))
        print(f"最低氧浓度 O2_min = {O2min:.5f} g/g DM（O2*={p['O2star']:g}）")
        if O2min <= 0.1 * p["O2star"]:
            print("结论：进入氧限制死区，生长基本停滞——必须降床层或提高通风。")
        else:
            print(f"结论：f_O2 最低约 {f_o2(O2min, p):.2f}，供氧{'充足' if f_o2(O2min, p) > 0.8 else '受限'}。")
    if a.scale == 5:
        print(f"乙醇终值 P = {yend[4]:.4f} g/g DM；残淀粉 S = {yend[2]:.4f}；"
              f"残还原糖 G = {yend[3]:.4f}")
        if yend[3] > 0.01:
            print("结论：残还原糖偏高，提示发酵不透（乙醇抑制过强或酵母量不足）。")
        elif yend[2] > 0.20:
            print("结论：还原糖不累积但淀粉未转化完——体系处于糖化限速，"
                  "可延长周期、提高霉菌产酶量或增加麸皮比例。")
        else:
            print("结论：糖化与发酵较匹配，淀粉利用率正常。")

    if a.out:
        plot_timeseries(a.scale, t, Y, p, a.out)
        print(f"已保存曲线：{a.out}")


def cmd_profile(a):
    """床层参数敏感性扫描：Scale 4 扫床高 H，Scale 3 扫有效散热系数 hA。"""
    if a.scale not in (3, 4):
        print("profile 仅适用于 Scale 3（传热）与 Scale 4（传质）。")
        return
    p0 = merge_params(a.scale, a.set)
    if a.scale == 4:
        lo = a.min if a.min is not None else 2.0
        hi = a.max if a.max is not None else 40.0
        sweep_key, unit, label = "H", "cm", "床层高度 H"
    else:
        lo = a.min if a.min is not None else 1.0
        hi = a.max if a.max is not None else 20.0
        sweep_key, unit, label = "hA", "J/(g·h·K)", "有效散热系数 hA"

    vals = np.linspace(lo, hi, a.n)
    rows = []
    print(f"Scale {a.scale}｜{SCALES[a.scale]} — {label} 敏感性扫描")
    print(f"  {sweep_key}({unit})   kLa_eff(h⁻¹)   T_peak(℃)   O2_min(g/g)   f_O2_min   P_final")
    for v in vals:
        p = dict(p0)
        p[sweep_key] = float(v)
        t, Y = simulate(a.scale, p, a.tend)
        if a.scale == 3:
            Tpk = float(np.max(Y[3]))
            O2min, fO2min, kla = float("nan"), float("nan"), float("nan")
        else:
            Tpk = float(np.max(Y[4]))
            O2min = float(np.min(Y[3]))
            fO2min = f_o2(O2min, p)
            kla = kla_eff(p)
        Pf = float(Y[2, -1])
        rows.append((float(v), Tpk, O2min, Pf))
        print(f"  {v:8.2f}       {kla:10.3f}   {Tpk:9.2f}   {O2min:11.5f}   "
              f"{fO2min:8.3f}   {Pf:7.4f}")
    if a.out:
        plot_depth_scan(a.scale, rows, a.out)
        print(f"已保存敏感性扫描图：{a.out}")
    if a.scale == 4:
        print("提示：H 增大 → kLa_eff 按 1/(1+H/Href) 双曲衰减，降床层是最高杠杆。")
    else:
        print("提示：hA 随床层加厚、通风变差而减小；本模型把 hA 当输入参数，"
              "需按具体反应器标定（文档待核实清单第 2 条）。")


def cmd_control(a):
    if a.scale:
        print_control(a.scale)
    else:
        for k in sorted(SCALES):
            print_control(k)
            print("-" * 60)


def cmd_demo(a):
    outdir = a.outdir
    os.makedirs(outdir, exist_ok=True)
    scales = sorted(SCALES) if a.all or not a.scale else [a.scale]
    for s in scales:
        p = merge_params(s, a.set)
        print("=" * 66)
        print(f"Demo · Scale {s}｜{SCALES[s]}")
        print(f"  真实案例：{CASES[s]['organism']}")
        print(f"  体系：{CASES[s]['system']}")
        print("  参数：")
        print(fmt_params(s, p))
        if CASES[s]["assumed"]:
            print(f"  演示默认值（文档未给定）：{', '.join(CASES[s]['assumed'])}")
        print(f"  文档控制结果：{CASES[s]['result']}")

        tend = a.tend or CASES[s]["tend"]
        t, Y = simulate(s, p, tend)
        names = STATE_NAMES[s]
        yend = Y[:, -1]
        print(f"  仿真至 {tend:g} h，终点："
              + ", ".join(f"{nm}={v:.4f}" for nm, v in zip(names, yend)))
        png = os.path.join(outdir, f"scale{s}_timeseries.png")
        plot_timeseries(s, t, Y, p, png, title=f"Scale {s} | {CASES[s]['ascii']}")
        print(f"  曲线：{png}")

        if s == 2:
            # 对照：水活度 0.99 vs 0.90，展示 f_aw 的杠杆
            for aw in (0.99, 0.90):
                p2 = dict(p)
                p2["aw"] = aw
                t2, Y2 = simulate(2, p2, tend)
                png2 = os.path.join(outdir, f"scale2_aw{aw:.2f}.png")
                plot_timeseries(2, t2, Y2, p2, png2,
                                title=f"Scale 2 | aw = {aw:.2f} (f_aw={f_aw(p2):.2f})")
                print(f"  对照（aw={aw:.2f}, f_aw={f_aw(p2):.2f}）：{png2}  "
                      f"终点 X={Y2[0, -1]:.4f}, P={Y2[2, -1]:.4f}")

        if s == 3:
            # 对照：床层 5 cm（hA 大）vs 30 cm（hA 小），展示传热放大瓶颈
            for H, hA in ((5.0, 24.0), (30.0, 3.0)):
                p3 = dict(p)
                p3["hA"] = hA
                t3, Y3 = simulate(3, p3, tend)
                png3 = os.path.join(outdir, f"scale3_bed{H:g}cm.png")
                plot_timeseries(3, t3, Y3, p3, png3,
                                title=f"Scale 3 | bed {H:g} cm (hA={hA:g})")
                print(f"  对照（床层 {H:g} cm, hA={hA:g}）：{png3}  "
                      f"T_peak={np.max(Y3[3]):.2f} ℃, P={Y3[2, -1]:.4f}")

        if s == 4:
            # 对照：床层 5 cm vs 30 cm，展示传质放大瓶颈
            for H in (5.0, 30.0):
                p4 = dict(p)
                p4["H"] = H
                t4, Y4 = simulate(4, p4, tend)
                png4 = os.path.join(outdir, f"scale4_bed{H:g}cm.png")
                plot_timeseries(4, t4, Y4, p4, png4,
                                title=f"Scale 4 | bed {H:g} cm (kLa_eff={kla_eff(p4):.2f})")
                print(f"  对照（床层 {H:g} cm, kLa_eff={kla_eff(p4):.2f}）：{png4}  "
                      f"O2_min={np.min(Y4[3]):.5f}, P={Y4[2, -1]:.4f}")
            if a.profile:
                bp = os.path.join(outdir, "scale4_depth_scan.png")
                rows = []
                for H in np.linspace(2.0, 40.0, 12):
                    pp = dict(p)
                    pp["H"] = float(H)
                    tt, YY = simulate(4, pp, tend)
                    rows.append((float(H), float(np.max(YY[4])),
                                 float(np.min(YY[3])), float(YY[2, -1])))
                plot_depth_scan(4, rows, bp)
                print(f"  深度扫描图：{bp}")

        if s == 5:
            # 对照：无乙醇抑制（Pcrit 很大）vs 有抑制，展示产物抑制的截断作用
            for pc, tag in ((1e6, "no-inhibition"), (p["Pcrit"], "Pcrit=0.12")):
                p5 = dict(p)
                p5["Pcrit"] = pc
                t5, Y5 = simulate(5, p5, tend)
                png5 = os.path.join(outdir, f"scale5_{tag}.png")
                plot_timeseries(5, t5, Y5, p5, png5,
                                title=f"Scale 5 | {tag}")
                print(f"  对照（{tag}）：{png5}  "
                      f"P={Y5[4, -1]:.4f}, 残糖 G={Y5[3, -1]:.4f}")

        print_control(s)
    print("=" * 66)
    print(f"演示完成，图片输出目录：{outdir}")


# ---------------------------------------------------------------------------
# 七、CLI
# ---------------------------------------------------------------------------

def parse_set(pairs):
    out = {}
    for item in pairs or []:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"--set 需为 key=value：{item}")
        k, v = item.split("=", 1)
        try:
            out[k.strip()] = float(v)
        except ValueError:
            raise argparse.ArgumentTypeError(f"--set 的 value 必须是数字：{item}")
    return out


def build_parser():
    ap = argparse.ArgumentParser(
        description="五级递进固态发酵（SSF）动力学模型引擎（双入口）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("纪律约定")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    LEVELS = list(range(1, 6))

    def add_common(sp, need_scale=True):
        if need_scale:
            sp.add_argument("--scale", type=int, choices=LEVELS, required=True,
                            help="手动指定模型 Scale（1..5）")
        sp.add_argument("--set", action="append", default=[], metavar="K=V",
                        help="覆盖参数，可重复，如 --set H=10 --set aw=0.97")

    p = sub.add_parser("list", help="列出模型面板与案例")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("params", help="查看某 Scale 的案例参数")
    add_common(p)
    p.set_defaults(func=cmd_params)

    p = sub.add_parser("simulate", help="入口一：时程仿真")
    add_common(p)
    p.add_argument("--tend", type=float, default=72.0, help="仿真时长 h（默认 72）")
    p.add_argument("--out", default=None, help="保存曲线 PNG")
    p.set_defaults(func=cmd_simulate)

    p = sub.add_parser("profile", help="入口一：床层参数敏感性扫描（Scale 3 扫 hA / Scale 4 扫 H）")
    add_common(p)
    p.add_argument("--min", type=float, default=None,
                   help="扫描下限（Scale4: H 默认 2 cm；Scale3: hA 默认 1）")
    p.add_argument("--max", type=float, default=None,
                   help="扫描上限（Scale4: H 默认 40 cm；Scale3: hA 默认 20）")
    p.add_argument("--n", type=int, default=10, help="扫描点数（默认 10）")
    p.add_argument("--tend", type=float, default=72.0, help="每次仿真时长 h（默认 72）")
    p.add_argument("--out", default=None, help="保存敏感性扫描图 PNG")
    p.set_defaults(func=cmd_profile)

    p = sub.add_parser("control", help="入口一：控制要点/策略")
    p.add_argument("--scale", type=int, choices=LEVELS, default=None,
                   help="指定 Scale；省略则输出全部")
    p.set_defaults(func=cmd_control)

    p = sub.add_parser("demo", help="入口二：真实案例 Demo 演示")
    p.add_argument("--scale", type=int, choices=LEVELS, default=None)
    p.add_argument("--all", action="store_true", help="演示全部 5 个 Scale")
    p.add_argument("--set", action="append", default=[], metavar="K=V")
    p.add_argument("--outdir", default="ssf_demo", help="图片输出目录")
    p.add_argument("--tend", type=float, default=None, help="覆盖各 Scale 默认仿真时长")
    p.add_argument("--profile", action="store_true", help="Scale4 附加深度扫描图")
    p.set_defaults(func=cmd_demo)


    return ap


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    if getattr(a, "set", None):
        a.set = parse_set(a.set)
    a.func(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
