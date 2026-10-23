# 种植电子书库 · 全文索引（INDEX）

> 共 **48 册**，合法开放获取（CC BY / OA）。水稻 **28 册**。
> **全文文本** `text/<分区>/<书名>.txt`；**目录** `toc/<分区>/<书名>.md`；元数据 `catalog.json`。

## 一、如何使用（给种植专家）

```bash
python3 references/books/tools/search_books.py "nitrogen" --context 1
python3 references/books/tools/search_books.py "rice blast" --books        # 哪本书讲得最多
python3 references/books/tools/search_books.py "transplanting" --book rice  # 限定水稻分区
python3 references/books/tools/read_page.py Rice_Almanac 120               # 按页读原文
```
- 命中 `书|页码|原文` 后读 `toc/` 定位章节、`text/` 页码附近引用；引用注明 作者/编者、书名、出版社、年份、页码。

## 二、主题标签索引

- **IPM**：Integrated Pest Management in Horticulture（2025）
- **产量差**：Closing Rice Yield Gaps in Asia（2023）
- **作物改良**：Advances in Crop Molecular Breeding and Genetics（2025）
- **保护性耕作**：Conservation Agricultural Practices for Improving Crop Production and Quality（2025）
- **养分管理**：Nutrient Management in Rainfed Lowland Rice in the Lao PDR（2001）；Crop Nutrient Requirements and Advanced Fertilizer Management Strategies（2024）
- **农艺性状**：Molecular Research in Rice: Agronomically Important Traits 2.0（2022）
- **分子育种**：Molecular Research in Rice（2020）；Molecular Research in Rice: Agronomically Important Traits 2.0（2022）；Advances in Crop Molecular Breeding and Genetics（2025）；Molecular Breeding and Germplasm Improvement of Rice（2025）；Abiotic Stress of Crops: Molecular Genetics and Genomic Perspectives（2026）
- **功能食品**：Exploiting the Rice Germplasm for Health-Promoting and Value-Added Foods（2024）
- **发展**：Rice Green Revolution in Sub-Saharan Africa（2023）
- **可持续农业**：Sustainable Crop Production（2019）；Sustainable Crop Production - Recent Advances（2022）；Closing Rice Yield Gaps in Asia（2023）；Soil Fertility and Plant Nutrition for Sustainable Cropping Systems（2026）
- **园艺作物**：Integrated Pest Management in Horticulture（2025）
- **图鉴**：A Practical Field Guide to Weeds of Rice in Asia（2010）；Pictorial Guide for the Identification of Rice Diseases and Pests（2021）
- **土壤健康**：Conservation Agricultural Practices for Improving Crop Production and Quality（2025）；Integrated Soil Management（2025）
- **土壤管理**：Integrated Soil Management（2025）
- **土壤肥力**：Soil Fertility and Plant Nutrition for Sustainable Cropping Systems（2026）；Soil Fertility, Plant Nutrition and Nutrient Management（2026）
- **培训**：Field Water Management and Irrigation for Improved Rice Systems: A Training Guide（2021）
- **基因挖掘**：Gene Mining and Germplasm Innovation for the Important Traits in Rice（2025）
- **基因组**：Genetics in Rice（2020）
- **小麦**：Global Wheat Production（2018）
- **循环利用**：Sustainable Rice Straw Management（2019）
- **循环经济**：Technical Manual: Rice Straw Management towards Circular Economy and Low Emission（2021）
- **技术**：Crop Production Technologies（2012）
- **抗旱**：Abiotic Stress in Plants（2020）；Agricultural Crops Subjected to Drought and Salinity Stress（2025）
- **抗盐**：Abiotic Stress in Plants（2020）；Agricultural Crops Subjected to Drought and Salinity Stress（2025）
- **教材**：Introduction to Crop Production（2023）
- **施肥**：Nutrient Management in Rainfed Lowland Rice in the Lao PDR（2001）；Crop Nutrient Requirements and Advanced Fertilizer Management Strategies（2024）；Soil Fertility, Plant Nutrition and Nutrient Management（2026）
- **旱稻**：Growing Upland Rice in Nigeria (Commercial Crop Production Guide)（2020）
- **机械化**：Technical Manual on Mechanized Rice Seeder Utilization（2021）
- **杂草**：A Practical Field Guide to Weeds of Rice in Asia（2010）
- **栽培**：Global Wheat Production（2018）；Rice Crop - Current Developments（2018）；Recent Advances in Rice Research（2020）
- **栽培指南**：Growing Upland Rice in Nigeria (Commercial Crop Production Guide)（2020）；Rice Cultivation Handbook（2024）
- **植保**：A Practical Field Guide to Weeds of Rice in Asia（2010）；New Insights into Pathogen, Insect Pest, and Weed Control in Field and Greenhouse Cropping Systems（2024）；Biological Pest Control in Agroecosystems（2025）；Integrated Pest Management in Horticulture（2025）；Plant Fungal Diseases and Crop Protection（2025）
- **植物营养**：Crop Nutrient Requirements and Advanced Fertilizer Management Strategies（2024）；Soil Fertility and Plant Nutrition for Sustainable Cropping Systems（2026）；Soil Fertility, Plant Nutrition and Nutrient Management（2026）
- **模型**：Nitrogen Management Studies in Irrigated Rice（1995）
- **模拟**：ORYZA Simulation Modules for Potential and Nitrogen Limited Rice Production（1994）
- **氮素**：ORYZA Simulation Modules for Potential and Nitrogen Limited Rice Production（1994）
- **氮肥**：Nitrogen Management Studies in Irrigated Rice（1995）
- **水分管理**：Water-wise Rice Production（2002）；Field Water Management and Irrigation for Improved Rice Systems: A Training Guide（2021）
- **水稻**：Natural Biological Control of African Rice Gall Midge (IITA Research Guide 37)（1994）；ORYZA Simulation Modules for Potential and Nitrogen Limited Rice Production（1994）；Nitrogen Management Studies in Irrigated Rice（1995）；Nutrient Management in Rainfed Lowland Rice in the Lao PDR（2001）；Water-wise Rice Production（2002）；A Practical Field Guide to Weeds of Rice in Asia（2010）；Rice Almanac, 4th Edition（2013）；Rice - Germplasm, Genetics and Improvement（2014）；Rice Crop - Current Developments（2018）；Sustainable Rice Straw Management（2019）；Genetics in Rice（2020）；Growing Upland Rice in Nigeria (Commercial Crop Production Guide)（2020）；Molecular Research in Rice（2020）；Recent Advances in Rice Research（2020）；Field Water Management and Irrigation for Improved Rice Systems: A Training Guide（2021）；Technical Manual on Mechanized Rice Seeder Utilization（2021）；Pictorial Guide for the Identification of Rice Diseases and Pests（2021）；Rice Improvement: Physiological, Molecular and Breeding Perspectives（2021）；Technical Manual: Rice Straw Management towards Circular Economy and Low Emission（2021）；Stem Borers of Cereal Crops in Africa and Their Management（2021）；Sustainable Insect Pest Management Options for Rice Production in Sub-Saharan Africa（2021）；Molecular Research in Rice: Agronomically Important Traits 2.0（2022）；Closing Rice Yield Gaps in Asia（2023）；Rice Green Revolution in Sub-Saharan Africa（2023）；Exploiting the Rice Germplasm for Health-Promoting and Value-Added Foods（2024）；Rice Cultivation Handbook（2024）；Gene Mining and Germplasm Innovation for the Important Traits in Rice（2025）；Molecular Breeding and Germplasm Improvement of Rice（2025）
- **水肥**：Nitrogen Management Studies in Irrigated Rice（1995）
- **灌溉**：Water-wise Rice Production（2002）；Field Water Management and Irrigation for Improved Rice Systems: A Training Guide（2021）
- **热带农业**：Field Crop Production in Tropical Africa（1991）
- **生产统计**：Rice Almanac, 4th Edition（2013）
- **生物防治**：Natural Biological Control of African Rice Gall Midge (IITA Research Guide 37)（1994）；Biological Pest Control in Agroecosystems（2025）
- **生理**：Rice Improvement: Physiological, Molecular and Breeding Perspectives（2021）
- **生长模型**：ORYZA Simulation Modules for Potential and Nitrogen Limited Rice Production（1994）
- **病害**：Plant Fungal Diseases and Crop Protection（2025）
- **病虫害**：Pictorial Guide for the Identification of Rice Diseases and Pests（2021）
- **病虫草害**：New Insights into Pathogen, Insect Pest, and Weed Control in Field and Greenhouse Cropping Systems（2024）
- **直播**：Technical Manual on Mechanized Rice Seeder Utilization（2021）
- **真菌**：Plant Fungal Diseases and Crop Protection（2025）
- **种质**：Rice Almanac, 4th Edition（2013）；Rice - Germplasm, Genetics and Improvement（2014）；Molecular Research in Rice（2020）；Exploiting the Rice Germplasm for Health-Promoting and Value-Added Foods（2024）；Molecular Breeding and Germplasm Improvement of Rice（2025）
- **种质创新**：Gene Mining and Germplasm Innovation for the Important Traits in Rice（2025）
- **秸秆**：Sustainable Rice Straw Management（2019）；Technical Manual: Rice Straw Management towards Circular Economy and Low Emission（2021）
- **粮食作物**：Field Crop Production in Tropical Africa（1991）；Global Wheat Production（2018）；Advances in Cereal Crops Breeding（2021）
- **综合**：Rice Almanac, 4th Edition（2013）；Rice Crop - Current Developments（2018）；Recent Advances in Rice Research（2020）；New Insights into Pathogen, Insect Pest, and Weed Control in Field and Greenhouse Cropping Systems（2024）；Rice Cultivation Handbook（2024）
- **综合栽培**：Field Crop Production in Tropical Africa（1991）；Crop Production Technologies（2012）；Sustainable Crop Production（2019）；Sustainable Crop Production - Recent Advances（2022）；Introduction to Crop Production（2023）；Conservation Agricultural Practices for Improving Crop Production and Quality（2025）；Integrated Soil Management（2025）
- **绿色防控**：Pictorial Guide for the Identification of Rice Diseases and Pests（2021）；Sustainable Insect Pest Management Options for Rice Production in Sub-Saharan Africa（2021）；Biological Pest Control in Agroecosystems（2025）
- **肥水**：Sustainable Crop Production（2019）
- **育种**：Advances in Cereal Crops Breeding（2021）；Rice Improvement: Physiological, Molecular and Breeding Perspectives（2021）
- **节水**：Water-wise Rice Production（2002）
- **虫害**：Natural Biological Control of African Rice Gall Midge (IITA Research Guide 37)（1994）；Stem Borers of Cereal Crops in Africa and Their Management（2021）；Sustainable Insect Pest Management Options for Rice Production in Sub-Saharan Africa（2021）
- **螟虫**：Stem Borers of Cereal Crops in Africa and Their Management（2021）
- **装备**：Technical Manual on Mechanized Rice Seeder Utilization（2021）
- **逆境胁迫**：Abiotic Stress in Plants（2020）；Agricultural Crops Subjected to Drought and Salinity Stress（2025）；Abiotic Stress of Crops: Molecular Genetics and Genomic Perspectives（2026）
- **遗传育种**：Rice - Germplasm, Genetics and Improvement（2014）；Genetics in Rice（2020）；Advances in Crop Molecular Breeding and Genetics（2025）
- **雨养**：Nutrient Management in Rainfed Lowland Rice in the Lao PDR（2001）
- **非洲**：Rice Green Revolution in Sub-Saharan Africa（2023）

