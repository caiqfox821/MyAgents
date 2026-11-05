#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六级递进纤维质物料转化动力学模型引擎
====================================
归属：发酵专家私有技能（lignocellulose-conversion）

建模对象：青贮饲料、好氧堆肥、果渣饲料化——共同点是**纤维质物料**的厌氧/好氧转化，
核心是**不可溶膳食纤维（IDF）按 Van Soest NDF/ADF/ADL 三组分分级降解**。

六级递进（可降解性链）
----------------------
1. 青贮基础厌氧发酵：LAB 产乳酸 + pH 自抑 + 缓冲能力
2. 纤维分级降解：半纤维素/纤维素分级速率 + 木质素屏蔽 + 不可降解残余
3. 青贮梭菌竞争与品质分型：LAB vs 梭菌，pH 门 + 干物质门
4. 苹果渣好氧堆肥：自热 + 耗氧 + 腐熟度
5. 果渣饲料固态发酵：果胶/IDF 双时间尺度 + 蛋白富集 + 脱毒
6. 多菌株共发酵：菌株筛选与共培养（含木质素屏蔽）

双入口
------
入口一 · 模型预测计算：list / params / simulate / control / mix
入口二 · 案例 Demo 演示：demo

纪律约定（照《六级模型方程与案例》文档执行）
---------------------------------------------
1. 只实现 Scale 1–6 文档给出的方程、参数与案例；不新增任何动力学机制。
2. 模型必须由用户手动指定 --scale（1..6），脚本不擅自替用户选型。
3. 文档未给出的数值一律使用明确标注的“演示默认值”，可用 --set key=value 覆盖。

浓度基准
--------
全部用“单位干基质量分数” g/g DM，不是 g/L。
换算：含水率 w（湿基）时，1 g 干基对应 w/(1-w) g 水。

参数覆盖
--------
--set key=value 可重复，例如： --set DM=0.33 --set WSC0=0.12
配比不固定时先用 `mix` 子命令把物料配比折算成参数，再传给 simulate/demo。
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
    1: "青贮基础厌氧发酵模型（LAB 产乳酸 + pH 自抑 + 缓冲能力）",
    2: "纤维分级降解模型（Van Soest NDF/ADF/ADL，木质素屏蔽）",
    3: "青贮梭菌竞争与品质分型模型（乳酸型 vs 丁酸型劣变）",
    4: "苹果渣好氧堆肥模型（自热 + 耗氧 + 腐熟度）",
    5: "果渣饲料固态发酵模型（果胶/IDF 降解 + 蛋白富集 + 抗营养因子）",
    6: "多菌株共发酵模型（菌株筛选与共培养，含木质素屏蔽）",
}

