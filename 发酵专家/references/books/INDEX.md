# 发酵电子书库 · 全文索引（INDEX）

> 共 **34 册**，全部为合法开放获取（CC BY / 公共领域）。
> PDF 存于各分区目录；**全文文本**在 `text/<分区>/<书名>.txt`；**目录**在 `toc/<分区>/<书名>.md`；结构化元数据 `catalog.json`。

## 一、如何使用（给发酵专家）

```bash
# 全文检索（多词 AND，返回 书|页码|原文）
python3 references/books/tools/search_books.py "Monod" --context 1
python3 references/books/tools/search_books.py "kLa" --word --max 20
# 各书命中统计（找哪本书讲得最多）
python3 references/books/tools/search_books.py "solid-state fermentation" --books
# 仅在某本书内检索
python3 references/books/tools/search_books.py "downstream" --book Distillation
# 命中页码后，按页读取原文
python3 references/books/tools/read_page.py Jorgensen 120
python3 references/books/tools/read_page.py Membrane_Distillation 45 50
```
- 检索到要点后，读取 `toc/<分区>/<书名>.md` 定位章节，再读取对应 `text/...txt` 的页码附近原文引用。
- 引用时注明：作者/编者、书名、出版社、年份、许可与页码。

## 二、主题标签索引

- **PAT**：Bioprocess Monitoring and Control（2020）
- **下游分离**：Distillation - Innovative Applications and Modeling（2017）；Membrane Distillation（2017）；Distillation Processes - From Solar and Membrane Distillation（2021）；Membrane Distillation Process（2021）；Application of Membrane Materials in Bioseparation and Downstream Processing（2026）
- **乳酸菌**：Recent Advances in Lactic Acid Bacteria and Metabolite for Food Quality（2026）
- **代谢**：Bacterial Fermentations (Barker)（1956）
- **代谢工程**：Recent Advances in Biocatalysis and Metabolic Engineering for Biomanufacturing（2019）
- **传统酿造**：The Chemistry of Sake-Brewing (Atkinson)（1881）；The Curiosities of Ale & Beer (Bickerdyke)（1889）；The Principles and Practice of Brewing (Sykes)（1907）；Brewing Technology（2017）；Brewing and Craft Beer（2019）；Wine Fermentation（2019）；Polyphenolic Compounds in Wine and Beer（2023）
- **动力学建模**：Fermentation Processes（2017）；Modern Technologies and Their Influence in Fermentation Quality（2020）
- **历史经典**：The Chemistry of Sake-Brewing (Atkinson)（1881）；The Curiosities of Ale & Beer (Bickerdyke)（1889）；Micro-organisms and Fermentation (Jorgensen)（1900）；The Principles and Practice of Brewing (Sykes)（1907）；Bacterial Fermentations (Barker)（1956）
- **发酵剂**：Development and Application of Starter Cultures, 2nd Edition（2026）
- **发酵工艺**：Micro-organisms and Fermentation (Jorgensen)（1900）；Fermentation Processes（2017）；New Advances on Fermentation Processes（2019）；Modern Technologies and Their Influence in Fermentation Quality（2020）；Fermentation - Processes, Benefits and Risks（2021）；Advances in Microbial Fermentation Processes（2022）；Fermentation Processes（2025）
- **发酵饲料**：Application of Fermentation Technology in Animal Nutrition（2024）
- **啤酒**：The Curiosities of Ale & Beer (Bickerdyke)（1889）；Brewing Technology（2017）；Brewing and Craft Beer（2019）
- **工业发酵**：Bioprocess Monitoring and Control（2020）；Advances in Industrial and Environmental Microbiology（2021）；Implementation of Digital Technologies on Beverage Fermentation（2022）；Industrial Microbiology in the Production of Organic Compounds（2024）
- **有机化合物**：Industrial Microbiology in the Production of Organic Compounds（2024）
- **清酒**：The Chemistry of Sake-Brewing (Atkinson)（1881）
- **环境微生物**：Advances in Industrial and Environmental Microbiology（2021）
- **生物乙醇**：Bioethanol Technologies（2020）
- **生物催化**：Enzyme Inhibitors and Activators（2017）；Recent Advances in Biocatalysis and Metabolic Engineering for Biomanufacturing（2019）
- **生物制造**：New Advances on Fermentation Processes（2019）；Recent Advances in Biocatalysis and Metabolic Engineering for Biomanufacturing（2019）；Bioethanol Technologies（2020）；Advances in Microbial Fermentation Processes（2022）；Application of Fermentation Technology in Animal Nutrition（2024）；Industrial Microbiology in the Production of Organic Compounds（2024）
- **益生菌**：Probiotics and Prebiotics in Human Nutrition and Health（2016）；Prebiotics and Probiotics（2018）；Probiotics and Prebiotics in Pediatrics（2019）
- **膜分离**：Membrane Distillation（2017）；Distillation Processes - From Solar and Membrane Distillation（2021）；Membrane Distillation Process（2021）；Application of Membrane Materials in Bioseparation and Downstream Processing（2026）
- **菌种**：Micro-organisms and Fermentation (Jorgensen)（1900）；Bacterial Fermentations (Barker)（1956）；Fermentation Processes（2017）；New Insights into Food Fermentation（2022）；Recent Advances in Lactic Acid Bacteria and Metabolite for Food Quality（2026）；Development and Application of Starter Cultures, 2nd Edition（2026）
- **营养**：Probiotics and Prebiotics in Human Nutrition and Health（2016）；Prebiotics and Probiotics（2018）；Probiotics and Prebiotics in Pediatrics（2019）
- **葡萄酒**：Wine Fermentation（2019）
- **蒸馏**：Distillation - Innovative Applications and Modeling（2017）；Distillation Processes - From Solar and Membrane Distillation（2021）
- **过程控制**：Bioprocess Monitoring and Control（2020）；Implementation of Digital Technologies on Beverage Fermentation（2022）
- **酶工程**：Enzyme Inhibitors and Activators（2017）
- **风味化学**：Polyphenolic Compounds in Wine and Beer（2023）
- **食品发酵**：New Insights into Food Fermentation（2022）；Recent Advances in Lactic Acid Bacteria and Metabolite for Food Quality（2026）；Development and Application of Starter Cultures, 2nd Edition（2026）
- **食品安全**：Fermentation - Processes, Benefits and Risks（2021）
- **饮料**：Implementation of Digital Technologies on Beverage Fermentation（2022）

