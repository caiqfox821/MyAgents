# 金线莲（Anoectochilus roxburghii）成分 质谱参考谱库

> 生成日期：2026-10-23 ｜ 来源：MassBank + GNPS/MoNA 镜像（多库合并）

## 一、概况

| 指标 | 数值 |
|---|---|
| 谱图总数 | **2387** |
| 化合物数（去重） | **35** |
| 正离子谱 | 1266 |
| 负离子谱 | 1121 |
| MS² 谱（ms_type=MS2） | 2220 |
| 非 MS² 谱（MS1 等） | 167 |
| 来源 MassBank | 1570 |
| 来源 MoNA | 485 |
| 来源 GNPS | 332 |
| 目标清单化合物 | 37 |
| 目标清单已收录 | 34 |
| 目标清单未收录 | 3 |

## 二、数据来源与版本

| 来源 | 文件/接口 | 说明 |
|---|---|---|
| MassBank | `https://rdfportal.org/primary/sparql`（GRAPH massbank） | 主库（RDF Portal SPARQL，权威参考谱）；本库 1570 条 |
| GNPS-LIBRARY.mgf / GNPS-NIH-NATURALPRODUCTSLIBRARY.mgf | `https://external.gnps2.org/gnpslibrary/`（MGF 镜像） | GNPS 社区库；命中本库目标 332 条 |
| MONA.mgf | 同上 | MoNA（MassBank of North America）镜像；命中本库目标 485 条 |
| MASSBANK.mgf | 同上 | MassBank 的 GNPS 镜像，**已跳过**（与 MassBank RDF 主库重复） |
| `user/*.msp`、`user/*.mgf` | 本地（实验自测） | 若存在则并入，source=`User(实验)`；当前 0 条 |

> 下载日期：2026-10-23。检索脚本见 `scripts/`。

## 三、收录化合物一览

按谱图条数排序（详见 `compounds.csv`）：