# 真实示范案例（来自文档）
CASES = {
    1: {
        "organism": "乳酸菌群（同型/异型发酵 LAB 合并为单一菌群）",
        "ascii": "LAB consortium",
        "system": "秸秆:麦苗 ≈ 70:30（鲜重），DM 32%，WSC 10% DM，初始 pH 6.2；产物：乳酸",
        "params": {"mu_max": 0.45, "Ks": 0.002, "Yxs": 0.25, "ms": 0.02,
                   "Yla": 0.90, "BC": 0.025,
                   "pH50": 4.25, "wpH": 0.06,
                   "pH0": 6.2, "WSC0": 0.10, "LAB0": 0.001, "LA0": 0.0},
        "assumed": ["mu_max", "Ks", "Yxs", "ms", "Yla", "BC", "pH50", "wpH",
                    "pH0", "WSC0", "LAB0", "LA0"],
        "tend": 168.0,
        "result": ("168 h 终点：pH 6.20 → 3.81，乳酸 0.0597 g/g DM（占初始 WSC 60%），WSC 耗尽。"
                   "pH 跌破 4.2 后 LAB 被自身产的酸抑制，发酵自然停止——这就是青贮「酸封」。"
                   "对照：WSC0=0.04 时 pH 只降到 4.78（未酸封）；WSC0=0.14 时降到 3.77。"),
    },
    2: {
        "organism": "纤维分解菌群（好氧/兼性，合并为单一菌群）",
        "ascii": "fibrolytic consortium",
        "system": "秸秆+麦苗混合料：NDF 70%、ADF 42%、ADL 5%（即 半纤维素 28%、纤维素 37%、木质素 5%）",
        "params": {"H0": 0.28, "C0": 0.37, "L0": 0.05,
                   "fHdig": 0.70, "fCdig": 0.55,
                   "kH": 3.0, "kC": 2.0, "alphaL": 8.0,
                   "YE": 0.35, "kd": 0.08, "E0": 0.02,
                   "pH": 6.0, "pH50": 5.5, "wpH": 0.50},
        "assumed": ["fHdig", "fCdig", "kH", "kC", "alphaL", "YE", "kd", "E0",
                    "pH", "pH50", "wpH"],
        "tend": 96.0,
        "result": ("96 h 终点：半纤维素 0.280→0.099（降解 65%，上限 70%）、纤维素 0.370→0.203"
                   "（降解 45%，上限 55%）、木质素 0.050 恒定；NDF 总降解率 54%。"
                   "木质素不消耗，但通过 exp(-αL) 同时压低两条速率：ADL 0.03→已发酵 0.367；"
                   "ADL 0.10→只剩 0.269。"),
    },
    3: {
        "organism": "乳酸菌 LAB vs 梭菌 Clostridia（竞争同一基质）",
        "ascii": "LAB vs Clostridia",
        "system": "麦苗为主、高水分低糖青贮：DM 22%，WSC 5% DM，初始 pH 6.0；产物：乳酸/丁酸",
        "params": {"muL": 0.45, "KsL": 0.002, "YxsL": 0.25, "msL": 0.02, "Yla": 0.90,
                   "muC": 0.30, "KsC": 0.004, "KsLA": 0.010, "YxsC": 0.12,
                   "Ybu": 0.55, "Ynh3": 0.015,
                   "pH50L": 4.25, "wpHL": 0.06, "pHCI": 4.60, "wpHC": 0.15,
                   "BC": 0.025, "kphBu": 0.50, "knh3": 0.02,
                   "DM": 0.22, "DM50": 0.28, "wDM": 0.05,
                   "pH0": 6.0, "WSC0": 0.05, "LAB0": 0.001, "CL0": 0.0002,
                   "LA0": 0.0, "Bu0": 0.0, "NH30": 0.0},
        "assumed": ["muL", "KsL", "YxsL", "msL", "Yla",
                    "muC", "KsC", "KsLA", "YxsC", "Ybu", "Ynh3",
                    "pH50L", "wpHL", "pHCI", "wpHC", "BC", "kphBu", "knh3",
                    "DM", "DM50", "wDM",
                    "pH0", "WSC0", "LAB0", "CL0", "LA0", "Bu0", "NH30"],
        "tend": 168.0,
        "result": ("168 h 终点（劣质基准）：pH 6.00 → 5.51（未酸封、反而有氨抬升），乳酸被梭菌吃光"
                   "（LA=0），丁酸累积 0.0247 g/g DM（2.47% DM），属【劣质·丁酸型】。"
                   "对照：WSC0=0.14、DM=0.33 时 pH=3.78、LA=0.055、丁酸仅 0.0010（【优质·乳酸型】）；"
                   "WSC0=0.10、DM=0.30 时丁酸 0.0018（【中等】）。"),
    },
    4: {
        "organism": "好氧堆肥微生物群落（嗜温→嗜热，合并为单一菌群）",
        "ascii": "composting consortium",
        "system": "苹果渣 70% + 秸秆 30% 调理（C/N≈25），含水率 60%，堆体约 1.5 m",
        "params": {"OM0": 0.80, "OMres": 0.30, "kOM": 0.004,
                   "Tmin": 10.0, "Topt": 55.0, "Tmax": 72.0,
                   "YQ": 1.4e4, "Ceff": 3.8, "hA": 0.30,
                   "Tamb": 25.0, "T0": 25.0,
                   "kLa": 20.0, "O2star": 0.02, "KO2": 0.004, "YO2": 0.8, "O20": 0.02,
                   "kGI": 0.02, "GI0": 0.10},
        "assumed": ["kOM", "OMres", "YQ", "Ceff", "hA", "Tamb", "T0",
                    "kLa", "O2star", "KO2", "YO2", "O20", "kGI", "GI0"],
        "tend": 720.0,
        "result": ("峰值堆温 67.0 ℃（第 2–3 天进入嗜热杀菌区），嗜热期持续约 15 天；"
                   "OM 0.80 → 0.391（降解 49%，受 OMres=0.30 截断）；GI 0.10 → 0.99（约 15 天过 0.8）。"
                   "对照：hA=1.2（小堆/散热快）峰值仅约 34 ℃，进不了杀菌区，OM 也只降到 0.518。"),
    },
    5: {
        "organism": "酵母 + 乳酸菌 + 霉菌（混菌，果渣饲料发酵）",
        "ascii": "yeast + LAB + mold",
        "system": "苹果渣 60% + 麸皮 25% + 秸秆 14% + 尿素 1%，含水率 55%，初始 pH 3.8",
        "params": {"PEC0": 0.12, "IDF0": 0.45, "PR0": 0.08, "ANF0": 0.02, "B0": 0.005,
                   "mu": 0.25, "KF": 0.05, "Xm": 0.06, "Yxs": 0.35, "kd": 0.01,
                   "kP": 0.15, "kI": 0.012, "kA": 0.15,
                   "Ypx": 0.90, "PRmax": 0.18},
        "assumed": ["PEC0", "IDF0", "PR0", "ANF0", "B0",
                    "mu", "KF", "Xm", "Yxs", "kd", "kP", "kI", "kA", "Ypx", "PRmax"],
        "tend": 120.0,
        "result": ("120 h 终点：果胶 0.120→0.048（降解 60%）、IDF 0.450→0.418（仅降解 7%）、"
                   "真蛋白 0.080→0.121 g/g DM（+4.1 个百分点）、抗营养因子 0.020→0.008（降解 60%）。"
                   "果胶降解速度是 IDF 的 8.6 倍——「快变量/慢变量」必须分阶段设计。"),
    },
    6: {
        "organism": "枯草芽孢杆菌 + 黑曲霉（双菌共培养，推荐方案）",
        "ascii": "B. subtilis + A. niger",
        "system": ("提胶 80% 后的苹果渣：DM 88%，CP 8.0%，NDF 52%、ADF 46%、ADL 14%，"
                   "残果胶 2.5%，灰分 6%，pH 4.7；补糖蜜 6% + 尿素 1%；目标：牛羊饲料"),
        "params": {"WSC0": 0.080, "PEC0": 0.025, "IDF0": 0.38, "PR0": 0.08,
                   "ANF0": 0.010,
                   "L0": 0.14, "alphaL": 6.0, "fIdig": 0.55, "PRmax": 0.18,
                   "Xm_tot": 0.035, "ms": 0.010, "Yhyd": 0.85,
                   "mu1": 0.32, "KF1": 0.03, "Xm1": 0.020, "kP1": 0.15,
                   "kI1": 0.05, "kA1": 0.08, "Ypx1": 1.8, "Yxs1": 0.35, "kd1": 0.010,
                   "mu2": 0.30, "KF2": 0.02, "Xm2": 0.015, "kP2": 0.05,
                   "kI2": 0.005, "kA2": 0.03, "Ypx2": 0.8, "Yxs2": 0.25, "kd2": 0.010,
                   "mu3": 0.25, "KF3": 0.05, "Xm3": 0.020, "kP3": 0.03,
                   "kI3": 0.005, "kA3": 0.04, "Ypx3": 2.2, "Yxs3": 0.30, "kd3": 0.010,
                   "mu4": 0.28, "KF4": 0.03, "Xm4": 0.030, "kP4": 0.30,
                   "kI4": 0.60, "kA4": 0.10, "Ypx4": 1.2, "Yxs4": 0.30, "kd4": 0.010,
                   "B10": 0.002, "B20": 0.0, "B30": 0.0, "B40": 0.002},
        "assumed": ["WSC0", "PEC0", "IDF0", "PR0", "ANF0", "L0", "alphaL",
                    "fIdig", "PRmax", "Xm_tot", "ms", "Yhyd",
                    "mu1", "KF1", "Xm1", "kP1", "kI1", "kA1", "Ypx1", "Yxs1", "kd1",
                    "mu2", "KF2", "Xm2", "kP2", "kI2", "kA2", "Ypx2", "Yxs2", "kd2",
                    "mu3", "KF3", "Xm3", "kP3", "kI3", "kA3", "Ypx3", "Yxs3", "kd3",
                    "mu4", "KF4", "Xm4", "kP4", "kI4", "kA4", "Ypx4", "Yxs4", "kd4",
                    "B10", "B20", "B30", "B40"],
        "tend": 120.0,
        "result": ("120 h 终点：IDF 0.380→0.305（降 19.8%）、果胶 0.025→0.011（降 54.7%）、"
                   "真蛋白 8.0%→13.4%（+5.4 点）、抗营养因子降 28.1%。"
                   "对照：单菌（仅枯草）IDF 只降 4.2%；四菌因总承载量竞争反而只降 12.6%"
                   "——菌株不是越多越好，双菌（芽孢杆菌+曲霉）是性价比最高的组合。"
                   "木质素 14% DM 通过 exp(-αL) 把 IDF 降解压在 20% 以内，是硬上限。"),
    },
}

