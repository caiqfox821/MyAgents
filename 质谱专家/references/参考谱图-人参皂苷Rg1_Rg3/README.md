# 人参皂苷 Rg1 / Rg3 参考质谱图

> 数据来源：**MassBank**（RDF Portal `rdfportal.org/primary/sparql`，dataset = `massbank`）
> 检索日期：2026-10-23 ｜ 检索方式：化合物名 → PubChem CID → InChIKey → 结构锚定反查谱图（非文本检索）

## 一、化合物信息

| 项目 | 人参皂苷 Rg1 | 人参皂苷 Rg3 |
|---|---|---|
| 分子式 | C42H72O14 | C42H72O13 |
| 单同位素质量 | **800.4922** | **784.4973** |
| PubChem CID | 441923 | 9918693 |
| InChIKey | `YURJSTAIMNSZAE-HHNZYBFYSA-N` | `RWXIFXNRCLMQCD-JBVRGBGGSA-N` |
| 苷元 | 原人参三醇 PPT（C30H52O4） | 原人参二醇 PPD（C30H52O3） |
| 糖基 | 2 × 葡萄糖（C6、C20） | 2 × 葡萄糖（C3、C20） |
| 主要加合/前体离子 | [M-H]⁻ 799.48；[M+HCOO]⁻ 845.49；[M+Na]⁺ 823.48 | [M-H]⁻ 783.49；[M+HCOO]⁻ 829.50 |
| 立体异构 | — | 20(S)-型、20(R)-型（一对差向异构体） |

> ⚠️ **数据订正**：MassBank 对 Rg1 记录的 `ch_exact_mass` = 800.492（单同位素质量，正确）；但对 Rg3 记录的是 **785.025（平均分子量，非单同位素质量）**。Rg3 单同位素质量应为 **784.4973**。引用时以单同位素质量为准。

## 二、MassBank 覆盖情况

| 化合物 | 记录数 | 品牌/来源 | 极性 | 仪器 | 备注 |
|---|---|---|---|---|---|
| Rg1 | **15** | RIKEN-PR 11 条 + Univ_Toyama 4 条 | 14 条负离子 + **1 条正离子** | LC-ESI-QTOF（RIKEN）、LC-ESI-ITTOF（Toyama） | 正离子仅 Seq. Toyama 的 MS1（[M+Na]⁺） |
| Rg3 | **44** | RIKEN-PR 41 条（S 型 23 + R 型 21，另有 3 条早期记录） | **全部负离子** | LC-ESI-QTOF | **无正离子参考谱** |

MassBank 全部 117,295 张参考谱中，用 InChIKey 骨架反查可得到上述记录；Rg1/Rg3 均以 **负离子 ESI 为主**。

## 三、本次提取的谱图（8 张，含完整峰表）

| 文件/记录号 | 化合物 | 极性 | 加合物 | MS 级 | 仪器 | 碰撞能 | 峰数 |
|---|---|---|---|---|---|---|---|
| MSBNK-RIKEN-PR307813 | Rg1 | 负 | [M+HCOO]⁻ | MS2 | LC-ESI-QTOF | 6V | 78 |
| MSBNK-Univ_Toyama-TY000193 | Rg1 | 负 | [M+CH3COOH-H]⁻ | MS2 | LC-ESI-ITTOF | — | 28 |
| MSBNK-Univ_Toyama-TY000020 | Rg1 | 负 | [M+CH3COOH-H]⁻ | MS1 | LC-ESI-ITTOF | — | 11 |
| MSBNK-Univ_Toyama-TY000031 | Rg1 | 正 | [M+Na]⁺ | MS1 | LC-ESI-ITTOF | — | 12 |
| MSBNK-RIKEN-PR308546 | Rg3(S) | 负 | [M-H]⁻ | MS2 | LC-ESI-QTOF | 6V | 36 |
| MSBNK-RIKEN-PR308678 | Rg3(S) | 负 | [M+HCOO]⁻ | MS2 | LC-ESI-QTOF | 6V | 128 |
| MSBNK-RIKEN-PR308649 | Rg3(R) | 负 | [M-H]⁻ | MS2 | LC-ESI-QTOF | 6V | 40 |
| MSBNK-RIKEN-PR308618 | Rg3(R) | 负 | [M+HCOO]⁻ | MS2 | LC-ESI-QTOF | 6V | 113 |

