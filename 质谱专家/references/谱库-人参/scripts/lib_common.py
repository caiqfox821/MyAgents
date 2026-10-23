#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公共工具：分子式解析 / 单同位素质量 / 加合物→m/z / 名称归一化与目标匹配"""
import os, re

# 单同位素原子质量
MASS = {
 "H":1.0078250319,"C":12.0,"N":14.0030740052,"O":15.9949146221,"Na":22.98976928,
 "S":31.97207069,"K":38.96370649,"Cl":34.96885271,"P":30.97376151,"F":18.99840320,
 "Br":78.9183376,"I":126.904468,"Si":27.9769265327,"Mg":23.98504190,"Ca":39.96259098,
 "Fe":55.93493633,"Zn":63.92914201,"Se":79.9165213,"B":11.0093055,"As":74.9215964,
 "Li":7.01600455,"Al":26.98153863,"Cu":62.92959772,"Mn":54.93804964,"Sn":119.9021966,
}
PROTON = 1.007276466

def parse_formula(f):
    """'C54H92O23' -> {'C':54,...}"""
    if not f: return None
    d = {}
    for el, n in re.findall(r'([A-Z][a-z]?)(\d*)', f):
        if el in MASS:
            d[el] = d.get(el, 0) + (int(n) if n else 1)
    return d or None

def monoisotopic(f):
    d = parse_formula(f)
    if not d: return None
    return round(sum(MASS[e]*n for e, n in d.items()), 5)

def adduct_mz(mass, adduct, charge=1):
    """由中性单同位素质量和加合物字符串计算母离子 m/z"""
    if mass is None: return None
    a = (adduct or "").replace(" ", "").upper()
    # 显式表（相对中性分子的净位移）
    shift = {
      "[M+H]+":  1*PROTON,
      "[M+NA]+": 22.98976928,
      "[M+NH4]+":18.033823 + 1*PROTON,   # NH4 = N+4H
      "[M+K]+":  38.96370649,
      "[M+LI]+": 7.01600455,
      "[M+H-H2O]+": 1*PROTON - 18.0105647,
      "[M]+":    0.0, "[M]+.": 0.0,
      "[M-H]-":  -1*PROTON,
      "[M+CL]-": 34.96885271,
      "[M+HCOO]-": 44.997655, "[M+FA-H]-": 44.997655,
      "[M+CH3COO]-": 59.013305, "[M+AC-H]-": 59.013305,
      "[M+NA-2H]-": 22.98976928 - 2*PROTON,
      "[M]-":    0.0,
    }
    if a in shift:
        return round(mass + shift[a], 5)
    return None

def norm_name(s):
    """名称归一化：转小写、统一希腊字母、去掉所有非字母数字字符"""
    if not s: return ""
    s = s.replace("β","beta").replace("γ","gamma").replace("α","alpha")
    return re.sub(r'[^a-z0-9]', '', s.lower())

def gnps_base_name(n):
    """GNPS NAME 去离子后缀，如 'Quercetin M-H' -> 'Quercetin'"""
    if not n: return ""
    n = n.strip().strip('"')
    n = re.sub(r'\s+\d*M[+\-].*$', '', n, flags=re.I)
    n = re.sub(r'\s+\[M.*$', '', n)
    return n.strip()

# 目标同义名（归一化后）：把库里可能出现的别名映射到目标名
SYNONYMS = {
 # —— 活性成分别名 ——
 "gammaaminobutyricacid":"4-Aminobutyric acid",
 "4aminobutanoicacid":"4-Aminobutyric acid",
 "arginine":"L-Arginine",
 "betasitosterol":"beta-Sitosterol",
 "sitosterol":"beta-Sitosterol",
 "34dihydroxybenzoicacid":"Protocatechuic acid",
 "25dihydroxybenzoicacid":"Gentisic acid",
 "trans4coumaricacid":"p-Coumaric acid",
 "4coumaricacid":"p-Coumaric acid",
 "transferulicacid":"Ferulic acid",
 "5hydroxymethyl2furaldehyde":"5-Hydroxymethylfurfural",
 # —— 人参皂苷别名（MassBank 多库同物异名）——
 "sanchinosidec1":"Ginsenoside Rg1",
 "sanchinosiderg1":"Ginsenoside Rg1",
 "panaxosiderg1":"Ginsenoside Rg1",
 "ginsenosideg1":"Ginsenoside Rg1",
 "ginsenosidea2":"Ginsenoside Rg1",
 "panaxosidea":"Ginsenoside Rg1",
 "sanchinosidere":"Ginsenoside Re",
 "panaxosidere":"Ginsenoside Re",
 "ginsenosideb2":"Ginsenoside Re",
 "gypenosideviii":"Ginsenoside Rd",
 "panaxosiderc":"Ginsenoside Rc",
 "ginsenosiderg3sform":"Ginsenoside Rg3",
 "ginsenosiderg3rform":"Ginsenoside Rg3",
 "ginsenosiderh2sform":"Ginsenoside Rh2",
 "ginsenosiderh2rform":"Ginsenoside Rh2",
 # —— 金线莲（黄酮苷系统名 → 俗名）——
 "quercetin3orutinoside":"Rutin",
 "quercetin3oglucoside":"Isoquercitrin",
 "quercetin3ogalactoside":"Hyperoside",
 "kaempferol3oglucoside":"Astragalin",
 "kaempferol3orutinoside":"Nicotiflorin",
 "kaempferol3ogalactoside":"Trifolin",
 "isorhamnetin3orutinoside":"Narcissin",
 "isorhamnetin3oglucoside":"Isorhamnetin-3-O-glucoside",
}

def load_targets(path):
    t = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"): continue
            p = line.split("\t")
            t.append({"name": p[0], "group": p[1] if len(p) > 1 else "",
                      "note": p[2] if len(p) > 2 else ""})
    return t

def target_index(targets):
    """返回 {归一化名: 目标名}"""
    idx = {}
    for t in targets:
        idx[norm_name(t["name"])] = t["name"]
    for syn, tgt in SYNONYMS.items():
        idx.setdefault(syn, tgt)
    return idx

def strip_variants(s):
    """去掉立体/衍生物后缀，便于归并到目标名：'Ginsenoside Rg3(S-FORM)' -> 'Ginsenoside Rg3'"""
    if not s: return s
    s = re.sub(r'\s*\([^)]*\)', '', s)                       # 去 (S-FORM)/(R)/(20S) 等
    s = re.sub(r'\b(form|forms|isomer|isomers|type)\b', '', s, flags=re.I)
    return s.strip(' -_')

def match_target(name, idx):
    """返回匹配到的目标名，或 None（多级归一化：原名/去离子后缀/去立体后缀）"""
    for cand in (name, gnps_base_name(name),
                 strip_variants(name), strip_variants(gnps_base_name(name))):
        n = idx.get(norm_name(cand))
        if n:
            return n
    return None