## 水稻专题（Rice）

| 书名 | 年 | 页 | 全文 | 目录 | 来源 |
|---|---|---|---|---|---|
| Gene Mining and Germplasm Innovation for the Important Traits in Rice | 2025 | 196 | `text/rice/Gene_Mining_and_Germplasm_Innovation_Rice_2025.txt` | `toc/rice/Gene_Mining_and_Germplasm_Innovation_Rice_2025.md` | https://www.mdpi.com/books/reprint/10932 |
| Molecular Breeding and Germplasm Improvement of Rice | 2025 | 190 | `text/rice/Molecular_Breeding_and_Germplasm_Improvement_of_Rice_2025.txt` | `toc/rice/Molecular_Breeding_and_Germplasm_Improvement_of_Rice_2025.md` | https://doi.org/10.3390/books978-3-7258-3009-1 |
| Exploiting the Rice Germplasm for Health-Promoting and Value-Added Foods | 2024 | 198 | `text/rice/Exploiting_the_Rice_Germplasm_Health_Promoting_Foods_2024.txt` | `toc/rice/Exploiting_the_Rice_Germplasm_Health_Promoting_Foods_2024.md` | https://www.mdpi.com/books/reprint/10118 |
| Rice Cultivation Handbook | 2024 | 36 | `text/rice/Rice_Cultivation_Handbook_2024.txt` | `toc/rice/Rice_Cultivation_Handbook_2024.md` | https://cgspace.cgiar.org/items/e76a7d69-0b2e-4b92-96c3-adc21721f654 |
| Closing Rice Yield Gaps in Asia | 2023 | 282 | `text/rice/Closing_Rice_Yield_Gaps_in_Asia_2023.txt` | `toc/rice/Closing_Rice_Yield_Gaps_in_Asia_2023.md` | https://doi.org/10.1007/978-3-031-37947-5 |
| Rice Green Revolution in Sub-Saharan Africa | 2023 | 312 | `text/rice/Rice_Green_Revolution_in_Sub_Saharan_Africa_2023.txt` | `toc/rice/Rice_Green_Revolution_in_Sub_Saharan_Africa_2023.md` | https://doi.org/10.1007/978-981-19-8046-6 |
| Molecular Research in Rice: Agronomically Important Traits 2.0 | 2022 | 184 | `text/rice/Molecular_Research_in_Rice_Agronomically_Important_Traits_2_0_2022.txt` | `toc/rice/Molecular_Research_in_Rice_Agronomically_Important_Traits_2_0_2022.md` | https://www.mdpi.com/books/reprint/6479 |
| Field Water Management and Irrigation for Improved Rice Systems: A Training Guide | 2021 | 49 | `text/rice/Field_Water_Management_and_Irrigation_Rice_Training_Guide.txt` | `toc/rice/Field_Water_Management_and_Irrigation_Rice_Training_Guide.md` | https://cgspace.cgiar.org/ |
| Technical Manual on Mechanized Rice Seeder Utilization | 2021 | 78 | `text/rice/Mechanized_Rice_Seeder_Technical_Manual.txt` | `toc/rice/Mechanized_Rice_Seeder_Technical_Manual.md` | https://cgspace.cgiar.org/ |
| Pictorial Guide for the Identification of Rice Diseases and Pests | 2021 | 45 | `text/rice/Pictorial_Guide_Rice_Diseases_and_Pests.txt` | `toc/rice/Pictorial_Guide_Rice_Diseases_and_Pests.md` | https://cgspace.cgiar.org/ |
| Rice Improvement: Physiological, Molecular and Breeding Perspectives | 2021 | 507 | `text/rice/Rice_Improvement_2021.txt` | `toc/rice/Rice_Improvement_2021.md` | https://doi.org/10.1007/978-3-030-66530-2 |
| Technical Manual: Rice Straw Management towards Circular Economy and Low Emission | 2021 | 78 | `text/rice/Rice_Straw_Management_Technical_Manual.txt` | `toc/rice/Rice_Straw_Management_Technical_Manual.md` | https://cgspace.cgiar.org/ |
| Stem Borers of Cereal Crops in Africa and Their Management | 2021 | 11 | `text/rice/Stem_Borers_of_Cereal_Crops_in_Africa.txt` | `toc/rice/Stem_Borers_of_Cereal_Crops_in_Africa.md` | https://www.intechopen.com/ |
| Sustainable Insect Pest Management Options for Rice Production in Sub-Saharan Africa | 2021 | 38 | `text/rice/Sustainable_Insect_Pest_Management_Rice_SubSaharan_Africa.txt` | `toc/rice/Sustainable_Insect_Pest_Management_Rice_SubSaharan_Africa.md` | https://cgspace.cgiar.org/ |
| Genetics in Rice | 2020 | 190 | `text/rice/Genetics_in_Rice_2020.txt` | `toc/rice/Genetics_in_Rice_2020.md` | https://www.mdpi.com/books/reprint/2807 |
| Growing Upland Rice in Nigeria (Commercial Crop Production Guide) | 2020 | 7 | `text/rice/Growing_Upland_Rice_in_Nigeria.txt` | `toc/rice/Growing_Upland_Rice_in_Nigeria.md` | https://cgspace.cgiar.org/ |
| Molecular Research in Rice | 2020 | 380 | `text/rice/Molecular_Research_in_Rice_2020.txt` | `toc/rice/Molecular_Research_in_Rice_2020.md` | https://www.mdpi.com/books/reprint/2941 |
| Recent Advances in Rice Research | 2020 | 260 | `text/rice/Recent_Advances_in_Rice_Research_2020.txt` | `toc/rice/Recent_Advances_in_Rice_Research_2020.md` | https://www.intechopen.com/books/9669 |
| Sustainable Rice Straw Management | 2019 | 199 | `text/rice/Sustainable_Rice_Straw_Management_2019.txt` | `toc/rice/Sustainable_Rice_Straw_Management_2019.md` | https://doi.org/10.1007/978-3-030-32373-8 |
| Rice Crop - Current Developments | 2018 | 268 | `text/rice/Rice_Crop_Current_Developments_2018.txt` | `toc/rice/Rice_Crop_Current_Developments_2018.md` | https://www.intechopen.com/books/6366 |
| Rice - Germplasm, Genetics and Improvement | 2014 | 322 | `text/rice/Rice_Germplasm_Genetics_and_Improvement_2014.txt` | `toc/rice/Rice_Germplasm_Genetics_and_Improvement_2014.md` | https://www.intechopen.com/books/3554 |
| Rice Almanac, 4th Edition | 2013 | 296 | `text/rice/Rice_Almanac_4th_Edition_2013.txt` | `toc/rice/Rice_Almanac_4th_Edition_2013.md` | https://archive.org/details/RiceAlmanac |
| A Practical Field Guide to Weeds of Rice in Asia | 2010 | 121 | `text/rice/A_Practical_Field_Guide_to_Weeds_of_Rice_in_Asia_2010.txt` | `toc/rice/A_Practical_Field_Guide_to_Weeds_of_Rice_in_Asia_2010.md` | https://ageconsearch.umn.edu/record/164472 |
| Water-wise Rice Production | 2002 | 353 | `text/rice/Water_wise_Rice_Production_2002.txt` | `toc/rice/Water_wise_Rice_Production_2002.md` | https://ageconsearch.umn.edu/record/281822 |
| Nutrient Management in Rainfed Lowland Rice in the Lao PDR | 2001 | 95 | `text/rice/Nutrient_Management_Rainfed_Lowland_Rice_Lao_PDR_2001.txt` | `toc/rice/Nutrient_Management_Rainfed_Lowland_Rice_Lao_PDR_2001.md` | https://ageconsearch.umn.edu/record/281826 |
| Nitrogen Management Studies in Irrigated Rice | 1995 | 118 | `text/rice/Nitrogen_Management_in_Irrigated_Rice_1995.txt` | `toc/rice/Nitrogen_Management_in_Irrigated_Rice_1995.md` | https://edepot.wur.nl/344761 |
| Natural Biological Control of African Rice Gall Midge (IITA Research Guide 37) | 1994 | 16 | `text/rice/Natural_Biological_Control_African_Rice_Gall_Midge_IITA.txt` | `toc/rice/Natural_Biological_Control_African_Rice_Gall_Midge_IITA.md` | https://cgspace.cgiar.org/ |
| ORYZA Simulation Modules for Potential and Nitrogen Limited Rice Production | 1994 | 222 | `text/rice/ORYZA_Simulation_Modules_Rice_Production_1994.txt` | `toc/rice/ORYZA_Simulation_Modules_Rice_Production_1994.md` | https://edepot.wur.nl/297741 |