CONTROL_NOTES = {
    1: ("青贮型：唯一目标是「快速把 pH 打到 4.2 以下」。三件可控事："
        "① 干物质 30%–35%（太低渗液、太高难压实）；② WSC ≥ 8%–10% DM（糖不够就不产酸）；"
        "③ 压实密封（残氧越少、梭菌越没有窗口）。缓冲能力高的原料要额外加糖蜜/乳酸菌剂。"),
    2: ("纤维型：可发酵量由 NDF/ADF/ADL 三组分唯一决定，不能靠延长周期硬提；"
        "木质素是「屏蔽」而非「消耗」，每提高 1 个百分点 ADL，降解速率按 exp(-αL) 打折；"
        "提高降解看三点：降低 ADL（选期/预处理）、补氮与矿物质、控制 pH 在中性附近。"),
    3: ("品质分型型：成败在于「pH 下降速度 vs 梭菌启动速度」的赛跑。"
        "pH 在 48 h 内降到 4.5 以下 → 乳酸型优质；降不下来 → 梭菌把乳酸转丁酸、pH 反弹，"
        "干物质二次损失。干预点：提高 DM、提高 WSC、接种乳酸菌、缩短装填时间。"),
    4: ("堆肥型：前 3–5 天是「升温赛跑」——堆体必须自己冲进 55–65 ℃ 才能杀菌与破壁；"
        "靠的是堆体尺寸（保温）与初始 C/N、含水率。温度到顶后由 f_T 自动回落，"
        "不要靠翻堆强行降温。腐熟看 GI>0.8 与 OM 降幅，不看时间。"),
    5: ("果渣饲料型：果胶是「快变量」、IDF 是「慢变量」，两者时间尺度差一个数量级；"
        "工艺上先让果胶快速降解释放可发酵糖、支撑菌体生长，再由菌体蛋白与酶系慢慢啃 IDF。"
        "苹果渣低 pH（3.5–4.5）本身抑菌，要接种耐酸酵母/乳酸菌并补氮（尿素/麸皮）。"),
    6: ("多菌株型：菌株不是越多越好，要按「功能分工」配——"
        "芽孢杆菌（蛋白酶/抑菌）+ 曲霉（纤维素酶/果胶酶）+ 酵母（菌体蛋白）+ 乳杆菌（产酸保藏）。"
        "关键约束是**总承载量 Xm_tot 固定**：菌株之间是竞争关系，加一个菌就挤掉另一个的份额。"
        "牛羊饲料还要额外注意：木质素 14% DM 是硬上限，发酵只能提高「可及性」，不能减少木质素。"),
}

# 过程控制实际案例：青贮品质分型（Scale 3）
CONTROL_CASE = {
    "scale": 3,
    "goal": "把青贮锁定在「乳酸型」而不是「丁酸型」，控制干物质二次损失",
    "cv": "pH（及其下降速率）；替代量：乳酸/丁酸比、氨态氮占全氮比例",
    "mv": "原料干物质（凋萎/混秸秆）、WSC（加糖蜜/麸皮）、接种量、压实与密封程度",
    "phenomenon": ("pH 48 h 内降不到 4.5 以下 → 梭菌接管，乳酸被转成丁酸 + NH₃，"
                   "pH 反弹、DM 二次损失、适口性崩坏"),
    "strategy": ("① 干物质调到 30%–35%（高水分是梭菌最大的窗口）；"
                 "② WSC ≥ 8%–10% DM，不够就加糖蜜/高糖副产物；"
                 "③ 接种同型乳酸菌（_L. plantarum_）抢跑；"
                 "④ 压实 + 快速密封，把残氧压到最低；"
                 "⑤ 判定以现行青贮质量分级标准为准（pH、丁酸、氨态氮三项）。"),
}


# ---------------------------------------------------------------------------
# 二、动力学方程（严格取自文档）
# ---------------------------------------------------------------------------

def f_ph(pH, pH50, w):
    """pH 抑制因子：pH 高于 pH50 时接近 1，低于 pH50 迅速衰减。"""
    z = (pH50 - pH) / w
    if z > 50.0:
        return 0.0
    if z < -50.0:
        return 1.0
    return 1.0 / (1.0 + pow(2.718281828459045, z))


def f_dm(DM, DM50, wDM):
    """干物质对梭菌的抑制因子：越湿（DM 越低）越有利于梭菌。"""
    z = (DM - DM50) / wDM
    if z > 50.0:
        return 0.0
    if z < -50.0:
        return 1.0
    return 1.0 / (1.0 + pow(2.718281828459045, z))


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


def rhs_scale1(t, y, p):
    """青贮基础：LAB 消耗 WSC 产乳酸，pH 随乳酸累积下降并自抑。"""
    LAB, WSC, LA, pH = y
    W = max(0.0, WSC)
    fph = f_ph(pH, p["pH50"], p["wpH"])
    mu = p["mu_max"] * W / (p["Ks"] + W) * fph
    dLAB = mu * LAB
    cons = (1.0 / p["Yxs"]) * dLAB + p["ms"] * LAB
    dWSC = -cons
    dLA = p["Yla"] * (1.0 / p["Yxs"]) * dLAB
    dpH = -dLA / p["BC"]
    return [dLAB, dWSC, dLA, dpH]


def rhs_scale2(t, y, p):
    """纤维分级降解：半纤维素/纤维素在木质素屏蔽下被降解，存在不可降解残余。"""
    E, H, C, L = y
    fL = pow(2.718281828459045, -p["alphaL"] * max(0.0, L))
    fph = f_ph(p["pH"], p["pH50"], p["wpH"])
    Hres = (1.0 - p["fHdig"]) * p["H0"]
    Cres = (1.0 - p["fCdig"]) * p["C0"]
    vH = p["kH"] * E * max(0.0, H - Hres) * fL * fph
    vC = p["kC"] * E * max(0.0, C - Cres) * fL * fph
    dH = -vH
    dC = -vC
    dL = 0.0
    dE = p["YE"] * (vH + vC) - p["kd"] * E
    return [dE, dH, dC, dL]