## IntechOpen（CC BY）

| 书名 | 年 | 页 | 许可 | 全文 | 目录 | 来源 |
|---|---|---|---|---|---|---|
| Distillation Processes - From Solar and Membrane Distillation | 2021 | 228 | CC BY 3.0 | `text/intechopen/Distillation_Processes_2021.txt` | `toc/intechopen/Distillation_Processes_2021.md` | https://www.intechopen.com/books/10995 |
| Fermentation - Processes, Benefits and Risks | 2021 | 200 | CC BY 3.0 | `text/intechopen/Fermentation_Processes_Benefits_and_Risks_2021.txt` | `toc/intechopen/Fermentation_Processes_Benefits_and_Risks_2021.md` | https://www.intechopen.com/books/9709 |
| Bioethanol Technologies | 2020 | 158 | CC BY 3.0 | `text/intechopen/Bioethanol_Technologies_2020.txt` | `toc/intechopen/Bioethanol_Technologies_2020.md` | https://www.intechopen.com/books/10379 |
| New Advances on Fermentation Processes | 2019 | 242 | CC BY 3.0 | `text/intechopen/New_Advances_on_Fermentation_Processes_2019.txt` | `toc/intechopen/New_Advances_on_Fermentation_Processes_2019.md` | https://www.intechopen.com/books/8244 |
| Brewing Technology | 2017 | 214 | CC BY 3.0 | `text/intechopen/Brewing_Technology_2017.txt` | `toc/intechopen/Brewing_Technology_2017.md` | https://www.intechopen.com/books/5967 |
| Distillation - Innovative Applications and Modeling | 2017 | 248 | CC BY 3.0 | `text/intechopen/Distillation_Innovative_Applications_and_Modeling_2017.txt` | `toc/intechopen/Distillation_Innovative_Applications_and_Modeling_2017.md` | https://www.intechopen.com/books/5452 |
| Enzyme Inhibitors and Activators | 2017 | 270 | CC BY 3.0 | `text/intechopen/Enzyme_Inhibitors_and_Activators_2017.txt` | `toc/intechopen/Enzyme_Inhibitors_and_Activators_2017.md` | https://www.intechopen.com/books/5540 |
| Fermentation Processes | 2017 | 314 | CC BY 3.0 | `text/intechopen/Fermentation_Processes_2017.txt` | `toc/intechopen/Fermentation_Processes_2017.md` | https://www.intechopen.com/books/5305 |
| Probiotics and Prebiotics in Human Nutrition and Health | 2016 | 396 | CC BY 3.0 | `text/intechopen/Probiotics_and_Prebiotics_in_Human_Nutrition_and_Health_2016.txt` | `toc/intechopen/Probiotics_and_Prebiotics_in_Human_Nutrition_and_Health_2016.md` | https://www.intechopen.com/books/5193 |