- 完整峰表（全部 446 个峰）：`peaks_all.csv`（列：record / compound / ion_mode / adduct / ms_level / mz / relative_intensity / intensity）
- 叠加谱图：`Rg1_mass_spectra.png`、`Rg3_mass_spectra.png`
- **入门讲解**：`讲解_怎么看质谱图.md`（带图 Markdown 教程）、`讲解_怎么看质谱图.docx`（**Word 版，图片已内嵌**）＋ `讲解_如何看质谱图.png`（带文字标注的 Rg1/Rg3 单张谱）、`讲解_碎片路径.png`（母离子→丢糖→苷元的路径示意）；生成脚本 `plot_teach.py`、`build_docx.py`
- 在线查看（MassBank Europe，把记录号替换即可）：
  `https://massbank.eu/MassBank/RecordDisplay?id=MSBNK-RIKEN-PR307813`

## 四、关键碎片归属（负离子 MS2）

| 化合物 | 前体 | 主要碎片（m/z，相对强度） | 归属 |
|---|---|---|---|
| Rg1 | [M+HCOO]⁻ 845.49 | **637.43**(999)、799.48(593)、161.04(309)、638.44(267)、179.06(258)、119.04(174) | 637.43 = [M-H-Glc]⁻（丢 1 个葡萄糖，162 u）；799.48 = [M-H]⁻；161/179/119/101 为糖残基特征离子 |
| Rg1 | [M+CH3COOH-H]⁻ | **799.49**(999)、800.50(677)、475.38(435)、637.43(324) | 799.49=[M-H]⁻；637.43=[M-H-Glc]⁻；**475.38 = PPT 苷元 [aglycone-H]⁻**（C30H51O4） |
| Rg3(S) | [M-H]⁻ 783.49 | **783.49**(999)、161.04(423)、621.44(61)、459.39(58) | 621.44=[M-H-Glc]⁻；**459.39 = PPD 苷元 [aglycone-H]⁻**（C30H51O3） |
| Rg3(S) | [M+HCOO]⁻ 829.49 | **783.49**(999)、784.49(480)、829.49(238)、621.44(38) | 829.49 丢 HCOOH → 783.49 → 621.44 |
| Rg3(R) | [M-H]⁻ 783.49 | **783.49**(999)、621.43(242)、101.02(172)、161.04(147)、113.02(142)、459.38(121) | 与 S 型一致：621.44（-Glc）、459.38（苷元） |
| Rg3(R) | [M+HCOO]⁻ 829.49 | 101.02(999)、113.02(568)、459.38(381)、161.04(359)、119.03(231)、89.02(227) | 糖碎片为主，459.38 苷元离子显著 |

**碎裂规律**：负离子下依次丢失葡萄糖（162 u），末位给出苷元离子 —— Rg1 → PPT 475.38，Rg3 → PPD 459.38。两者以 **苷元离子相差 16 u（多一个 O）** 区分，且 Rg1 比 Rg3 多 1 个氧（C42H72O14 vs C42H72O13）。

## 五、使用注意

1. **Rg3 无正离子参考谱**：MassBank 中 Rg3 的 44 张谱全部为负离子 ESI；如需正离子 [M+Na]⁺/[M+NH4]⁺ 数据，需自测或查 NIST/mzCloud。
2. **Rg3 的 20(S)/20(R) 差向异构体**在 MassBank 中带同一骨架 InChIKey（`RWXIFXNRCLMQCD-UHFFFAOYSA-N`，无立体层），靠记录标题 `(S-FORM)`/`(R-FORM)` 区分；二者 MS2 主要碎片一致，需靠**色谱保留时间**分离，不能仅凭 MS 区分。
3. **不适合 GC-MS/EI**：人参皂苷挥发性低、热不稳定，MassBank 覆盖为 ESI 软电离；若用 GC-MS 须先衍生化。
4. 强度为 MassBank 归一化相对强度（基峰 = 999，本表按 0–100% 换算）；绝对强度见 CSV 的 `intensity` 列。