def rhs_scale3(t, y, p):
    """青贮品质分型：LAB 与梭菌竞争，梭菌在高 pH、低干物质下把乳酸转为丁酸并产氨。"""
    LAB, CL, WSC, LA, Bu, NH3, pH = y
    W = max(0.0, WSC)
    L = max(0.0, LA)
    fphL = f_ph(pH, p["pH50L"], p["wpHL"])
    fphC = f_ph(pH, p["pHCI"], p["wpHC"])
    fDM = f_dm(p["DM"], p["DM50"], p["wDM"])
    muL = p["muL"] * W / (p["KsL"] + W) * fphL
    dLAB = muL * LAB
    consL = (1.0 / p["YxsL"]) * dLAB + p["msL"] * LAB
    dLA_L = p["Yla"] * (1.0 / p["YxsL"]) * dLAB
    sW = W / (p["KsC"] + W)
    sL = L / (p["KsLA"] + L)
    fC_sub = sW + sL
    muC = p["muC"] * fC_sub * fphC * fDM
    dCL = muC * CL
    consC = (1.0 / p["YxsC"]) * dCL
    shareW = sW / fC_sub if fC_sub > 1e-12 else 0.0
    shareL = 1.0 - shareW
    dWSC = -consL - consC * shareW
    dLA = dLA_L - consC * shareL
    dBu = p["Ybu"] * consC
    dNH3 = p["Ynh3"] * consC
    dpH = -(dLA + p["kphBu"] * dBu) / p["BC"] + p["knh3"] * dNH3
    return [dLAB, dCL, dWSC, dLA, dBu, dNH3, dpH]


def rhs_scale4(t, y, p):
    """苹果渣好氧堆肥：有机质降解自热，氧限制，腐熟度累积。"""
    OM, T, O2, GI = y
    fT = f_temp(T, p)
    fO2 = f_o2(O2, p)
    deg = p["kOM"] * max(0.0, OM - p["OMres"]) * fT * fO2
    dOM = -deg
    dT = (p["YQ"] * deg - p["hA"] * (T - p["Tamb"])) / p["Ceff"]
    dO2 = p["kLa"] * (p["O2star"] - O2) - (1.0 / p["YO2"]) * deg
    dGI = p["kGI"] * (1.0 - GI) * ((p["OM0"] - max(0.0, OM)) / p["OM0"])
    return [dOM, dT, dO2, dGI]


def rhs_scale5(t, y, p):
    """果渣饲料固态发酵：果胶快降、IDF 慢降、蛋白富集、抗营养因子脱除。"""
    PEC, IDF, PR, ANF, B = y
    F = max(0.0, PEC) + 0.30 * max(0.0, IDF)   # 可发酵底物当量
    mu = p["mu"] * F / (p["KF"] + F) * max(0.0, 1.0 - B / p["Xm"])
    dB = (mu - p["kd"]) * B
    vP = p["kP"] * B * max(0.0, PEC)
    vI = p["kI"] * B * max(0.0, IDF)
    dPEC = -vP
    dIDF = -vI
    dPR = p["Ypx"] * (vP + vI) * max(0.0, 1.0 - PR / p["PRmax"])
    dANF = -p["kA"] * B * max(0.0, ANF)
    return [dPEC, dIDF, dPR, dANF, dB]


def rhs_scale6(t, y, p):
    """多菌株共发酵：4 株菌共享可发酵糖/果胶/纤维池与总承载量，各自贡献不同酶活谱。"""
    B1, B2, B3, B4, WSC, PEC, IDF, PR, ANF = y
    Bs = [max(0.0, B1), max(0.0, B2), max(0.0, B3), max(0.0, B4)]
    Btot = sum(Bs)
    W = max(0.0, WSC)
    F = W + max(0.0, PEC) + 0.30 * max(0.0, IDF)
    fL = pow(2.718281828459045, -p["alphaL"] * max(0.0, p["L0"]))
    IDFres = (1.0 - p["fIdig"]) * p["IDF0"]

    dB = []
    cons = 0.0
    for i, Bi in enumerate(Bs, start=1):
        mu = (p[f"mu{i}"] * F / (p[f"KF{i}"] + F)
              * max(0.0, 1.0 - Btot / p["Xm_tot"]))
        dB.append((mu - p[f"kd{i}"]) * Bi)
        cons += (1.0 / p[f"Yxs{i}"]) * mu * Bi
    # 各菌株的酶活贡献（一阶于菌体量）
    vP = sum(p[f"kP{i}"] * Bs[i - 1] for i in range(1, 5)) * max(0.0, PEC)
    vI = (sum(p[f"kI{i}"] * Bs[i - 1] for i in range(1, 5))
          * max(0.0, IDF - IDFres) * fL)
    dPEC = -vP
    dIDF = -vI
    # 可发酵糖：酶解产物回补 − 生长消耗 − 维持（闭合碳平衡）
    dWSC = p["Yhyd"] * (vP + vI) - cons - p["ms"] * Btot
    # 蛋白富集：按菌体量加权的蛋白得率
    if Btot > 1e-12:
        Ypx_eff = sum(p[f"Ypx{i}"] * Bs[i - 1] for i in range(1, 5)) / Btot
    else:
        Ypx_eff = 0.0
    dPR = Ypx_eff * (vP + vI) * max(0.0, 1.0 - PR / p["PRmax"])
    dANF = -sum(p[f"kA{i}"] * Bs[i - 1] for i in range(1, 5)) * max(0.0, ANF)
    return [dB[0], dB[1], dB[2], dB[3], dWSC, dPEC, dIDF, dPR, dANF]


RHS = {1: rhs_scale1, 2: rhs_scale2, 3: rhs_scale3, 4: rhs_scale4, 5: rhs_scale5,
       6: rhs_scale6}

STATE_NAMES = {
    1: ["LAB", "WSC", "LA", "pH"],
    2: ["E", "H", "C", "L"],
    3: ["LAB", "CL", "WSC", "LA", "Bu", "NH3", "pH"],
    4: ["OM", "T", "O2", "GI"],
    5: ["PEC", "IDF", "PR", "ANF", "B"],
    6: ["B1", "B2", "B3", "B4", "WSC", "PEC", "IDF", "PR", "ANF"],
}