| 化合物 | 目标名 | InChIKey | 分子式 | 单同位素质量 | 谱图数 | 来源 |
|---|---|---|---|---|---|---|
| Quercetin | Quercetin | REFJWTPEDVJJIY-UHFFFAOYSA-N | C15H10O7 | 302.04265 | 183 | GNPS|MassBank|MoNA |
| Kaempferol | Kaempferol | IYRMWMYZSQPJKC-UHFFFAOYSA-N | C15H10O6 | 286.04774 | 158 | GNPS|MassBank|MoNA |
| Nicotiflorin | Nicotiflorin | RTATXGUCZHCSNG-QHWHWDPRSA-N | C27H30O15 | 594.15847 | 133 | GNPS|MassBank|MoNA |
| Adenosine | Adenosine | OIRDTQYFTABQOQ-KQYNXXCUSA-N | C10H13N5O4 | 267.09675 | 123 | GNPS|MassBank|MoNA |
| Rutin | Rutin | IKGXIBQEEMLURG-NVPNHPEKSA-N | C27H30O16 | 610.15338 | 118 | GNPS|MassBank|MoNA |
| Ferulic acid | Ferulic acid | KSEBMYQBYZTDHS-HWKANZROSA-N | C10H10O4 | 194.05791 | 117 | GNPS|MassBank|MoNA |
| Quercitrin | Quercitrin | OXGUCUVFOIWWQJ-HQBVPOQASA-N | C21H20O11 | 448.10056 | 98 | GNPS|MassBank|MoNA |
| Hyperoside | Hyperoside | OVSQVDMCBVZWGM-DTGCRPNFSA-N | C21H20O12 | 464.09548 | 97 | GNPS|MassBank|MoNA |
| Luteolin | Luteolin | IQPNAANSBPBGFQ-UHFFFAOYSA-N | C15H10O6 | 286.04774 | 97 | GNPS|MassBank|MoNA |
| Apigenin | Apigenin | KZNIFHPLKGYRTM-UHFFFAOYSA-N | C15H10O5 | 270.05282 | 95 | GNPS|MassBank|MoNA |
| Chlorogenic acid | Chlorogenic acid | CWVRJTMFETXNAD-JUHZACGLSA-N | C16H18O9 | 354.09508 | 93 | GNPS|MassBank|MoNA |
| L-Arginine | L-Arginine | ODKSFYDXXFIFQN-BYPYZUCNSA-N | C6H14N4O2 | 174.11168 | 89 | GNPS|MassBank|MoNA |
| Astragalin | Astragalin | JPUKWEQWGBDDQB-QSOFNFLRSA-N | C21H20O11 | 448.10056 | 81 | GNPS|MassBank |
| Citric acid | Citric acid | KRKNYBCHXYNGOX-UHFFFAOYSA-N | C6H8O7 | 192.027 | 75 | GNPS|MassBank|MoNA |
| p-Coumaric acid | p-Coumaric acid | NGSWKAQJJWESNS-ZZXKWVIFSA-N | C9H8O3 | 164.04734 | 75 | GNPS|MassBank|MoNA |
| Isorhamnetin | Isorhamnetin | IZQSVPBOUDKVDZ-UHFFFAOYSA-N | C16H12O7 | 316.0583 | 71 | GNPS|MassBank |
| Salicylic acid | Salicylic acid | YGSDEFSMJLZEOE-UHFFFAOYSA-N | C7H6O3 | 138.03169 | 67 | GNPS|MassBank|MoNA |
| 4-Hydroxybenzoic acid | 4-Hydroxybenzoic acid | FJKROLUGYXJWQN-UHFFFAOYSA-N | C7H6O3 | 138.03169 | 62 | GNPS|MassBank|MoNA |
| Narcissin | Narcissin | UIDGLYUNOUKLBM-GEBJFKNCSA-N | C28H32O16 | 624.16903 | 60 | GNPS|MassBank |
| Gallic acid | Gallic acid | LNTHITQWFMADLM-UHFFFAOYSA-N | C7H6O5 | 170.02152 | 58 | GNPS|MassBank|MoNA |
| Caffeic acid | Caffeic acid | QAIPRVGONGVQAS-DUXPYHPUSA-N | C9H8O4 | 180.04226 | 56 | GNPS|MassBank|MoNA |
| 4-Aminobutyric acid | 4-Aminobutyric acid | BTCSSZJGUNDROE-UHFFFAOYSA-N | C4H9NO2 | 103.06333 | 50 | GNPS|MassBank|MoNA |
| Isoquercitrin | Isoquercitrin | OVSQVDMCBVZWGM-QSOFNFLRSA-N | C21H20O12 | 464.09548 | 50 | GNPS|MassBank |
| Isorhamnetin-3-O-glucoside | Isorhamnetin-3-O-glucoside | CQLRUIIRRZYHHS-LFXZADKFSA-N | C22H22O12 | 478.11113 | 49 | MassBank |
| Vitexin | Vitexin | SGEWCQFRYRRZDC-VPRICQMDSA-N | C21H20O10 | 432.10565 | 40 | GNPS|MassBank |
| Syringic acid | Syringic acid | JMSVCTWVEWCHDZ-UHFFFAOYSA-N | C9H10O5 | 198.05282 | 38 | GNPS|MassBank|MoNA |
| Succinic acid | Succinic acid | KDYFGRWQOYBRFD-UHFFFAOYSA-N | C4H6O4 | 118.02661 | 35 | GNPS|MassBank|MoNA |
| beta-Sitosterol | beta-Sitosterol | KZJWDPNRJALLNS-VJSFXXLFSA-N | C29H50O | 414.38617 | 26 | MassBank|MoNA |
| Malic acid | Malic acid | BJEPYKJPYRNKOW-REOHCLBHSA-N | C4H6O5 | 134.02152 | 21 | GNPS|MassBank|MoNA |
| Isovitexin | Isovitexin | MYXNWGACZJSMBT-VJXVFPJBSA-N | C21H20O10 | 432.10565 | 19 | GNPS|MassBank |
| Vanillic acid | Vanillic acid | WKOLLVMJNQIZCI-UHFFFAOYSA-N | C8H8O4 | 168.04226 | 16 | GNPS|MassBank|MoNA |
| Protocatechuic acid | Protocatechuic acid | YQUVCSBJEUQKSH-UHFFFAOYSA-N | C7H6O4 | 154.02661 | 14 | GNPS|MassBank |
| Stigmasterol | Stigmasterol | HCXVJBMSMIARIN-PHZDYDNGSA-N | C29H48O | 412.37052 | 12 | GNPS|MassBank |
| 2,5-Dihydroxybenzoic acid | - | WXTMDXOMEHJXQO-UHFFFAOYSA-N | C7H6O4 | 154.02661 | 10 | MassBank |
| Daucosterol | Daucosterol | - | - | - | 1 | GNPS |

