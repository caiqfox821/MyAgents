#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""riskcalc.py — 跨域风险评估计算器（纯标准库，无第三方依赖）

设计原则
--------
1. 只做数学与统计，**不内置任何 ADI/MRL/限量/HBGV 数值**。指导值必须由使用者
   按权威来源（JECFA/JMPR/JEMRA/EFSA/CFSA/GB）输入并注明出处。
2. 单位不做"猜测式"自动换算，只做**显式**指定（如 --conc-unit ug/kg --exp-unit mg/kg_bw_d）。
   暴露量内部统一为 mg/kg bw/d；浓度与消费量按输入单位换算后求和。
3. 输出人读表格；`--json` 输出机读结果，便于落盘与复算。

子命令
------
  edi     膳食暴露（多点累加）
  hq      危害商
  moe     暴露边界
  ilcr    终生致癌风险增量
  iesti   农药急性 IESTI（Case 1 / 2a / 2b / 3）
  hbgv    健康指导值推导（POD / UF）
  ttc     毒理学关注阈值比较
  mc      Monte Carlo 概率暴露 + 敏感性筛查
  demo    演示（全部为假设值）

免责：本脚本为计算辅助工具，输出不构成合规判定或安全结论。
"""

import argparse
import json
import math
import random
import statistics
import sys
from typing import Callable, Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------- 单位换算
# 质量统一折算到 mg
MASS_TO_MG = {"mg": 1.0, "ug": 1e-3, "µg": 1e-3, "ng": 1e-6, "g": 1e3, "kg": 1e6}
# 消费量统一折算到 kg
AMOUNT_TO_KG = {"kg": 1.0, "g": 1e-3, "mg": 1e-6}

# TTC 阈值（µg/人·d，按 60 kg 成人）。
# 出处（已按原著核实）：WHO/FAO EHC 240（2020 更新）§4.5 TTC 决策树（改编自 WHO 2015a），
# 公共知识库 `公共知识/书库/guides/WHO_EHC240_S4.5_genotoxicity_2020.pdf` 物理 p.78；
# 逐 kg 体重阈值与 DNA 反应层依据见同文件 p.67（Kroes et al. 2004，基于 >730 种致癌物 potency 分布）。
# 对应条目：公共知识/技术指南/风险评估-证据条目与出处.md 条目 3-1、3-2、3-3。
# 括号内为 µg/kg bw/d 原值；仍以 EFSA/WHO/iTTC 现行文本为准（短时程暴露另有 LTL-TTC 分级）。
TTC_THRESHOLDS_UG_PER_DAY = {
    "DNA": 0.15,   # 0.0025 µg/kg bw/d，DNA 反应性致突变（可能）；亦与 ICH M7 致突变杂质一致
    "I": 1800.0,   # 30 µg/kg bw/d，Cramer class I（低毒性结构，经充分代谢解毒）
    "II": 540.0,   # 9 µg/kg bw/d，Cramer class II
    "III": 90.0,   # 1.5 µg/kg bw/d，Cramer class III（有明显结构警示）
    "OP": 18.0,    # 0.3 µg/kg bw/d，有机磷/氨基甲酸酯（AChE 抑制活性）
}


def _mass_factor(unit: str) -> float:
    u = unit.strip()
    if u not in MASS_TO_MG:
        raise ValueError(f"未知质量单位: {unit}（可用: {', '.join(MASS_TO_MG)}）")
    return MASS_TO_MG[u]


def _amount_factor(unit: str) -> float:
    u = unit.strip()
    if u not in AMOUNT_TO_KG:
        raise ValueError(f"未知消费量单位: {unit}（可用: {', '.join(AMOUNT_TO_KG)}）")
    return AMOUNT_TO_KG[u]


def _floats(s: str) -> List[float]:
    return [float(x) for x in s.split(",") if x.strip() != ""]


def _align(a: Sequence[float], b: Sequence[float]) -> Tuple[List[float], List[float]]:
    """把 浓度点 与 消费量点 对齐成逐项相乘的序列。

    - 等长：逐项相乘（对应同一食品/同一情景）
    - 一方为单值：广播
    - 均多值且不等长：拒绝（语义不清，避免静默算错）
    """
    if len(a) == len(b):
        return list(a), list(b)
    if len(a) == 1:
        return list(a) * len(b), list(b)
    if len(b) == 1:
        return list(a), list(b) * len(a)
    raise ValueError(
        f"浓度点({len(a)}) 与消费量点({len(b)}) 数量不一致且均非单值；"
        "请按食品顺序一一对应，或分别计算后相加。"
    )


# ---------------------------------------------------------------- 基础计算
def calc_edi(concs, crs, bw, conc_unit="mg", cr_unit="kg", exp_unit="mg/kg_bw_d"):
    """膳食暴露量 = Σ(浓度 × 消费量) / 体重，返回统一单位下的值。"""
    if bw <= 0:
        raise ValueError("体重必须 > 0")
    c, q = _align(concs, crs)
    mf, af = _mass_factor(conc_unit), _amount_factor(cr_unit)
    # Σ (mg) / kg bw  -> mg/kg bw
    total_mg = sum(ci * mf * qi * af for ci, qi in zip(c, q))
    value = total_mg / bw
    # 换算到 mg/kg bw/d 或 ug/kg bw/d
    if exp_unit in ("mg/kg_bw_d", "mg/kg bw/d"):
        return value, "mg/kg bw/d"
    if exp_unit in ("ug/kg_bw_d", "ug/kg bw/d", "µg/kg_bw_d"):
        return value * 1e3, "ug/kg bw/d"
    raise ValueError(f"未知暴露单位: {exp_unit}")


def calc_hq(exposure, hbgv):
    if hbgv <= 0:
        raise ValueError("健康指导值必须 > 0")
    hq = exposure / hbgv
    if hq <= 1:
        level = "可接受（HQ ≤ 1）"
    elif hq <= 3:
        level = "需关注（1 < HQ ≤ 3）"
    else:
        level = "高风险（HQ > 3）"
    return hq, hq * 100.0, level


def calc_moe(pod, exposure):
    if exposure <= 0:
        raise ValueError("暴露量必须 > 0（MOE 无法计算）")
    moe = pod / exposure
    if moe >= 10000:
        level = "low concern（MOE ≥ 10 000）— EFSA SC 2025, EFSA J 23(8):e9606 ※前提：POD 须为动物研究 BMDL10；含义=风险管理优先级低，并非'无害'，不排除减排措施"
    elif moe >= 1000:
        level = "关切较高（1 000 ≤ MOE < 10 000）※1 000/100 两档为管理约定（EFSA 只定义 10 000），个案阈值见 references/03 §五"
    else:
        level = "需重点关注（MOE < 1 000）※EFSA SC 2025：MOE < 10 000 即关切更高，越小越关切"
    return moe, level


def calc_ilcr(cdi, sf):
    v = cdi * sf
    if v <= 1e-6:
        level = "通常可接受（ILCR ≤ 1e-6）"
    elif v <= 1e-4:
        level = "关注区间（1e-6 < ILCR ≤ 1e-4）"
    else:
        level = "高风险（ILCR > 1e-4）"
    return v, level


def calc_iesti(case, lp, hr, bw, u=None, stmr=None, vf=3.0):
    """JMPR IESTI 四情形。lp 大份餐(kg)，hr 最高残留(mg/kg)，u 单位重(kg)，stmr 中位残留。"""
    if bw <= 0:
        raise ValueError("体重必须 > 0")
    case = case.lower()
    if case in ("1", "case1"):
        if lp is None or hr is None:
            raise ValueError("Case 1 需要 --lp 与 --hr")
        return (lp * hr) / bw, "IESTI = (LP × HR) / bw"
    if case in ("2a", "case2a"):
        if None in (u, lp, hr):
            raise ValueError("Case 2a 需要 --u / --lp / --hr（且 U < LP）")
        if not (u < lp):
            raise ValueError("Case 2a 要求 U < LP；若 U ≥ LP 请用 Case 2b")
        return (u * hr * vf + (lp - u) * hr) / bw, "IESTI = [U×HR×vf + (LP−U)×HR] / bw"
    if case in ("2b", "case2b"):
        if None in (u, lp, hr):
            raise ValueError("Case 2b 需要 --u / --lp / --hr（且 U ≥ LP）")
        if not (u >= lp):
            raise ValueError("Case 2b 要求 U ≥ LP；若 U < LP 请用 Case 2a")
        return (u * hr * vf) / bw, "IESTI = (U × HR × vf) / bw"
    if case in ("3", "case3"):
        if None in (lp, stmr):
            raise ValueError("Case 3 需要 --lp 与 --stmr")
        return (lp * stmr) / bw, "IESTI = (LP × STMR) / bw"
    raise ValueError("case 取 1 / 2a / 2b / 3")


def calc_hbgv(pod, uf_overall):
    if uf_overall <= 0:
        raise ValueError("UF 必须 > 0")
    return pod / uf_overall


def calc_ttc(exposure_ug_per_day, cramer_class):
    key = cramer_class.strip().upper()
    if key not in TTC_THRESHOLDS_UG_PER_DAY:
        raise ValueError(f"class 取 DNA / I / II / III / OP，收到 {cramer_class}")
    thr = TTC_THRESHOLDS_UG_PER_DAY[key]
    ratio = exposure_ug_per_day / thr
    if ratio <= 1:
        level = "低于 TTC 阈值（筛查未提示关注）"
    else:
        level = "超过 TTC 阈值（需进一步毒理学评估）"
    return thr, ratio, level


# ---------------------------------------------------------------- 分布抽样
def make_sampler(spec: str, rng: random.Random) -> Callable[[], float]:
    """spec 形如 lognormal:mu:sd / normal:mean:sd / uniform:lo:hi / empirical:v1,v2,.. / point:v

    lognormal 参数按**自然对数空间**的 mu 与 sd（即 ln 值的均值与标准差）解释；
    若只有原始尺度的中位数与 GSD，请先换算：mu=ln(median), sd=ln(GSD)。
    """
    parts = spec.split(":")
    kind = parts[0].strip().lower()
    if kind == "point":
        v = float(parts[1])
        return lambda: v
    if kind == "lognormal":
        mu, sd = float(parts[1]), float(parts[2])
        return lambda: rng.lognormvariate(mu, sd)
    if kind == "normal":
        mu, sd = float(parts[1]), float(parts[2])
        return lambda: max(0.0, rng.gauss(mu, sd))
    if kind == "uniform":
        lo, hi = float(parts[1]), float(parts[2])
        return lambda: rng.uniform(lo, hi)
    if kind == "empirical":
        vals = [float(x) for x in parts[1].split(",") if x.strip() != ""]
        if not vals:
            raise ValueError("empirical 需要至少一个值")
        return lambda: rng.choice(vals)
    raise ValueError(f"未知分布: {kind}（可用: point/lognormal/normal/uniform/empirical）")


def _pct(sorted_vals: List[float], p: float) -> float:
    """线性插值分位数（p 取 0~1）。"""
    if not sorted_vals:
        raise ValueError("空序列")
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = p * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def _rank(values: List[float]) -> List[float]:
    """平均秩（处理并列）。"""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(x: List[float], y: List[float]) -> float:
    n = len(x)
    if n < 3:
        return 0.0
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx <= 0 or syy <= 0:
        return 0.0
    return sxy / math.sqrt(sxx * syy)


def monte_carlo(specs: Dict[str, str], formula: Callable[[Dict[str, float]], float],
                n: int = 20000, seed: Optional[int] = 42, hbgv: Optional[float] = None):
    """通用 Monte Carlo：各输入按 spec 抽样，代入 formula 得到输出分布。"""
    if n < 1000:
        raise ValueError("n 建议 ≥ 10 000（最低 1 000）")
    rng = random.Random(seed)
    samplers = {k: make_sampler(v, rng) for k, v in specs.items()}
    outputs: List[float] = []
    inputs: Dict[str, List[float]] = {k: [] for k in specs}
    for _ in range(n):
        draw = {k: f() for k, f in samplers.items()}
        for k, v in draw.items():
            inputs[k].append(v)
        outputs.append(formula(draw))

    s = sorted(outputs)
    res = {
        "n": n,
        "seed": seed,
        "mean": sum(outputs) / n,
        "median": _pct(s, 0.5),
        "sd": statistics.pstdev(outputs) if n > 1 else 0.0,
        "p50": _pct(s, 0.50),
        "p90": _pct(s, 0.90),
        "p95": _pct(s, 0.95),
        "p99": _pct(s, 0.99),
        "min": s[0],
        "max": s[-1],
    }
    if hbgv is not None and hbgv > 0:
        exceed = sum(1 for v in outputs if v > hbgv)
        res["hbgv"] = hbgv
        res["p_exceed_hbgv"] = exceed / n
        res["hq_p95"] = res["p95"] / hbgv
    # 敏感性：秩相关（对非线性单调关系稳健）；非严格 Sobol 指数
    res["sensitivity_spearman"] = {
        k: _pearson(_rank(vals), _rank(outputs)) for k, vals in inputs.items()
    }
    res["sensitivity_note"] = (
        "秩相关系数仅作敏感性筛查；严格方差分解（一阶/总效应 Sobol）请用 R sensitivity/salib。"
    )
    return res, outputs


# ---------------------------------------------------------------- OAT 敏感性
def oat_sensitivity(base: Dict[str, float], formula: Callable[[Dict[str, float]], float],
                    delta: float = 0.1):
    """单因素（One-At-a-Time）：各输入 ±delta 相对变化时的输出相对变化。"""
    base_out = formula(base)
    rows = []
    for k, v in base.items():
        if v == 0:
            rows.append({"input": k, "base": v, "plus": None, "minus": None,
                         "elasticity_plus": None, "elasticity_minus": None})
            continue
        hi = dict(base)
        lo = dict(base)
        hi[k] = v * (1 + delta)
        lo[k] = v * (1 - delta)
        oh, ol = formula(hi), formula(lo)
        rows.append({
            "input": k,
            "base": v,
            "plus": oh,
            "minus": ol,
            "elasticity_plus": (oh - base_out) / base_out / delta if base_out else None,
            "elasticity_minus": (ol - base_out) / base_out / (-delta) if base_out else None,
        })
    return base_out, rows


# ---------------------------------------------------------------- CLI
def _fmt(x: float) -> str:
    if x == 0:
        return "0"
    if abs(x) < 1e-3 or abs(x) >= 1e5:
        return f"{x:.6g}"
    return f"{x:.6g}"


def _print_kv(d: Dict, indent: str = "") -> None:
    for k, v in d.items():
        if isinstance(v, dict):
            print(f"{indent}{k}:")
            _print_kv(v, indent + "  ")
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            print(f"{indent}{k}:")
            for row in v:
                print(f"{indent}  - " + ", ".join(
                    f"{kk}={_fmt(vv) if isinstance(vv, float) else vv}" for kk, vv in row.items()))
        elif isinstance(v, float):
            print(f"{indent}{k}: {_fmt(v)}")
        else:
            print(f"{indent}{k}: {v}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="riskcalc.py",
        description="跨域风险评估计算器（不含任何限量/ADI 内置值）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例见 --help 顶部文档字符串或运行: riskcalc.py demo",
    )
    p.add_argument("--json", action="store_true", help="输出 JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("edi", help="膳食暴露 Σ(浓度×消费量)/体重")
    e.add_argument("--conc", required=True, help="浓度，逗号分隔（按食品顺序）")
    e.add_argument("--cr", required=True, help="消费量，逗号分隔")
    e.add_argument("--bw", type=float, required=True, help="体重 kg")
    e.add_argument("--conc-unit", default="mg", help="mg/ug/ng/g/kg（默认 mg）")
    e.add_argument("--cr-unit", default="kg", help="kg/g（默认 kg）")
    e.add_argument("--exp-unit", default="mg/kg_bw_d", help="mg/kg_bw_d 或 ug/kg_bw_d")

    for name, args, helptext in (
        ("hq", ("--exp", "--hbgv"), "危害商 HQ = 暴露/指导值"),
        ("moe", ("--pod", "--exp"), "MOE = POD/暴露"),
        ("ilcr", ("--cdi", "--sf"), "ILCR = CDI × SF"),
        ("hbgv", ("--pod", "--uf"), "HBGV = POD/UF"),
    ):
        sp = sub.add_parser(name, help=helptext)
        for a in args:
            sp.add_argument(a, type=float, required=True)

    i = sub.add_parser("iesti", help="农药急性 IESTI")
    i.add_argument("--case", required=True, choices=["1", "2a", "2b", "3"])
    i.add_argument("--lp", type=float, help="大份餐 kg（P97.5）")
    i.add_argument("--hr", type=float, help="最高残留 mg/kg")
    i.add_argument("--u", type=float, help="单位重 kg")
    i.add_argument("--stmr", type=float, help="中位残留 mg/kg")
    i.add_argument("--vf", type=float, default=3.0, help="变异系数，默认 3")
    i.add_argument("--bw", type=float, required=True)
    i.add_argument("--arfad", type=float, help="ARfD，用于 %ARfD")

    t = sub.add_parser("ttc", help="TTC 阈值比较")
    t.add_argument("--exp", type=float, required=True, help="暴露 µg/人·d")
    t.add_argument("--class", dest="cramer", default="III",
                   help="Cramer 类别 I/II/III，OP（有机磷/氨基甲酸酯），DNA（DNA 反应性致突变，0.15 µg/人·d）")

    m = sub.add_parser("mc", help="Monte Carlo 概率暴露")
    m.add_argument("--conc", required=True, help="浓度分布，如 lognormal:mu:sd 或 empirical:0.1,0.2")
    m.add_argument("--cr", required=True, help="消费量分布")
    m.add_argument("--bw", required=True, help="体重分布，如 normal:60:8 或 point:60")
    m.add_argument("--conc-unit", default="mg")
    m.add_argument("--cr-unit", default="kg")
    m.add_argument("--n", type=int, default=20000)
    m.add_argument("--seed", type=int, default=42)
    m.add_argument("--hbgv", type=float, help="给出则计算超限概率与 P95 的 HQ")

    s = sub.add_parser("sens", help="单因素敏感性（OAT）")
    s.add_argument("--conc", type=float, required=True)
    s.add_argument("--cr", type=float, required=True)
    s.add_argument("--bw", type=float, required=True)
    s.add_argument("--delta", type=float, default=0.1)

    sub.add_parser("demo", help="演示（假设值）")
    # 允许 --json 放在子命令之后（default=SUPPRESS 以免覆盖主解析器的值）
    for sp in sub.choices.values():
        sp.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="输出 JSON")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _dispatch(args)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


def _dispatch(args) -> int:
    out: Dict = {"command": args.cmd}

    if args.cmd == "edi":
        val, unit = calc_edi(_floats(args.conc), _floats(args.cr), args.bw,
                             args.conc_unit, args.cr_unit, args.exp_unit)
        c, q = _align(_floats(args.conc), _floats(args.cr))
        out.update({"items": len(c), "exposure": val, "unit": unit, "bw": args.bw})

    elif args.cmd == "hq":
        hq, pct, level = calc_hq(args.exp, args.hbgv)
        out.update({"hq": hq, "percent_hbgv": pct, "level": level,
                    "exposure": args.exp, "hbgv": args.hbgv})

    elif args.cmd == "moe":
        moe, level = calc_moe(args.pod, args.exp)
        out.update({"moe": moe, "level": level, "pod": args.pod, "exposure": args.exp})

    elif args.cmd == "ilcr":
        v, level = calc_ilcr(args.cdi, args.sf)
        out.update({"ilcr": v, "level": level, "cdi": args.cdi, "sf": args.sf})

    elif args.cmd == "hbgv":
        v = calc_hbgv(args.pod, args.uf)
        out.update({"hbgv": v, "pod": args.pod, "uf": args.uf,
                    "formula": "HBGV = POD / UF"})

    elif args.cmd == "iesti":
        v, formula = calc_iesti(args.case, args.lp, args.hr, args.bw,
                                u=args.u, stmr=args.stmr, vf=args.vf)
        out.update({"iesti": v, "unit": "mg/kg bw", "case": args.case, "formula": formula})
        if args.arfad:
            out["percent_arfad"] = v / args.arfad * 100
            out["arfad"] = args.arfad

    elif args.cmd == "ttc":
        thr, ratio, level = calc_ttc(args.exp, args.cramer)
        out.update({"ttc_threshold_ug_per_day": thr, "exposure_ug_per_day": args.exp,
                    "ratio": ratio, "level": level, "cramer_class": args.cramer,
                    "note": "阈值已按 WHO/FAO EHC 240(2020更新)§4.5 TTC 决策树核实（公共知识/技术指南/风险评估-证据条目与出处.md 条目 3-1~3-3）；仍须核对 EFSA/WHO 现行意见版本"})

    elif args.cmd == "mc":
        mfa, afa = _mass_factor(args.conc_unit), _amount_factor(args.cr_unit)
        spec = {"conc": args.conc, "cr": args.cr, "bw": args.bw}
        # 输入单位在抽样后统一折算到 mg/kg bw
        formula = lambda d: d["conc"] * mfa * d["cr"] * afa / d["bw"]
        res, _ = monte_carlo(spec, formula, n=args.n, seed=args.seed, hbgv=args.hbgv)
        res["unit"] = "mg/kg bw/d"
        out.update(res)

    elif args.cmd == "sens":
        base = {"conc": args.conc, "cr": args.cr, "bw": args.bw}
        formula = lambda d: d["conc"] * d["cr"] / d["bw"]
        base_out, rows = oat_sensitivity(base, formula, args.delta)
        out.update({"base_exposure": base_out, "delta": args.delta, "rows": rows})

    elif args.cmd == "demo":
        return _demo()

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"[{args.cmd}]")
        _print_kv({k: v for k, v in out.items() if k != "command"})
        print("\n提示：本工具只做算术与抽样，不含任何限量/ADI 内置值；")
        print("      指导值须由权威来源输入并注明机构、年份与版本。")
    return 0


def _demo() -> int:
    """全部为演示用假设值，非真实限量/监测值。"""
    print("=" * 66)
    print("riskcalc.py 演示 —— 所有数值均为假设值，非真实限量或监测结果")
    print("=" * 66)

    print("\n[示例1] 慢性点评估 + HQ（假设 ADI=0.02 mg/kg bw/d）")
    e1, u1 = calc_edi([0.08], [0.12], 60.0)
    hq1, pct1, lv1 = calc_hq(e1, 0.02)
    print(f"  一般人群 EDI = {_fmt(e1)} {u1}; HQ = {_fmt(hq1)} ({pct1:.2f}% ADI) -> {lv1}")
    e2, _ = calc_edi([0.25], [0.35], 60.0)
    hq2, pct2, lv2 = calc_hq(e2, 0.02)
    print(f"  高端人群 EDI = {_fmt(e2)} mg/kg bw/d; HQ = {_fmt(hq2)} ({pct2:.2f}% ADI) -> {lv2}")

    print("\n[示例2] 急性 IESTI Case 2a（假设 ARfD=0.05 mg/kg bw）")
    i2, f2 = calc_iesti("2a", lp=0.50, hr=0.30, bw=60.0, u=0.10, vf=3.0)
    print(f"  {f2}")
    print(f"  IESTI = {_fmt(i2)} mg/kg bw; %ARfD = {i2 / 0.05 * 100:.1f}%")

    print("\n[示例3] MOE（假设 BMDL10=0.5，暴露 5e-5）")
    m3, lv3 = calc_moe(0.5, 5e-5)
    print(f"  MOE = {_fmt(m3)} -> {lv3}")

    print("\n[示例4] ILCR（假设 SF=0.5，CDI=2e-5）")
    c4, lv4 = calc_ilcr(2e-5, 0.5)
    print(f"  ILCR = {_fmt(c4)} -> {lv4}")

    print("\n[示例5] HBGV 推导（假设 BMDL=5 mg/kg bw/d，UF=100）")
    print(f"  HBGV = {_fmt(calc_hbgv(5.0, 100.0))} mg/kg bw/d")

    print("\n[示例6] TTC 比较（假设暴露 0.02 µg/kg bw/d × 60 kg = 1.2 µg/d，Cramer III）")
    thr, ratio, lv6 = calc_ttc(1.2, "III")
    print(f"  阈值 {_fmt(thr)} µg/人·d; 比值 {ratio:.4f} -> {lv6}")

    print("\n[示例7] Monte Carlo 概率暴露（假设分布，n=20000）")
    res, _ = monte_carlo(
        {"conc": "lognormal:-2.6:0.6", "cr": "empirical:0.05,0.12,0.2,0.35",
         "bw": "normal:60:8"},
        lambda d: d["conc"] * d["cr"] / d["bw"], n=20000, seed=42, hbgv=0.02)
    print(f"  mean={_fmt(res['mean'])} p95={_fmt(res['p95'])} p99={_fmt(res['p99'])}")
    print(f"  超 ADI 概率 = {res['p_exceed_hbgv'] * 100:.2f}%; P95 的 HQ = {res['hq_p95']:.4f}")
    top = sorted(res["sensitivity_spearman"].items(), key=lambda kv: -abs(kv[1]))
    print("  敏感性(秩相关): " + ", ".join(f"{k}={v:+.3f}" for k, v in top))

    print("\n[示例8] 单因素敏感性 OAT（±10%）")
    base_out, rows = oat_sensitivity({"conc": 0.08, "cr": 0.12, "bw": 60.0},
                                     lambda d: d["conc"] * d["cr"] / d["bw"], 0.1)
    print(f"  基准暴露 = {_fmt(base_out)}")
    for r in rows:
        print(f"  {r['input']:>4}: +10% -> {_fmt(r['plus'])} (弹性 {r['elasticity_plus']:+.3f})")

    print("\n" + "=" * 66)
    print("免责：以上均为教学演示值，不得用于任何实际合规判定。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