def initial_state(scale, p):
    if scale == 1:
        return [p["LAB0"], p["WSC0"], p["LA0"], p["pH0"]]
    if scale == 2:
        return [p["E0"], p["H0"], p["C0"], p["L0"]]
    if scale == 3:
        return [p["LAB0"], p["CL0"], p["WSC0"], p["LA0"],
                p["Bu0"], p["NH30"], p["pH0"]]
    if scale == 4:
        return [p["OM0"], p["T0"], p["O20"], p["GI0"]]
    if scale == 5:
        return [p["PEC0"], p["IDF0"], p["PR0"], p["ANF0"], p["B0"]]
    if scale == 6:
        return [p["B10"], p["B20"], p["B30"], p["B40"],
                p["WSC0"], p["PEC0"], p["IDF0"], p["PR0"], p["ANF0"]]
    raise ValueError("scale 必须为 1..6")


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
    ax2 = None

    if scale == 1:
        ax.plot(t, Y[1], label="WSC (g/g DM)", color="#2ca02c", ls="--")
        ax.plot(t, Y[2], label="LA lactic acid (g/g DM)", color="#ff7f0e")
        ax2 = ax.twinx()
        ax2.plot(t, Y[3], label="pH", color="#d62728")
        ax2.axhline(4.2, color="#7f7f7f", ls=":", lw=1)
        ax2.set_ylabel("pH")
        ax.set_ylabel("WSC / LA (g/g DM)")
    elif scale == 2:
        ax.plot(t, Y[1], label="H hemicellulose (g/g DM)", color="#1f77b4")
        ax.plot(t, Y[2], label="C cellulose (g/g DM)", color="#ff7f0e")
        ax.plot(t, Y[3], label="L lignin (g/g DM)", color="#7f7f7f", ls="--")
        ax.set_ylabel("fiber fraction (g/g DM)")
    elif scale == 3:
        ax.plot(t, Y[2], label="WSC (g/g DM)", color="#2ca02c", ls="--")
        ax.plot(t, Y[3], label="LA lactic acid (g/g DM)", color="#ff7f0e")
        ax.plot(t, Y[4], label="Bu butyric acid (g/g DM)", color="#d62728", ls="-.")
        ax2 = ax.twinx()
        ax2.plot(t, Y[6], label="pH", color="#1f77b4")
        ax2.axhline(4.5, color="#7f7f7f", ls=":", lw=1)
        ax2.set_ylabel("pH")
        ax.set_ylabel("WSC / LA / Bu (g/g DM)")
    elif scale == 4:
        ax.plot(t, Y[0], label="OM degradable (g/g DM)", color="#1f77b4")
        ax.plot(t, Y[3], label="GI maturity index", color="#2ca02c", ls="--")
        ax2 = ax.twinx()
        ax2.plot(t, Y[1], label="T pile (degC)", color="#d62728")
        ax2.axhline(55.0, color="#7f7f7f", ls=":", lw=1)
        ax2.set_ylabel("T (degC)")
        ax.set_ylabel("OM / GI")
    elif scale == 5:
        ax.plot(t, Y[0], label="PEC pectin (g/g DM)", color="#1f77b4")
        ax.plot(t, Y[1], label="IDF insoluble fiber (g/g DM)", color="#8c564b")
        ax.plot(t, Y[2], label="PR true protein (g/g DM)", color="#ff7f0e")
        ax.plot(t, Y[3], label="ANF anti-nutrients (g/g DM)", color="#d62728", ls="--")
        ax.set_ylabel("fraction (g/g DM)")
    else:
        ax.plot(t, Y[0], label="B1 B. subtilis (g/g DM)", color="#1f77b4")
        ax.plot(t, Y[1], label="B2 L. plantarum (g/g DM)", color="#2ca02c")
        ax.plot(t, Y[2], label="B3 S. cerevisiae (g/g DM)", color="#9467bd")
        ax.plot(t, Y[3], label="B4 A. niger (g/g DM)", color="#8c564b")
        ax2 = ax.twinx()
        ax2.plot(t, Y[4], label="WSC sugar", color="#bcbd22", ls="--")
        ax2.plot(t, Y[5], label="PEC pectin", color="#17becf", ls="--")
        ax2.plot(t, Y[6], label="IDF fiber", color="#7f7f7f", ls=":")
        ax2.plot(t, Y[7], label="PR protein", color="#ff7f0e", ls="-.")
        ax2.set_ylabel("WSC / PEC / IDF / PR (g/g DM)")
        ax.set_ylabel("strain biomass (g/g DM)")
    ax.set_xlabel("time (h)")
    ax.grid(alpha=0.3)
    h1, l1 = ax.get_legend_handles_labels()
    if ax2 is None:
        ax.legend(h1, l1, loc="best", fontsize=8)
    else:
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, loc="best", fontsize=8)
    ax.set_title(title or f"Scale {scale} lignocellulose conversion")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 五、文本输出
# ---------------------------------------------------------------------------

PARAM_ORDER = {
    1: ["mu_max", "Ks", "Yxs", "ms", "Yla", "BC", "pH50", "wpH",
        "pH0", "WSC0", "LAB0", "LA0"],
    2: ["kH", "kC", "alphaL", "fHdig", "fCdig", "YE", "kd",
        "H0", "C0", "L0", "E0", "pH", "pH50", "wpH"],
    3: ["muL", "KsL", "YxsL", "msL", "Yla",
        "muC", "KsC", "KsLA", "YxsC", "Ybu", "Ynh3",
        "pH50L", "wpHL", "pHCI", "wpHC", "BC", "kphBu", "knh3",
        "DM", "DM50", "wDM",
        "pH0", "WSC0", "LAB0", "CL0", "LA0", "Bu0", "NH30"],
    4: ["kOM", "Tmin", "Topt", "Tmax", "YQ", "Ceff", "hA", "Tamb", "T0",
        "kLa", "O2star", "KO2", "YO2", "O20", "kGI", "OM0", "OMres", "GI0"],
    5: ["mu", "KF", "Xm", "Yxs", "kd", "kP", "kI", "kA", "Ypx", "PRmax",
        "PEC0", "IDF0", "PR0", "ANF0", "B0"],
    6: ["mu1", "KF1", "Xm1", "kP1", "kI1", "kA1", "Ypx1", "Yxs1", "kd1",
        "mu2", "KF2", "Xm2", "kP2", "kI2", "kA2", "Ypx2", "Yxs2", "kd2",
        "mu3", "KF3", "Xm3", "kP3", "kI3", "kA3", "Ypx3", "Yxs3", "kd3",
        "mu4", "KF4", "Xm4", "kP4", "kI4", "kA4", "Ypx4", "Yxs4", "kd4",
        "Xm_tot", "ms", "Yhyd", "alphaL", "fIdig", "PRmax", "L0",
        "WSC0", "PEC0", "IDF0", "PR0", "ANF0", "B10", "B20", "B30", "B40"],
}