## MDPI Books（CC BY）

| 书名 | 年 | 页 | 许可 | 全文 | 目录 | 来源 |
|---|---|---|---|---|---|---|
| Application of Membrane Materials in Bioseparation and Downstream Processing | 2026 | 144 | CC BY | `text/mdpi/Membrane_Materials_Bioseparation_Downstream_2026.txt` | `toc/mdpi/Membrane_Materials_Bioseparation_Downstream_2026.md` | https://doi.org/10.3390/books978-3-7258-6773-8 |
| Recent Advances in Lactic Acid Bacteria and Metabolite for Food Quality | 2026 | 180 | CC BY | `text/mdpi/Recent_Advances_Lactic_Acid_Bacteria_2026.txt` | `toc/mdpi/Recent_Advances_Lactic_Acid_Bacteria_2026.md` | https://doi.org/10.3390/books978-3-7258-7521-4 |
| Development and Application of Starter Cultures, 2nd Edition | 2026 | 162 | CC BY | `text/mdpi/Starter_Cultures_2nd_Edition_2026.txt` | `toc/mdpi/Starter_Cultures_2nd_Edition_2026.md` | https://doi.org/10.3390/books978-3-7258-8454-4 |
| Fermentation Processes | 2025 | 168 | CC BY | `text/mdpi/Fermentation_Processes_2025.txt` | `toc/mdpi/Fermentation_Processes_2025.md` | https://doi.org/10.3390/books978-3-7258-5112-6 |
| Application of Fermentation Technology in Animal Nutrition | 2024 | 182 | CC BY | `text/mdpi/Fermentation_Technology_in_Animal_Nutrition_2024.txt` | `toc/mdpi/Fermentation_Technology_in_Animal_Nutrition_2024.md` | https://doi.org/10.3390/books978-3-7258-2770-1 |
| Polyphenolic Compounds in Wine and Beer | 2023 | 218 | CC BY | `text/mdpi/Polyphenolic_Compounds_in_Wine_and_Beer_2023.txt` | `toc/mdpi/Polyphenolic_Compounds_in_Wine_and_Beer_2023.md` | https://www.mdpi.com/books/pdfview/book/6554 |
| Advances in Microbial Fermentation Processes | 2022 | 222 | CC BY | `text/mdpi/Advances_in_Microbial_Fermentation_Processes_2022.txt` | `toc/mdpi/Advances_in_Microbial_Fermentation_Processes_2022.md` | https://doi.org/10.3390/books978-3-0365-4010-8 |
| Implementation of Digital Technologies on Beverage Fermentation | 2022 | 222 | CC BY | `text/mdpi/Digital_Technologies_on_Beverage_Fermentation_2022.txt` | `toc/mdpi/Digital_Technologies_on_Beverage_Fermentation_2022.md` | https://doi.org/10.3390/books978-3-0365-3656-9 |
| New Insights into Food Fermentation | 2022 | 228 | CC BY | `text/mdpi/New_Insights_into_Food_Fermentation_2022.txt` | `toc/mdpi/New_Insights_into_Food_Fermentation_2022.md` | https://doi.org/10.3390/books978-3-0365-3919-5 |
| Advances in Industrial and Environmental Microbiology | 2021 | 94 | CC BY | `text/mdpi/Advances_in_Industrial_and_Environmental_Microbiology_2021.txt` | `toc/mdpi/Advances_in_Industrial_and_Environmental_Microbiology_2021.md` | https://www.mdpi.com/books/pdfview/book/4600 |
| Membrane Distillation Process | 2021 | 191 | CC BY | `text/mdpi/Membrane_Distillation_Process_2021.txt` | `toc/mdpi/Membrane_Distillation_Process_2021.md` | https://doi.org/10.3390/books978-3-0365-1211-2 |
| Bioprocess Monitoring and Control | 2020 | 236 | CC BY | `text/mdpi/Bioprocess_Monitoring_and_Control_2020.txt` | `toc/mdpi/Bioprocess_Monitoring_and_Control_2020.md` | https://doi.org/10.3390/books978-3-03936-933-1 |
| Modern Technologies and Their Influence in Fermentation Quality | 2020 | 238 | CC BY | `text/mdpi/Modern_Technologies_Fermentation_Quality_2020.txt` | `toc/mdpi/Modern_Technologies_Fermentation_Quality_2020.md` | https://www.mdpi.com/books/pdfview/book/2285 |
| Brewing and Craft Beer | 2019 | 142 | CC BY | `text/mdpi/Brewing_and_Craft_Beer_2019.txt` | `toc/mdpi/Brewing_and_Craft_Beer_2019.md` | https://doi.org/10.3390/books978-3-03921-490-7 |
| Probiotics and Prebiotics in Pediatrics | 2019 | 260 | CC BY | `text/mdpi/Probiotics_and_Prebiotics_in_Pediatrics_2019.txt` | `toc/mdpi/Probiotics_and_Prebiotics_in_Pediatrics_2019.md` | https://www.mdpi.com/books/pdfview/book/1290 |
| Recent Advances in Biocatalysis and Metabolic Engineering for Biomanufacturing | 2019 | 280 | CC BY | `text/mdpi/Recent_Advances_Biocatalysis_and_Metabolic_Engineering_2019.txt` | `toc/mdpi/Recent_Advances_Biocatalysis_and_Metabolic_Engineering_2019.md` | https://www.mdpi.com/books/pdfview/book/1569 |
| Wine Fermentation | 2019 | 178 | CC BY | `text/mdpi/Wine_Fermentation_2019.txt` | `toc/mdpi/Wine_Fermentation_2019.md` | https://www.mdpi.com/books/pdfview/book/1190 |
| Prebiotics and Probiotics | 2018 | 488 | CC BY | `text/mdpi/Prebiotics_and_Probiotics_2018.txt` | `toc/mdpi/Prebiotics_and_Probiotics_2018.md` | https://doi.org/10.3390/books978-3-03897-169-6 |
| Membrane Distillation | 2017 | 134 | CC BY | `text/mdpi/Membrane_Distillation_2017.txt` | `toc/mdpi/Membrane_Distillation_2017.md` | https://www.mdpi.com/books/pdfview/book/335 |

