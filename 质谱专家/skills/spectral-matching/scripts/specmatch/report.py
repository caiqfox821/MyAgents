# -*- coding: utf-8 -*-
"""
specmatch.report —— 置信度分级与报告
===================================

把相似度分数翻译成 **Schymanski 五级** 置信度，并生成 Markdown / CSV 结论。
分级是**启发式**：最终定级必须结合保留时间、标准品、异构体信息人工确认。
"""
import csv
import io

# Schymanski 五级（2014）
LEVELS = {
    1: "Level 1 已确证结构（标准品 + 保留时间一致）",
    2: "Level 2 推定结构（谱库/诊断证据高度匹配）",
    3: "Level 3 候选结构（有证据的候选物）",
    4: "Level 4 唯一分子式",
    5: "Level 5 仅精确质量",
}


def schymanski_level(score, method="entropy", n_matched=0,
                     has_standard=False, rt_match=False, has_formula=False,
                     strong=0.80, tentative=0.50, min_peaks=4):
    """返回 (level, 理由)。"""
    if has_standard and rt_match:
        return 1, "标准品保留时间一致"
    if score >= strong and n_matched >= min_peaks:
        return 2, "%s=%.3f（≥%.2f）且匹配峰 %d（≥%d），推定结构" % (
            method, score, strong, n_matched, min_peaks)
    if score >= tentative:
        return 3, "%s=%.3f 介于 %.2f–%.2f，候选结构" % (
            method, score, tentative, strong)
    if has_formula:
        return 4, "仅有分子式证据"
    return 5, "仅精确质量，无结构证据"


def rank_table(query, results, methods=None):
    """把检索结果整理成二维表（表头固定，便于人工评分/回归）。"""
    if methods is None:
        methods = [k[6:] for k in (results[0] if results else {}) if k.startswith("score_")]
    header = ["rank", "library_id", "compound", "inchikey", "adduct", "ionmode",
              "collision_energy", "precursor_mz"]
    for m in methods:
        header += ["score_" + m, "nmatched_" + m]
    header += ["level", "rationale"]
    rows = []
    for r in results:
        row = [r.get("rank"), r.get("library_id"), r.get("compound"), r.get("inchikey"),
               r.get("adduct"), r.get("ionmode"), r.get("collision_energy"),
               r.get("precursor_mz")]
        for m in methods:
            row += [round(r.get("score_" + m, 0.0), 4), r.get("nmatched_" + m)]
        lvl, why = schymanski_level(
            r.get("score_" + methods[0], 0.0), methods[0],
            r.get("nmatched_" + methods[0], 0),
            has_formula=bool(r.get("formula")))
        row += [lvl, why]
        rows.append(row)
    return header, rows


def to_markdown(query, results, title="谱库匹配报告"):
    lines = ["# %s" % title, ""]
    lines.append("**查询谱**：%s ｜ 前体 m/z %s ｜ %s ｜ 加合物 %s ｜ CE %s ｜ %d 峰" % (
        query.compound_name or query.get("id") or "(未命名)",
        query.precursor_mz, query.ionmode, query.adduct,
        query.collision_energy, len(query)))
    lines.append("")
    if not results:
        lines.append("> 未命中（注意：**查不到 ≠ 不存在**，考虑扩库或用原位解析）。")
        return "\n".join(lines)
    header, rows = rank_table(query, results)
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for row in rows:
        lines.append("| " + " | ".join("" if c is None else str(c) for c in row) + " |")
    lines.append("")
    lines.append("> 分级为启发式：**MS² 库匹配最高到 Level 2**；Level 1 需标准品 + 保留时间；")
    lines.append("> 同分异构/立体异构需 RT 或离子淌度 CCS 区分。")
    return "\n".join(lines)


def to_csv(results, path, methods=None):
    if methods is None:
        methods = [k[6:] for k in (results[0] if results else {}) if k.startswith("score_")]
    header, rows = rank_table({}, results, methods)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path