def fmt_params(scale, p):
    keys = PARAM_ORDER[scale]
    parts = []
    for k in keys:
        if k in p:
            v = p[k]
            parts.append(f"{k}={v:g}" if abs(v) < 1e5 else f"{k}={v:.3g}")
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
    print("模型选择面板（必须手动指定 --scale 1..6）：")
    for k in sorted(SCALES):
        print(f"  Scale {k}：{SCALES[k]}")
    print("\n案例：")
    for k in sorted(CASES):
        print(f"  Scale {k}：{CASES[k]['organism']}")
        print(f"            {CASES[k]['system']}")
    print("\n浓度基准：g/g 干基质（DM），不是 g/L。")
    print("配比不固定时，先用 `mix` 把物料配比折算成参数。")


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
    if a.scale == 1:
        print(f"当前 f_pH(pH0) = {f_ph(p['pH0'], p['pH50'], p['wpH']):.3f}")
    if a.scale == 2:
        print(f"当前木质素屏蔽 f_L = {pow(2.718281828459045, -p['alphaL'] * p['L0']):.3f}")
        print(f"可发酵上限 = fHdig*H0 + fCdig*C0 = "
              f"{p['fHdig'] * p['H0'] + p['fCdig'] * p['C0']:.4f} g/g DM")
    if a.scale == 3:
        print(f"当前 f_DM = {f_dm(p['DM'], p['DM50'], p['wDM']):.3f}"
              f"（DM={p['DM']:g}，DM50={p['DM50']:g}）")


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

    if a.scale == 1:
        LA_end = float(yend[2])
        pH_end = float(yend[3])
        print(f"终点 pH = {pH_end:.2f}；乳酸 = {LA_end:.4f} g/g DM "
              f"（占初始 WSC 的 {LA_end / max(1e-9, p['WSC0']) * 100:.1f}%）")
        if pH_end <= 4.2:
            print("结论：pH ≤ 4.2，达到「酸封」——乳酸型优质青贮的充分条件已满足。")
        elif pH_end <= 4.5:
            print("结论：pH 在 4.2–4.5 之间，属临界区，梭菌仍有窗口，需加糖/接种/提高干物质。")
        else:
            print("结论：pH > 4.5，未酸封——梭菌风险高，青贮大概率劣变。")
    if a.scale == 2:
        Hf, Cf, Lf = float(yend[1]), float(yend[2]), float(yend[3])
        dH = (p["H0"] - Hf) / p["H0"] * 100
        dC = (p["C0"] - Cf) / p["C0"] * 100
        print(f"半纤维素降解 {dH:.1f}%（上限 {p['fHdig'] * 100:.0f}%）；"
              f"纤维素降解 {dC:.1f}%（上限 {p['fCdig'] * 100:.0f}%）；木质素 {Lf:.4f}（惰性）")
        got = (p["H0"] - Hf) + (p["C0"] - Cf)
        print(f"已发酵纤维量 {got:.4f} g/g DM；"
              f"NDF 总降解率 {got / (p['H0'] + p['C0']) * 100:.1f}%")
        print("结论：木质素全程不变，但通过 exp(-αL) 同时压低两条降解速率——「屏蔽而非消耗」。")
    if a.scale == 3:
        pH_end = float(yend[6])
        Bu_end = float(yend[4])
        LA_end = float(yend[3])
        ratio = Bu_end / (LA_end + Bu_end + 1e-12)
        print(f"终点 pH={pH_end:.2f}；乳酸={LA_end:.4f}；丁酸={Bu_end:.4f}；"
              f"丁酸占有机酸 {ratio * 100:.1f}%；氨态氮={yend[5]:.4f}")
        if pH_end <= 4.2 and Bu_end < 0.001:
            print("结论：【优质·乳酸型】pH≤4.2 且丁酸<0.1% DM——梭菌被完全压制。")
        elif Bu_end < 0.005:
            print("结论：【中等】丁酸 0.1%–0.5% DM，存在轻度梭菌活动，仍可用但损失已发生。")
        else:
            print("结论：【劣质·丁酸型】丁酸>0.5% DM、pH 反弹——干物质二次损失、适口性差，不建议饲用。")
        print("注：品质分级阈值以现行青贮质量分级标准为准，此处仅作模型自检。")
    if a.scale == 4:
        Tpk = float(np.max(Y[1]))
        GI_end = float(yend[3])
        OM_end = float(yend[0])
        print(f"峰值堆温 T_max = {Tpk:.1f} ℃；有机质 {p['OM0']:.2f} → {OM_end:.2f} "
              f"（降解 {(p['OM0'] - OM_end) / p['OM0'] * 100:.1f}%）；GI = {GI_end:.2f}")
        if Tpk >= 55.0:
            print("结论：堆体进入嗜热杀菌区（≥55 ℃），卫生学指标可满足；"
                  "嗜热持续时长需按现行堆肥卫生标准校核。")
        else:
            print("结论：未达 55 ℃，杀菌不充分——加大堆体/提高初始 C/N 或含水率。")
        if GI_end >= 0.8:
            print("结论：GI ≥ 0.8，达到腐熟判据（种子发芽指数），可作肥料使用。")
        else:
            print("结论：GI < 0.8，未腐熟，直接施用有烧苗/植物毒性风险。")
    if a.scale == 5:
        dPEC = (p["PEC0"] - yend[0]) / p["PEC0"] * 100
        dIDF = (p["IDF0"] - yend[1]) / p["IDF0"] * 100
        dANF = (p["ANF0"] - yend[3]) / p["ANF0"] * 100
        print(f"果胶降解 {dPEC:.1f}%；IDF 降解 {dIDF:.1f}%；抗营养因子降解 {dANF:.1f}%；"
              f"真蛋白 {p['PR0']:.3f} → {yend[2]:.3f} g/g DM")
        print(f"结论：果胶降解是 IDF 的 {dPEC / max(1e-9, dIDF):.1f} 倍——"
              "两个时间尺度差一个数量级，工艺上必须分阶段设计。")
        if yend[2] > p["PR0"]:
            print(f"      蛋白净增 {(yend[2] - p['PR0']) * 100:.1f} 个百分点（菌体蛋白富集）。")
    if a.scale == 6:
        Bs = [float(yend[i]) for i in range(4)]
        Btot = sum(Bs)
        dPEC = (p["PEC0"] - yend[5]) / p["PEC0"] * 100
        dIDF = (p["IDF0"] - yend[6]) / p["IDF0"] * 100
        dANF = (p["ANF0"] - yend[8]) / p["ANF0"] * 100
        names4 = ["枯草芽孢杆菌", "植物乳杆菌", "酿酒酵母", "黑曲霉"]
        print("菌株终生物量（g/g DM）与占比：")
        for i, (nm, b) in enumerate(zip(names4, Bs), start=1):
            share = b / Btot * 100 if Btot > 1e-12 else 0.0
            print(f"  B{i} {nm:<8} {b:.4f}   {share:5.1f}%")
        print(f"果胶降解 {dPEC:.1f}%；IDF 降解 {dIDF:.1f}%（上限 {p['fIdig'] * 100:.0f}%，"
              f"木质素屏蔽 f_L={pow(2.718281828459045, -p['alphaL'] * p['L0']):.3f}）；"
              f"抗营养因子降解 {dANF:.1f}%")
        print(f"真蛋白 {p['PR0']:.3f} → {yend[7]:.3f} g/g DM"
              f"（{p['PR0'] * 100:.1f}% → {yend[7] * 100:.1f}% DM）")
        if Btot > 1e-12:
            dom = names4[int(np.argmax(Bs))]
            print(f"结论：优势菌为 {dom}（占 {max(Bs) / Btot * 100:.0f}%）。"
                  "总承载量固定，菌株之间是竞争关系——加菌不等于加效果。")
        if dIDF < 10:
            print("结论：IDF 降解率低，木质素 14% DM 是硬限制；"
                  "发酵只能提高瘤胃可及性，不能减少木质素。")

    if a.out:
        plot_timeseries(a.scale, t, Y, p, a.out)
        print(f"已保存曲线：{a.out}")


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

        if s == 1:
            # 对照：WSC 不足 vs 充足，展示「糖不够就打不下 pH」
            for wsc, tag in ((0.04, "low-WSC"), (0.14, "high-WSC")):
                p1 = dict(p)
                p1["WSC0"] = wsc
                t1, Y1 = simulate(1, p1, tend)
                png1 = os.path.join(outdir, f"scale1_WSC{wsc:.2f}.png")
                plot_timeseries(1, t1, Y1, p1, png1,
                                title=f"Scale 1 | WSC0={wsc:.2f}")
                print(f"  对照（WSC0={wsc:.2f}）：{png1}  "
                      f"pH_end={Y1[3, -1]:.2f}, LA={Y1[2, -1]:.4f}")

        if s == 2:
            # 对照：ADL 低 vs 高，展示木质素屏蔽的指数效应
            for adl, tag in ((0.03, "low-ADL"), (0.10, "high-ADL")):
                p2 = dict(p)
                p2["L0"] = adl
                t2, Y2 = simulate(2, p2, tend)
                png2 = os.path.join(outdir, f"scale2_ADL{adl:.2f}.png")
                plot_timeseries(2, t2, Y2, p2, png2,
                                title=f"Scale 2 | ADL={adl:.2f}")
                got = ((p2["H0"] - Y2[1, -1]) + (p2["C0"] - Y2[2, -1]))
                print(f"  对照（ADL={adl:.2f}）：{png2}  已发酵纤维={got:.4f} g/g DM")

        if s == 3:
            # 对照：优质（高 DM 高 WSC）vs 劣质（低 DM 低 WSC），展示品质分型
            for wsc, dm, tag in ((0.14, 0.33, "good-lactic"),
                                 (0.05, 0.22, "bad-butyric")):
                p3 = dict(p)
                p3["WSC0"] = wsc
                p3["DM"] = dm
                t3, Y3 = simulate(3, p3, tend)
                png3 = os.path.join(outdir, f"scale3_{tag}.png")
                plot_timeseries(3, t3, Y3, p3, png3,
                                title=f"Scale 3 | {tag}")
                print(f"  对照（{tag}, WSC0={wsc:.2f}, DM={dm:.2f}）：{png3}  "
                      f"pH={Y3[6, -1]:.2f}, LA={Y3[3, -1]:.4f}, Bu={Y3[4, -1]:.4f}")

        if s == 4:
            # 对照：保温好（hA 小）vs 散热快（hA 大），展示能否冲进杀菌区
            for ha, tag in ((0.15, "large-pile"), (1.2, "small-pile")):
                p4 = dict(p)
                p4["hA"] = ha
                t4, Y4 = simulate(4, p4, tend)
                png4 = os.path.join(outdir, f"scale4_hA{ha:g}.png")
                plot_timeseries(4, t4, Y4, p4, png4,
                                title=f"Scale 4 | hA={ha:g} ({tag})")
                print(f"  对照（{tag}, hA={ha:g}）：{png4}  "
                      f"T_peak={np.max(Y4[1]):.1f} ℃, GI={Y4[3, -1]:.2f}")

        if s == 5:
            # 对照：果胶起点高 vs 低，展示「快变量」对菌体启动的作用
            for pec, tag in ((0.20, "high-pectin"), (0.05, "low-pectin")):
                p5 = dict(p)
                p5["PEC0"] = pec
                t5, Y5 = simulate(5, p5, tend)
                png5 = os.path.join(outdir, f"scale5_PEC{pec:.2f}.png")
                plot_timeseries(5, t5, Y5, p5, png5,
                                title=f"Scale 5 | PEC0={pec:.2f}")
                print(f"  对照（PEC0={pec:.2f}）：{png5}  "
                      f"IDF={Y5[1, -1]:.4f}, PR={Y5[2, -1]:.4f}, ANF={Y5[3, -1]:.4f}")

        if s == 6:
            # 对照：单菌 / 双菌 / 四菌，展示菌株分工与竞争
            combos = [
                ("single-Bs", {"B40": 0.0}),
                ("Bs+An", {}),
                ("all-four", {"B20": 0.002, "B30": 0.002}),
            ]
            for tag, over in combos:
                p6 = dict(p)
                p6.update(over)
                t6, Y6 = simulate(6, p6, tend)
                png6 = os.path.join(outdir, f"scale6_{tag}.png")
                plot_timeseries(6, t6, Y6, p6, png6,
                                title=f"Scale 6 | {tag}")
                print(f"  对照（{tag}）：{png6}  "
                      f"IDF={Y6[6, -1]:.4f}, PR={Y6[7, -1]:.4f}, ANF={Y6[8, -1]:.4f}")

        print_control(s)
    print("=" * 66)
    print(f"演示完成，图片输出目录：{outdir}")