## 公共领域 / 历史经典

| 书名 | 年 | 页 | 许可 | 全文 | 目录 | 来源 |
|---|---|---|---|---|---|---|
| Bacterial Fermentations (Barker) | 1956 | 110 | Public Domain | `text/public_domain/Bacterial_Fermentations_1956.txt` | `toc/public_domain/Bacterial_Fermentations_1956.md` | https://archive.org/details/bacterialferment00bark |
| The Principles and Practice of Brewing (Sykes) | 1907 | 616 | Public Domain | `text/public_domain/The_Principles_and_Practice_of_Brewing_1907.txt` | `toc/public_domain/The_Principles_and_Practice_of_Brewing_1907.md` | https://archive.org/details/principlespracti00syke |
| Micro-organisms and Fermentation (Jorgensen) | 1900 | 344 | Public Domain | `text/public_domain/Micro-organisms_and_Fermentation_1900.txt` | `toc/public_domain/Micro-organisms_and_Fermentation_1900.md` | https://archive.org/details/microorganismsfe00jrrich |
| The Curiosities of Ale & Beer (Bickerdyke) | 1889 | 480 | Public Domain | `text/public_domain/Curiosities_of_Ale_and_Beer_1889.txt` | `toc/public_domain/Curiosities_of_Ale_and_Beer_1889.md` | https://archive.org/details/curiositiesofale00bick |
| The Chemistry of Sake-Brewing (Atkinson) | 1881 | 144 | Public Domain | `text/public_domain/The_Chemistry_of_Sake-Brewing_1881.txt` | `toc/public_domain/The_Chemistry_of_Sake-Brewing_1881.md` | https://archive.org/details/chemistryofsakeb00atki |

## 其他开放获取

| 书名 | 年 | 页 | 许可 | 全文 | 目录 | 来源 |
|---|---|---|---|---|---|---|
| Industrial Microbiology in the Production of Organic Compounds | 2024 | 64 | Open Access | `text/other/Industrial_Microbiology_in_the_Production_of_Organic_Compounds_2024.txt` | `toc/other/Industrial_Microbiology_in_the_Production_of_Organic_Compounds_2024.md` | https://www.bspublications.com/ |

---
*由发酵专家维护；新增电子书请运行 `python3 tools/make_index.py` 重建索引并登记。*