## 四、目标清单覆盖情况


## 五、文件清单

| 文件 | 说明 |
|---|---|
| `library.msp` | NIST/MassHunter 兼容主库（每谱一条记录） |
| `library.mgf` | MGF 格式（MS-DIAL / MZmine / GNPS 可直接读） |
| `index.csv` | 谱图索引（来源、ID、化合物、母离子、加合物、碰撞能量等） |
| `compounds.csv` | 库内化合物汇总（去重、谱图数、前体 m/z） |
| `coverage.csv` | 目标清单覆盖表（收录/缺失） |
| `raw/` | 原始数据（MassBank 元数据/峰表、GNPS MGF、目标解析） |
| `scripts/` | 抓取与建库脚本 + `targets.tsv` 目标清单 |
| `user/` | **自测（实验）谱图投放处**：放 `*.mgf` 或 `*.msp` 后重跑即并入 |

## 六、使用说明

**NIST MS Search / MassHunter**：直接打开 `library.msp` 作为用户谱库检索。

**MS-DIAL / MZmine / GNPS**：用 `library.mgf` 建立本地库或做谱库比对。

**自建脚本/编程**：读 `index.csv` + `raw/massbank/peaks.csv` 或直接解析 `library.mgf`。

> 建议：母离子过滤 + 加合物 + 极性 + 碰撞能量一致后再算相似度；MS² 库匹配置信度最高到 Schymanski Level 2。

## 七、如何补充自测（实验）谱图

把鉴定确证的实测 MS² 谱放入本库 `user/` 目录（`*.mgf` 或 NIST `*.msp` 均可），然后重跑：

```bash
cd <本库>/scripts
python3 build_library.py    # 自测谱以 source=User(实验) 并入 library.msp / .mgf / index.csv
python3 make_report.py      # 刷新覆盖率与说明
```
MSP 记录建议含：`Name`、`InChIKey`、`Formula`、`PrecursorMZ`、`Precursor_type`、`Ion_mode`、`Collision_energy`、`Num Peaks` 及峰表；名称与目标清单一致时自动归入该目标（也可写 `MATCHED_TARGET=` 指定）。

## 八、已知局限（务必阅读）