# ---------------------------------------------------------------------------
# 七、物料配比折算（mix）
# ---------------------------------------------------------------------------

# 组分理化性质（实测区间中值；正式设计须以实测替换）
#   dm  : 湿基干物质分数
#   wsc : WSC（水溶性碳水化合物），g/g DM
#   ndf,adf,adl : Van Soest 三组分，g/g DM
#   cp  : 粗蛋白，g/g DM
MIX_COMPONENTS = {
    "straw":    {"name": "玉米秸秆", "dm": 0.88, "wsc": 0.08, "ndf": 0.78,
                 "adf": 0.45, "adl": 0.06, "cp": 0.04},
    "grass":    {"name": "麦苗(青刈)", "dm": 0.22, "wsc": 0.14, "ndf": 0.45,
                 "adf": 0.28, "adl": 0.03, "cp": 0.18},
    "pomace":   {"name": "苹果渣", "dm": 0.25, "wsc": 0.18, "ndf": 0.42,
                 "adf": 0.30, "adl": 0.05, "cp": 0.05},
    "bran":     {"name": "麸皮", "dm": 0.88, "wsc": 0.10, "ndf": 0.45,
                 "adf": 0.13, "adl": 0.03, "cp": 0.15},
    "molasses": {"name": "糖蜜", "dm": 0.75, "wsc": 0.60, "ndf": 0.00,
                 "adf": 0.00, "adl": 0.00, "cp": 0.05},
}


