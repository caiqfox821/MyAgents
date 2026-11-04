#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五级递进恒化发酵动力学模型引擎
================================
归属：食品发酵专家私有技能（chemostat-dynamics）

双入口
------
入口一 · 模型预测计算：list / params / simulate / steady / bifurcation / control
入口二 · 案例 Demo 演示：demo

纪律约定（照《五级递进恒化发酵动力学模型》文档执行）
----------------------------------------------------
1. 只实现 Scale 1–5 文档给出的方程、参数与案例；不新增任何动力学机制
   （不引入维持系数、Luedeking–Piret、氧传递等额外项）。
2. 模型必须由用户手动指定 --scale（1..5），脚本不擅自替用户选型。
3. 文档未给出的数值（如 Scale 3/5 的部分参数、各 Scale 的 S0）一律使用
   明确标注的“演示默认值”，可用 --set key=value 覆盖；这些默认值只用于
   让方程可数值求解，不构成新的动力学假设。

参数覆盖
--------
--set key=value 可重复，例如： --set mu_max=0.40 --set D=0.20 --set S0=12
"""
from __future__ import annotations

import argparse
import os
import sys
import math

import numpy as np

try:
    from scipy.integrate import solve_ivp
    from scipy.optimize import brentq
except Exception:  # pragma: no cover
    solve_ivp = None
    brentq = None


# ---------------------------------------------------------------------------
# 二、模型面板与案例参数
# ---------------------------------------------------------------------------

SCALES = {
    1: "Monod 基础恒化模型（无抑制，单菌）",
    2: "Haldane 底物抑制恒化模型（底物高浓度抑制）",
    3: "双菌种竞争恒化模型（两菌竞争同一底物）",
    4: "产物抑制单菌恒化模型（代谢产物抑制菌体生长）",
    5: "带代谢时滞单菌恒化模型（代谢响应存在迟滞）",
}

# 真实示范案例（来自文档）
CASES = {
    1: {
        "organism": "酿酒酵母 Saccharomyces cerevisiae",
        "ascii": "S. cerevisiae",
        "substrate": "葡萄糖（好氧恒化，30℃，pH 5.0，通气充足）",
        "params": {"mu_max": 0.45, "Ks": 0.08, "Yxs": 0.42, "S0": 10.0, "D": 0.25},
        "assumed": ["S0"],
        "result": ("调节稀释率 D，在 0.1~0.35 h⁻¹ 区间稳定稳态；"
                   "D 超过临界稀释率，菌体洗出。"),
    },
    2: {
        "organism": "醋酸杆菌 Acetobacter aceti",
        "ascii": "A. aceti",
        "substrate": "葡萄糖（高糖发酵产乙酸，28℃，pH 6.0，充分好氧）",
        "params": {"mu_max": 0.32, "Ks": 0.12, "Ki": 18.0, "Yxs": 0.35,
                   "S0": 30.0, "D": 0.15},
        "assumed": ["S0", "D"],
        "result": ("存在两个稳态分支；底物过高，生长速率反而下降；"
                   "工艺上需要控制进料糖浓度，避免强抑制。"),
    },
    3: {
        "organism": "大肠杆菌 Escherichia coli（菌株1） vs 假单胞菌 Pseudomonas sp.（菌株2）",
        "ascii": "E. coli vs Pseudomonas",
        "substrate": "葡萄糖（37℃，好氧恒化）",
        "params": {"mu_max1": 0.70, "Ks1": 0.020, "Yxs1": 0.50,
                   "mu_max2": 0.50, "Ks2": 0.005, "Yxs2": 0.45,
                   "S0": 10.0, "D": 0.20},
        "assumed": ["mu_max1", "Ks1", "Yxs1", "mu_max2", "Ks2", "Yxs2", "S0", "D"],
        "result": ("K_S 更小的菌株在低底物稳态下占优势（竞争排斥原理）；"
                   "通过调节稀释率 D，可以选择性保留其中一株，实现菌群定向筛选。"),
    },
    4: {
        "organism": "干酪乳杆菌 Lactobacillus casei（产乳酸，兼性好氧）",
        "ascii": "L. casei",
        "substrate": "葡萄糖（产乳酸）",
        "params": {"mu_max": 0.30, "Ks": 0.15, "Pcrit": 75.0, "Ypx": 2.2,
                   "Yxs": 0.15, "S0": 50.0, "D": 0.10},
        "assumed": ["Yxs", "S0", "D"],
        "result": ("产物累积会压低比生长速率；连续发酵需要原位产物分离，"
                   "解除产物抑制才能持续高产。"),
    },
    5: {
        "organism": "里氏木霉 Trichoderma reesei（纤维素好氧发酵产纤维素酶）",
        "ascii": "T. reesei",
        "substrate": "纤维素（28℃，恒化纤维底物培养）",
        "params": {"mu_max": 0.25, "Ks": 1.00, "Yxs": 0.40,
                   "tau": 1.2, "S0": 15.0, "D": 0.12},
        "assumed": ["mu_max", "Ks", "Yxs", "S0", "D"],
        "result": ("时滞会诱发系统振荡；简单的 PID 控制容易超调；"
                   "需要预测控制、滞后补偿方案。"),
    },
}

# 过程控制实际案例（文档给出，以 Scale 2 为例）
CONTROL_CASE = {
    "scale": 2,
    "goal": "稳定菌体浓度，规避底物抑制",
    "cv": "生物量 X",
    "mv": "进料底物浓度 S0 或稀释率 D",
    "phenomenon": "高 S0 触发抑制，稳态多解",
    "strategy": ("分级控制；先小 D 低底物启动，缓慢抬升进料浓度；"
                 "禁止一次性高底物进料；监测底物在线浓度作为前馈信号。"),
}

CONTROL_NOTES = {
    1: "以 D 为操纵变量，将 D 稳定在临界稀释率以下（D < D_crit），在线监测 X 防止洗出。",
    2: ("底物抑制型：先小 D 低底物启动，缓慢抬升进料浓度；禁止一次性高底物进料；"
        "以在线底物浓度作前馈，规避多稳态与抑制区。"),
    3: "竞争型：以 D 为筛选杠杆，选择性保留低 K_S（低临界底物）菌株；在线监测两菌比例。",
    4: "产物抑制型：控制 P < P_crit，并采用原位产物分离（膜/渗透气化）解除产物抑制，维持高产。",
    5: "时滞型：避免纯 PID（易超调、振荡），采用预测控制/滞后补偿（如 Smith 预估器）。",
}


# ---------------------------------------------------------------------------
# 三、动力学方程（严格取自文档）
# ---------------------------------------------------------------------------

def mu_monod(S, p):
    return p["mu_max"] * S / (p["Ks"] + S)


def mu_haldane(S, p):
    return p["mu_max"] * S / (p["Ks"] + S + S * S / p["Ki"])


def mu_product(S, P, p):
    return p["mu_max"] * S / (p["Ks"] + S) * max(0.0, 1.0 - P / p["Pcrit"])


def rhs_scale1(t, y, p):
    X, S = y
    mu = mu_monod(S, p)
    return [(mu - p["D"]) * X,
            p["D"] * (p["S0"] - S) - mu * X / p["Yxs"]]


def rhs_scale2(t, y, p):
    X, S = y
    mu = mu_haldane(S, p)
    return [(mu - p["D"]) * X,
            p["D"] * (p["S0"] - S) - mu * X / p["Yxs"]]


def rhs_scale3(t, y, p):
    X1, X2, S = y
    m1 = p["mu_max1"] * S / (p["Ks1"] + S)
    m2 = p["mu_max2"] * S / (p["Ks2"] + S)
    return [(m1 - p["D"]) * X1,
            (m2 - p["D"]) * X2,
            p["D"] * (p["S0"] - S) - m1 * X1 / p["Yxs1"] - m2 * X2 / p["Yxs2"]]


def rhs_scale4(t, y, p):
    X, S, P = y
    mu = mu_product(S, P, p)
    return [(mu - p["D"]) * X,
            p["D"] * (p["S0"] - S) - mu * X / p["Yxs"],
            mu * X * p["Ypx"] - p["D"] * P]


RHS = {1: rhs_scale1, 2: rhs_scale2, 3: rhs_scale3, 4: rhs_scale4}


def initial_state(scale, p):
    if scale == 1:
        return [0.05, p["S0"]]
    if scale == 2:
        return [0.05, p["S0"]]
    if scale == 3:
        return [0.05, 0.05, p["S0"]]
    if scale == 4:
        return [0.05, p["S0"], 0.0]
    if scale == 5:
        return [0.05, p["S0"]]
    raise ValueError("scale 必须为 1..5")


# ---------------------------------------------------------------------------
# 四、数值工具
# ---------------------------------------------------------------------------

def merge_params(scale, overrides):
    p = dict(CASES[scale]["params"])
    for k, v in (overrides or {}).items():
        p[k] = v
    return p


def d_crit(scale, p):
    """临界稀释率：超过则菌体洗出（仅对单菌 Monod 形态给出解析值）。"""
    if scale in (1, 5):
        return p["mu_max"] * p["S0"] / (p["Ks"] + p["S0"])
    if scale == 2:
        # 洗出发生在 S*=S0，即 μ(S0)=D
        return mu_haldane(p["S0"], p)
    if scale == 4:
        return mu_product(p["S0"], 0.0, p)
    if scale == 3:
        return None
    return None


def jacobian(rhs, y, p, eps=1e-6):
    y = np.asarray(y, dtype=float)
    n = len(y)
    J = np.zeros((n, n))
    f0 = np.asarray(rhs(0.0, y, p), dtype=float)
    for j in range(n):
        yp = y.copy()
        yp[j] += eps
        J[:, j] = (np.asarray(rhs(0.0, yp, p), dtype=float) - f0) / eps
    return J


def classify_stability(rhs, y, p):
    try:
        ev = np.linalg.eigvals(jacobian(rhs, y, p))
        maxre = float(np.max(ev.real))
        return maxre < -1e-7, maxre
    except Exception:
        return None, None


def steady_states(scale, p):
    """返回该 Scale 的全部稳态（解析/数值）。每个元素为 dict。"""
    states = []
    S0 = p["S0"]
    D = p["D"]

    if scale in (1, 5):
        # 洗出态
        states.append({"y": [0.0, S0], "label": "洗出态 (washout)"})
        if D < p["mu_max"]:
            Ss = p["Ks"] * D / (p["mu_max"] - D)
            if 0 < Ss < S0:
                Xs = p["Yxs"] * (S0 - Ss)
                states.append({"y": [Xs, Ss], "label": "非平凡稳态 (μ = D)"})

    elif scale == 2:
        states.append({"y": [0.0, S0], "label": "洗出态 (washout)"})
        # D/Ki * S^2 + (D - mu_max) * S + D*Ks = 0
        a = D / p["Ki"]
        b = D - p["mu_max"]
        c = D * p["Ks"]
        disc = b * b - 4 * a * c
        if disc >= 0:
            for Ss in sorted([(-b - math.sqrt(disc)) / (2 * a),
                              (-b + math.sqrt(disc)) / (2 * a)]):
                if 0 < Ss < S0:
                    Xs = p["Yxs"] * (S0 - Ss)
                    states.append({"y": [Xs, Ss],
                                   "label": "非平凡稳态 (μ(S) = D)"})

    elif scale == 3:
        states.append({"y": [0.0, 0.0, S0], "label": "洗出态 (washout)"})
        for name, mm, ks, ys in (("菌株1", "mu_max1", "Ks1", "Yxs1"),
                                 ("菌株2", "mu_max2", "Ks2", "Yxs2")):
            if D < p[mm]:
                Ss = p[ks] * D / (p[mm] - D)
                if 0 < Ss < S0:
                    Xi = p[ys] * (S0 - Ss)
                    if name == "菌株1":
                        states.append({"y": [Xi, 0.0, Ss], "label": "仅菌株1存活"})
                    else:
                        states.append({"y": [0.0, Xi, Ss], "label": "仅菌株2存活"})
        # 共存需 S*_1 == S*_2（测度为零），此处只做提示不做求解
        b1 = p["Ks1"] * D / (p["mu_max1"] - D) if D < p["mu_max1"] else None
        b2 = p["Ks2"] * D / (p["mu_max2"] - D) if D < p["mu_max2"] else None

    elif scale == 4:
        states.append({"y": [0.0, S0, 0.0], "label": "洗出态 (washout)"})
        # μ(S,P)=D, X=Yxs(S0-S), P=Ypx*X
        def g(S):
            X = p["Yxs"] * (S0 - S)
            P = p["Ypx"] * X
            return mu_product(S, P, p) - D
        grid = np.linspace(1e-6, S0 - 1e-6, 2000)
        vals = np.array([g(s) for s in grid])
        roots = []
        for i in range(len(grid) - 1):
            if vals[i] == 0:
                roots.append(grid[i])
            elif vals[i] * vals[i + 1] < 0:
                roots.append(brentq(g, grid[i], grid[i + 1]))
        for Ss in roots:
            if 0 < Ss < S0:
                Xs = p["Yxs"] * (S0 - Ss)
                Ps = p["Ypx"] * Xs
                states.append({"y": [Xs, Ss, Ps],
                               "label": "非平凡稳态 (μ = D)"})

    # 稳定性（Scale 5 有时滞，此处不判）
    if scale in RHS:
        for st in states:
            s, maxre = classify_stability(RHS[scale], st["y"], p)
            st["stable"] = s
            st["maxre"] = maxre
    for st in states:
        st.setdefault("stable", None)
        st.setdefault("maxre", None)
    return states


# ---------------------------------------------------------------------------
# 五、积分器
# ---------------------------------------------------------------------------

def simulate(scale, p, t_end, dt=None, y0=None):
    """返回 (t, Y)。Scale 5 用固定步长 RK4 + 时滞缓冲，其余用 solve_ivp。"""
    if scale == 5:
        return _simulate_delay(p, t_end, dt or 0.005, y0)

    if y0 is None:
        y0 = initial_state(scale, p)
    if solve_ivp is None:
        raise RuntimeError("需要 scipy 才能求解 Scale 1–4")
    # 事件：底物/菌体触零即停止，避免入负
    def ev_washout(t, y):
        return y[0]
    ev_washout.terminal = True
    ev_washout.direction = -1
    sol = solve_ivp(RHS[scale], [0.0, t_end], y0, args=(p,), method="LSODA",
                    rtol=1e-8, atol=1e-10, dense_output=True, max_step=t_end / 50.0)
    n = 400
    t = np.linspace(0.0, t_end, n)
    Y = sol.sol(t)
    Y = np.clip(Y, 0.0, None)
    return t, Y


def _simulate_delay(p, t_end, dt, y0=None):
    nsteps = int(round(t_end / dt))
    t = np.arange(nsteps + 1) * dt
    X = np.empty(nsteps + 1)
    S = np.empty(nsteps + 1)
    X[0], S[0] = initial_state(5, p) if y0 is None else y0
    tau_idx = max(1, int(round(p["tau"] / dt)))
    S_hist0 = S[0]

    def delayed_S(i):
        j = i - tau_idx
        return S_hist0 if j < 0 else S[j]

    for i in range(nsteps):
        Sd = delayed_S(i)
        mu = mu_monod(Sd, p)

        def f(Xv, Sv):
            dX = (mu - p["D"]) * Xv
            dS = p["D"] * (p["S0"] - Sv) - mu * Xv / p["Yxs"]
            return dX, dS

        Xa, Sa = X[i], S[i]
        k1 = f(Xa, Sa)
        k2 = f(Xa + 0.5 * dt * k1[0], Sa + 0.5 * dt * k1[1])
        k3 = f(Xa + 0.5 * dt * k2[0], Sa + 0.5 * dt * k2[1])
        k4 = f(Xa + dt * k3[0], Sa + dt * k3[1])
        X[i + 1] = max(0.0, Xa + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]))
        S[i + 1] = max(0.0, Sa + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]))
    return t, np.vstack([X, S])


# ---------------------------------------------------------------------------
# 六、绘图
# ---------------------------------------------------------------------------

def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def plot_timeseries(scale, t, Y, p, out_path, title=None):
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if scale == 3:
        ax.plot(t, Y[0], label="X1 (strain 1)", color="#1f77b4")
        ax.plot(t, Y[1], label="X2 (strain 2)", color="#d62728")
        ax2 = ax.twinx()
        ax2.plot(t, Y[2], label="S (substrate)", color="#2ca02c", ls="--")
        ax2.set_ylabel("S (g/L)", color="#2ca02c")
    elif scale == 4:
        ax.plot(t, Y[0], label="X (biomass)", color="#1f77b4")
        ax.plot(t, Y[2], label="P (product)", color="#ff7f0e")
        ax2 = ax.twinx()
        ax2.plot(t, Y[1], label="S (substrate)", color="#2ca02c", ls="--")
        ax2.set_ylabel("S (g/L)", color="#2ca02c")
    else:
        ax.plot(t, Y[0], label="X (biomass)", color="#1f77b4")
        ax2 = ax.twinx()
        ax2.plot(t, Y[1], label="S (substrate)", color="#2ca02c", ls="--")
        ax2.set_ylabel("S (g/L)", color="#2ca02c")
    ax.set_xlabel("time (h)")
    ax.set_ylabel("X / P (g/L)")
    ax.grid(alpha=0.3)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="best", fontsize=8)
    ax.set_title(title or f"Scale {scale} chemostat dynamics")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_bifurcation(scale, p, out_path, Dmax=None):
    plt = _mpl()
    if Dmax is None:
        if scale in (1, 5):
            Dmax = p["mu_max"] * 1.05
        elif scale == 2:
            Dmax = mu_haldane(math.sqrt(p["Ks"] * p["Ki"]), p) * 1.1
        elif scale == 4:
            Dmax = mu_product(p["S0"], 0.0, p) * 1.05
        else:
            Dmax = max(p["mu_max1"], p["mu_max2"]) * 1.05
    Ds = np.linspace(1e-4, Dmax, 400)
    fig, (axS, axX) = plt.subplots(1, 2, figsize=(11, 4.5), sharex=True)
    for D in Ds:
        pp = dict(p)
        pp["D"] = D
        for st in steady_states(scale, pp):
            y = st["y"]
            X = y[0] if scale != 3 else y[0] + y[1]
            S = y[1] if scale != 3 else y[2]
            stable = bool(st["stable"])
            color = "#1f77b4" if stable else "#d62728"
            marker = "o" if stable else "x"
            axS.scatter(D, S, s=6, color=color, marker=marker)
            axX.scatter(D, X, s=6, color=color, marker=marker)
    axS.set_xlabel("dilution rate D (1/h)")
    axS.set_ylabel("substrate S* (g/L)")
    axS.set_title("steady substrate")
    axX.set_xlabel("dilution rate D (1/h)")
    axX.set_ylabel("biomass X* (g/L)")
    axX.set_title("steady biomass")
    for ax in (axS, axX):
        ax.grid(alpha=0.3)
    axS.scatter([], [], color="#1f77b4", marker="o", label="stable")
    axS.scatter([], [], color="#d62728", marker="x", label="unstable")
    axS.legend(loc="best", fontsize=8)
    fig.suptitle(f"Scale {scale} bifurcation vs dilution rate")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 七、文本输出
# ---------------------------------------------------------------------------

def fmt_params(scale, p):
    order = {
        1: ["mu_max", "Ks", "Yxs", "S0", "D"],
        2: ["mu_max", "Ks", "Ki", "Yxs", "S0", "D"],
        3: ["mu_max1", "Ks1", "Yxs1", "mu_max2", "Ks2", "Yxs2", "S0", "D"],
        4: ["mu_max", "Ks", "Pcrit", "Ypx", "Yxs", "S0", "D"],
        5: ["mu_max", "Ks", "Yxs", "tau", "S0", "D"],
    }[scale]
    return "  " + "  ".join(f"{k}={p[k]:g}" for k in order if k in p)


def print_steady(scale, p):
    print(f"Scale {scale}｜{SCALES[scale]}")
    print(f"案例：{CASES[scale]['organism']}")
    print(f"参数：{fmt_params(scale, p)}")
    dc = d_crit(scale, p)
    if dc is not None:
        print(f"临界稀释率 D_crit（洗出阈值）≈ {dc:.4f} h⁻¹；当前 D={p['D']:g} h⁻¹")
    print("稳态解：")
    for st in steady_states(scale, p):
        y = st["y"]
        kind = {3: "X1,X2,S", 4: "X,S,P"}.get(scale, "X,S")
        vals = ", ".join(f"{v:.4f}" for v in y)
        tag = {True: "稳定", False: "不稳定", None: "未判"}[st["stable"]]
        print(f"  - {st['label']:<22} [{kind}] = {vals}   ({tag})")
    if scale == 2:
        print("  注：非平凡稳态出现两支即文档所述「稳态多解 / 双稳态分支」。")


def print_control(scale):
    print(f"Scale {scale}｜{SCALES[scale]}")
    print(f"控制要点：{CONTROL_NOTES[scale]}")
    if scale == CONTROL_CASE["scale"]:
        c = CONTROL_CASE
        print("-" * 52)
        print("文档「过程控制实际案例（通用示范）」：")
        print(f"  目标：{c['goal']}")
        print(f"  被控变量：{c['cv']}；操纵变量：{c['mv']}")
        print(f"  现象：{c['phenomenon']}")
        print(f"  策略：{c['strategy']}")


# ---------------------------------------------------------------------------
# 八、命令实现
# ---------------------------------------------------------------------------

def cmd_list(_a):
    print("模型选择面板（必须手动指定 --scale 1..5）：")
    for k in sorted(SCALES):
        print(f"  Scale {k}：{SCALES[k]}")
    print("\n案例：")
    for k in sorted(CASES):
        print(f"  Scale {k}：{CASES[k]['organism']}")


def cmd_params(a):
    p = merge_params(a.scale, a.set)
    print(f"Scale {a.scale}｜{SCALES[a.scale]}")
    print(f"案例：{CASES[a.scale]['organism']}；底物/条件：{CASES[a.scale]['substrate']}")
    print(f"参数：{fmt_params(a.scale, p)}")
    assumed = CASES[a.scale]["assumed"]
    if assumed:
        print(f"演示默认值（文档未给定，可 --set 覆盖）：{', '.join(assumed)}")


def cmd_simulate(a):
    p = merge_params(a.scale, a.set)
    t, Y = simulate(a.scale, p, a.tend, a.dt)
    print(f"Scale {a.scale}｜{SCALES[a.scale]} — 仿真 {a.tend:g} h")
    print(f"参数：{fmt_params(a.scale, p)}")
    # 打印若干采样点
    n = len(t)
    idx = np.unique(np.linspace(0, n - 1, min(11, n)).astype(int))
    kind = {3: "X1/X2/S", 4: "X/S/P"}.get(a.scale, "X/S")
    print(f"  t(h)      {kind}")
    for i in idx:
        vals = "  ".join(f"{v:8.4f}" for v in Y[:, i])
        print(f"  {t[i]:6.2f}  {vals}")
    yend = Y[:, -1]
    print(f"终点 (t={t[-1]:.2f} h)：{', '.join(f'{v:.4f}' for v in yend)}")
    dc = d_crit(a.scale, p)
    if dc is not None:
        if p["D"] >= dc:
            print(f"结论：D={p['D']:g} ≥ D_crit≈{dc:.4f}，预计菌体洗出。")
        else:
            print(f"结论：D={p['D']:g} < D_crit≈{dc:.4f}，可维持稳态。")
    if a.scale == 5:
        print("提示：时滞体系可能出现衰减振荡；可用 --set tau=… 对比不同时滞。")
    if a.out:
        plot_timeseries(a.scale, t, Y, p, a.out)
        print(f"已保存曲线：{a.out}")


def cmd_steady(a):
    p = merge_params(a.scale, a.set)
    print_steady(a.scale, p)


def cmd_bifurcation(a):
    p = merge_params(a.scale, a.set)
    print(f"Scale {a.scale}｜{SCALES[a.scale]} — 稀释率 D 分岔扫描")
    print(f"参数：{fmt_params(a.scale, p)}")
    if a.out:
        plot_bifurcation(a.scale, p, a.out, a.dmax)
        print(f"已保存分岔图：{a.out}  （o=稳定，x=不稳定）")
    else:
        print("（未指定 --out，仅打印扫描摘要）")
        base = p["D"]
        for D in (0.05, 0.1, 0.2, 0.3, 0.4):
            pp = dict(p)
            pp["D"] = D
            sts = [st for st in steady_states(a.scale, pp) if st["y"][0] > 1e-9 or (a.scale == 3 and st["y"][1] > 1e-9)]
            n_triv = len(sts)
            print(f"  D={D:g}: 非平凡稳态 {n_triv} 个")


def cmd_control(a):
    if a.scale:
        print_control(a.scale)
    else:
        for k in sorted(SCALES):
            print_control(k)
            print("-" * 52)


def cmd_demo(a):
    outdir = a.outdir
    os.makedirs(outdir, exist_ok=True)
    scales = sorted(SCALES) if a.all or not a.scale else [a.scale]
    for s in scales:
        p = merge_params(s, a.set)
        print("=" * 60)
        print(f"Demo · Scale {s}｜{SCALES[s]}")
        print(f"  真实案例：{CASES[s]['organism']}")
        print(f"  底物/条件：{CASES[s]['substrate']}")
        print(f"  参数：{fmt_params(s, p)}")
        if CASES[s]["assumed"]:
            print(f"  演示默认值（文档未给定）：{', '.join(CASES[s]['assumed'])}")
        print(f"  文档控制结果：{CASES[s]['result']}")
        # 仿真
        tend = {1: 60, 2: 80, 3: 60, 4: 120, 5: 200}[s]
        t, Y = simulate(s, p, tend, None if a.dt is None else a.dt)
        yend = Y[:, -1]
        print(f"  仿真至 {tend} h，终点：{', '.join(f'{v:.4f}' for v in yend)}")
        png = os.path.join(outdir, f"scale{s}_timeseries.png")
        plot_timeseries(s, t, Y, p, png, title=f"Scale {s} | {CASES[s]['ascii']}")
        print(f"  曲线：{png}")
        if s == 2:
            # 对照：分级启动——降低进料底物浓度 S0（对应文档控制案例“先小D低底物启动”）
            p2 = dict(p)
            p2["S0"] = 5.0
            t2, Y2 = simulate(2, p2, tend, a.dt)
            png2 = os.path.join(outdir, "scale2_staged_S0.png")
            plot_timeseries(2, t2, Y2, p2, png2,
                            title="Scale 2 | staged feed S0=5 (vs high S0 washout)")
            print(f"  对照（分级进料 S0=5）：{png2}  终点 "
                  f"{', '.join(f'{v:.4f}' for v in Y2[:, -1])}")
            if a.bifurcation:
                bp = os.path.join(outdir, "scale2_bifurcation.png")
                plot_bifurcation(2, p, bp)
                print(f"  分岔图：{bp}")
        if s == 5:
            # 对照：无时滞 / 小时滞，展示时滞诱发的振荡
            for tau in (0.2, 5.0):
                ptu = dict(p)
                ptu["tau"] = tau
                t3, Y3 = simulate(5, ptu, tend, a.dt)
                png3 = os.path.join(outdir, f"scale5_tau{tau:g}.png")
                plot_timeseries(5, t3, Y3, ptu, png3,
                                title=f"Scale 5 | tau = {tau:g} h")
                print(f"  对照（tau={tau:g} h）：{png3}")
        print_control(s)
    print("=" * 60)
    print(f"演示完成，图片输出目录：{outdir}")


# ---------------------------------------------------------------------------
# 九、CLI
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
        description="五级递进恒化发酵动力学模型引擎（双入口）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("纪律约定")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_common(sp, need_scale=True):
        if need_scale:
            sp.add_argument("--scale", type=int, choices=[1, 2, 3, 4, 5], required=True,
                            help="手动指定模型 Scale（1..5）")
        sp.add_argument("--set", action="append", default=[], metavar="K=V",
                        help="覆盖参数，可重复，如 --set D=0.2 --set S0=12")

    p = sub.add_parser("list", help="列出模型面板与案例")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("params", help="查看某 Scale 的案例参数")
    add_common(p)
    p.set_defaults(func=cmd_params)

    p = sub.add_parser("simulate", help="入口一：时程仿真")
    add_common(p)
    p.add_argument("--tend", type=float, default=60.0, help="仿真时长 h（默认 60）")
    p.add_argument("--dt", type=float, default=None, help="Scale5 积分步长 h（默认 0.005）")
    p.add_argument("--out", default=None, help="保存曲线 PNG")
    p.set_defaults(func=cmd_simulate)

    p = sub.add_parser("steady", help="入口一：稳态求解与稳定性")
    add_common(p)
    p.set_defaults(func=cmd_steady)

    p = sub.add_parser("bifurcation", help="入口一：稀释率分岔扫描")
    add_common(p)
    p.add_argument("--dmax", type=float, default=None, help="D 扫描上限")
    p.add_argument("--out", default=None, help="保存分岔图 PNG")
    p.set_defaults(func=cmd_bifurcation)

    p = sub.add_parser("control", help="入口一：控制要点/策略")
    p.add_argument("--scale", type=int, choices=[1, 2, 3, 4, 5], default=None,
                   help="指定 Scale；省略则输出全部")
    p.set_defaults(func=cmd_control)

    p = sub.add_parser("demo", help="入口二：真实案例 Demo 演示")
    p.add_argument("--scale", type=int, choices=[1, 2, 3, 4, 5], default=None)
    p.add_argument("--all", action="store_true", help="演示全部 5 个 Scale")
    p.add_argument("--set", action="append", default=[], metavar="K=V")
    p.add_argument("--outdir", default="chemostat_demo", help="图片输出目录")
    p.add_argument("--bifurcation", action="store_true", help="Scale2 附加分岔图")
    p.add_argument("--dt", type=float, default=None)
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