1. **公开库覆盖不全**：目标清单中未能检索到实测 MS² 的化合物见 `coverage.csv` 与《覆盖与缺失清单》。公开免费库（MassBank / GNPS / MoNA）对它们确无记录——**「查不到」不等于「不存在」**，多属需自测、或仅散见于论文的稀有成分类。
2. **同分异构体无法仅凭 MS² 区分**：分子式相同者（立体/位置异构）须靠色谱保留时间、标准品或离子淌度 CCS；本库相关同分异构对见 `notes_extra.md`。
3. **MassBank 的 `ch_exact_mass` 字段不可靠**（部分为平均分子量），本库的质量已改由分子式重新计算（`ExactMass`），原始值保留在 `Comment` 中备查。
4. **前体 m/z**：MassBank 多数记录未给前体值，本库按加合物由分子式推算并在 MSP 中给出 `PrecursorMZ`；如与实际仪器条件不符请以原始 `Comment` 为准。
5. **强度标尺不同**：MassBank 为相对强度(%)；GNPS/MoNA 原始为绝对强度，本库已归一到基峰=100。
6. **无保留时间/CCS**：均为谱库（MS²）参考谱，不含 RT/CCS。
7. 多库合并存在**同化合物多来源重复**（保留各自来源记录，便于交叉验证）。
8. 本库**保留全部**参考谱（含少量低信息量记录，如仅 1–2 个碎片的谱）。可在 `index.csv` 中按 `n_peaks` 列过滤（如 `n_peaks>=5`）后使用，以获得更干净的子库。
9. **含少量非 MS² 记录**：本库 `ms_type=MS2` 共 **2220** 条，另有 **167** 条为一级谱（`ms_type=MS`，多为某些氨基酸/小分子的 LC-ESI-ITFT 谱）；另有极少数来源为 MoNA、加合物字段解析异常（如负离子记录标为 `[M]⁺`）。做 **MS² 库检索前请先按 `index.csv` 的 `ms_type`/`adduct` 列过滤**（`ms_type==MS2`），一级谱对二级匹配无意义。

## 九、补充说明与使用提示

### 金线莲判读要点（质量均按分子式推算，鉴定须以标准品/实测复核）

1. **标志成分——金线莲苷 Kinsenoside（C10H16O8，单同位素 264.0845）**：公开谱库（MassBank / GNPS / MoNA）**无实测 MS²**，是本库最大缺口。常见母离子（按分子式推算）：`[M–H]⁻ 263.0772`、`[M+HCOO]⁻ 309.0822`、`[M+H]⁺ 265.0918`、`[M+Na]⁺ 287.0743`。建议自测（负离子优先）后放入本库 `user/` 目录。
2. **Gastrodin 天麻素（C13H18O7，286.1053）**：`[M–H]⁻ 285.0980`。同为小分子糖苷，可与金线莲苷对照。
3. **黄酮苷的碎裂**：负离子下常先丢糖（Glc 162、Rha 146、Gal 162），留下苷元离子；苷元与糖的连接位置/类型不同则碎片分布不同。**黄酮 O-苷**易水解，**黄酮 C-苷**（牡荆素/异牡荆素）不水解、保留完整糖基。
4. **同分异构体对（须色谱区分）**：
   - 牡荆素 / 异牡荆素 —— C21H20O10，`[M–H]⁻ 431.0984`；
   - 金丝桃苷 / 异槲皮苷 —— C21H20O12，`[M–H]⁻ 463.0882`；
   - 芦丁 `[M–H]⁻ 609.1461`（C27H30O16），与烟花苷/水仙苷（C27H30O15，`[M–H]⁻ 593.15`）易混。
5. **金线莲主要黄酮**：芦丁、异槲皮苷、槲皮苷、金丝桃苷、紫云英苷、烟花苷、水仙苷、牡荆素/异牡荆素，及苷元槲皮素（`[M–H]⁻ 301.0354`）、山奈酚（`[M–H]⁻ 285.0405`）、异鼠李素。酚酸类（绿原酸、咖啡酸、阿魏酸、对香豆酸等）在负离子下响应好。
6. **建议检索策略**：负离子优先（`[M–H]⁻`）；先做酚酸/黄酮的靶向 MRM（用本库对应谱），再用非靶向找金线莲苷等未收录成分；黄酮苷需结合保留时间区分同分异构体。

## 十、参考

- MassBank: Horai et al., *J. Mass Spectrom.* 2010, 45, 703–714. 数据经 RDF Portal（https://rdfportal.org/dataset/massbank）获取。
- GNPS / GNPS2: Wang et al., *Nat. Biotechnol.* 2016, 34, 828–837.
- MoNA (MassBank of North America): https://mona.fiehnlab.ucdavis.edu