def cmd_mix(a):
    keys = ["straw", "grass", "pomace", "bran", "molasses"]
    ratios = {k: float(getattr(a, k) or 0.0) for k in keys}
    total = sum(ratios.values())
    if total <= 0:
        print("错误：至少给一个组分的配比（--straw/--grass/--pomace/--bran/--molasses）。")
        return

    if a.basis == "fresh":
        dry_mass = {k: ratios[k] * MIX_COMPONENTS[k]["dm"] for k in keys}
        dm_total = sum(dry_mass.values()) / total
    else:
        dry_mass = dict(ratios)
        dm_total = sum(ratios[k] * MIX_COMPONENTS[k]["dm"] for k in keys) / total

    dm_sum = sum(dry_mass.values())
    share = {k: (dry_mass[k] / dm_sum if dm_sum > 0 else 0.0) for k in keys}

    def blend(field):
        return sum(share[k] * MIX_COMPONENTS[k][field] for k in keys)

    ndf, adf, adl, wsc, cp = (blend(f) for f in ("ndf", "adf", "adl", "wsc", "cp"))
    H = max(0.0, ndf - adf)
    C = max(0.0, adf - adl)
    L = adl

    print("物料配比换算（全部为 g/g 干基质 DM）")
    print(f"  基准：{'鲜重' if a.basis == 'fresh' else '干重'}；混合后湿基干物质 DM = {dm_total * 100:.1f}%")
    print("  组分明细：")
    for k in keys:
        if ratios[k] > 0:
            print(f"    {MIX_COMPONENTS[k]['name']:<12} 配比 {ratios[k]:.2f}"
                  f"  干基份额 {share[k] * 100:5.1f}%  DM {MIX_COMPONENTS[k]['dm'] * 100:4.0f}%")
    print()
    print(f"  WSC（水溶性糖）      {wsc:.4f}   （青贮建议 ≥ 0.08–0.10）")
    print(f"  NDF（中性洗涤纤维）  {ndf:.4f}")
    print(f"  ADF（酸性洗涤纤维）  {adf:.4f}")
    print(f"  ADL（木质素）        {adl:.4f}")
    print(f"  粗蛋白 CP            {cp:.4f}")
    print(f"  → 半纤维素 H = NDF−ADF = {H:.4f}")
    print(f"  → 纤维素   C = ADF−ADL = {C:.4f}")
    print(f"  → 木质素   L = ADL     = {L:.4f}")
    print()
    print("可直接复制的参数（按需要加 --scale）：")
    print(f"  --set DM={dm_total:.3f} --set WSC0={wsc:.4f}          # Scale 1 / 3")
    print(f"  --set H0={H:.4f} --set C0={C:.4f} --set L0={L:.4f}   # Scale 2")
    print()
    if dm_total < 0.25:
        print("提示：DM < 25%，高水分——梭菌窗口大。建议混入秸秆/麸皮把 DM 提到 30%–35%。")
    elif dm_total > 0.45:
        print("提示：DM > 45%，过干难压实、易霉变。建议混入麦苗/果渣或加水。")
    else:
        print("提示：DM 落在 25%–45% 区间，处于可青贮范围（最优 30%–35%）。")
    if wsc < 0.08:
        print("提示：WSC < 8% DM，产酸不足。建议加糖蜜 2%–4% 或接种乳酸菌。")
    if adl > 0.08:
        print("提示：ADL > 8% DM，木质素屏蔽强，纤维可发酵性差（选期/氨化/碱处理可改善）。")
    print("注：以上组分为典型区间中值，正式设计必须用实测值替换。")


# ---------------------------------------------------------------------------
# 八、CLI
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
        description="六级递进纤维质物料转化动力学模型引擎（青贮/纤维/堆肥/果渣饲料）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("纪律约定")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_common(sp, need_scale=True):
        if need_scale:
            sp.add_argument("--scale", type=int, choices=[1, 2, 3, 4, 5, 6], required=True,
                            help="手动指定模型 Scale（1..6）")
        sp.add_argument("--set", action="append", default=[], metavar="K=V",
                        help="覆盖参数，可重复，如 --set DM=0.33 --set WSC0=0.12")

    p = sub.add_parser("list", help="列出模型面板与案例")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("params", help="查看某 Scale 的案例参数")
    add_common(p)
    p.set_defaults(func=cmd_params)

    p = sub.add_parser("simulate", help="入口一：时程仿真")
    add_common(p)
    p.add_argument("--tend", type=float, default=168.0, help="仿真时长 h（默认 168）")
    p.add_argument("--out", default=None, help="保存曲线 PNG")
    p.set_defaults(func=cmd_simulate)

    p = sub.add_parser("control", help="入口一：控制要点/策略")
    p.add_argument("--scale", type=int, choices=[1, 2, 3, 4, 5, 6], default=None,
                   help="指定 Scale；省略则输出全部")
    p.set_defaults(func=cmd_control)

    p = sub.add_parser("demo", help="入口二：真实案例 Demo 演示")
    p.add_argument("--scale", type=int, choices=[1, 2, 3, 4, 5, 6], default=None)
    p.add_argument("--all", action="store_true", help="演示全部 6 个 Scale")
    p.add_argument("--set", action="append", default=[], metavar="K=V")
    p.add_argument("--outdir", default="fiber_demo", help="图片输出目录")
    p.add_argument("--tend", type=float, default=None, help="覆盖各 Scale 默认仿真时长")
    p.set_defaults(func=cmd_demo)

    p = sub.add_parser("mix", help="把物料配比折算成模型参数（秸秆/麦苗/果渣/麸皮/糖蜜）")
    p.add_argument("--straw", type=float, default=0.0, help="玉米秸秆配比")
    p.add_argument("--grass", type=float, default=0.0, help="麦苗配比")
    p.add_argument("--pomace", type=float, default=0.0, help="苹果渣配比")
    p.add_argument("--bran", type=float, default=0.0, help="麸皮配比")
    p.add_argument("--molasses", type=float, default=0.0, help="糖蜜配比")
    p.add_argument("--basis", choices=["fresh", "dry"], default="fresh",
                   help="配比基准：fresh=鲜重（默认）/ dry=干重")
    p.set_defaults(func=cmd_mix)

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