## 其他作物 / 综合农学（Crops & General）

| 书名 | 年 | 页 | 全文 | 目录 | 来源 |
|---|---|---|---|---|---|
| Abiotic Stress of Crops: Molecular Genetics and Genomic Perspectives | 2026 | 256 | `text/crops/Abiotic_Stress_of_Crops_2026.txt` | `toc/crops/Abiotic_Stress_of_Crops_2026.md` | https://doi.org/10.3390/books978-3-7258-6813-1 |
| Soil Fertility and Plant Nutrition for Sustainable Cropping Systems | 2026 | 212 | `text/crops/Soil_Fertility_Plant_Nutrition_Sustainable_Cropping_2026.txt` | `toc/crops/Soil_Fertility_Plant_Nutrition_Sustainable_Cropping_2026.md` | https://www.mdpi.com/books/reprint/12848 |
| Soil Fertility, Plant Nutrition and Nutrient Management | 2026 | 192 | `text/crops/Soil_Fertility_Plant_Nutrition_and_Nutrient_Management_2026.txt` | `toc/crops/Soil_Fertility_Plant_Nutrition_and_Nutrient_Management_2026.md` | https://doi.org/10.3390/books978-3-7258-8644-9 |
| Advances in Crop Molecular Breeding and Genetics | 2025 | 342 | `text/crops/Advances_in_Crop_Molecular_Breeding_and_Genetics_2025.txt` | `toc/crops/Advances_in_Crop_Molecular_Breeding_and_Genetics_2025.md` | https://www.mdpi.com/books/reprint/10478 |
| Agricultural Crops Subjected to Drought and Salinity Stress | 2025 | 202 | `text/crops/Agricultural_Crops_Subjected_to_Drought_and_Salinity_Stress_2025.txt` | `toc/crops/Agricultural_Crops_Subjected_to_Drought_and_Salinity_Stress_2025.md` | https://www.mdpi.com/books/reprint/11204 |
| Biological Pest Control in Agroecosystems | 2025 | 142 | `text/crops/Biological_Pest_Control_in_Agroecosystems_2025.txt` | `toc/crops/Biological_Pest_Control_in_Agroecosystems_2025.md` | https://www.mdpi.com/books/reprint/11248 |
| Conservation Agricultural Practices for Improving Crop Production and Quality | 2025 | 270 | `text/crops/Conservation_Agricultural_Practices_Improving_Crop_Production_2025.txt` | `toc/crops/Conservation_Agricultural_Practices_Improving_Crop_Production_2025.md` | https://www.mdpi.com/books/reprint/10710 |
| Integrated Pest Management in Horticulture | 2025 | 142 | `text/crops/Integrated_Pest_Management_in_Horticulture_2025.txt` | `toc/crops/Integrated_Pest_Management_in_Horticulture_2025.md` | https://doi.org/10.3390/books978-3-7258-3710-6 |
| Integrated Soil Management | 2025 | 268 | `text/crops/Integrated_Soil_Management_2025.txt` | `toc/crops/Integrated_Soil_Management_2025.md` | https://www.mdpi.com/books/reprint/11236 |
| Plant Fungal Diseases and Crop Protection | 2025 | 240 | `text/crops/Plant_Fungal_Diseases_and_Crop_Protection_2025.txt` | `toc/crops/Plant_Fungal_Diseases_and_Crop_Protection_2025.md` | https://www.mdpi.com/books/reprint/11024 |
| Crop Nutrient Requirements and Advanced Fertilizer Management Strategies | 2024 | 342 | `text/crops/Crop_Nutrient_Requirements_Advanced_Fertilizer_Management_2024.txt` | `toc/crops/Crop_Nutrient_Requirements_Advanced_Fertilizer_Management_2024.md` | https://www.mdpi.com/books/reprint/9034 |
| New Insights into Pathogen, Insect Pest, and Weed Control in Field and Greenhouse Cropping Systems | 2024 | 214 | `text/crops/New_Insights_into_Pathogen_Insect_Pest_and_Weed_Control_2024.txt` | `toc/crops/New_Insights_into_Pathogen_Insect_Pest_and_Weed_Control_2024.md` | https://www.mdpi.com/books/reprint/9196 |
| Introduction to Crop Production | 2023 | 66 | `text/crops/Introduction_to_Crop_Production_2023.txt` | `toc/crops/Introduction_to_Crop_Production_2023.md` | https://zenodo.org/record/8400944 |
| Sustainable Crop Production - Recent Advances | 2022 | 210 | `text/crops/Sustainable_Crop_Production_Recent_Advances_2022.txt` | `toc/crops/Sustainable_Crop_Production_Recent_Advances_2022.md` | https://www.intechopen.com/books/11357 |
| Advances in Cereal Crops Breeding | 2021 | 198 | `text/crops/Advances_in_Cereal_Crops_Breeding_2021.txt` | `toc/crops/Advances_in_Cereal_Crops_Breeding_2021.md` | https://doi.org/10.3390/books978-3-0365-2651-5 |
| Abiotic Stress in Plants | 2020 | 496 | `text/crops/Abiotic_Stress_in_Plants_2020.txt` | `toc/crops/Abiotic_Stress_in_Plants_2020.md` | https://www.intechopen.com/books/10363 |
| Sustainable Crop Production | 2019 | 354 | `text/crops/Sustainable_Crop_Production_2019.txt` | `toc/crops/Sustainable_Crop_Production_2019.md` | https://www.intechopen.com/books/9345 |
| Global Wheat Production | 2018 | 254 | `text/crops/Global_Wheat_Production_2018.txt` | `toc/crops/Global_Wheat_Production_2018.md` | https://www.intechopen.com/books/6776 |
| Crop Production Technologies | 2012 | 290 | `text/crops/Crop_Production_Technologies_2012.txt` | `toc/crops/Crop_Production_Technologies_2012.md` | https://www.intechopen.com/books/597 |
| Field Crop Production in Tropical Africa | 1991 | 477 | `text/crops/Field_Crop_Production_in_Tropical_Africa_1991.txt` | `toc/crops/Field_Crop_Production_in_Tropical_Africa_1991.md` | https://cgspace.cgiar.org/ |

---
*由种植专家维护；新增电子书后运行 `python3 tools/make_index.py` 重建。*
