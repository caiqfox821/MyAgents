# 食品加工电子书库 · 全文索引（INDEX）

> 共 **118 册/篇**，均为合法开放获取（MDPI CC BY / FAO 开放获取 / Archive.org 公共领域）。
> PDF 存于 `mdpi/`、`fao/`、`public_domain/`；**全文文本**在 `text/<分区>/<书名>.txt`；**目录**在 `toc/<分区>/<书名>.md`；结构化元数据 `catalog.json`。

## 一、如何使用（给食品加工专家）

```bash
# 全文检索（多词 AND，返回 书|页码|原文）
python3 references/books/tools/search_books.py "spray drying" --context 1
python3 references/books/tools/search_books.py "high pressure processing" --word --max 20
# 各书命中统计（找哪本书讲得最多）
python3 references/books/tools/search_books.py "encapsulation" --books
# 仅在某本书内检索
python3 references/books/tools/search_books.py "extrusion" --book Grain_Processing
# 命中页码后，按页读取原文
python3 references/books/tools/read_page.py Food_Gels 120
python3 references/books/tools/read_page.py Plant_Protein 45 60
```
- 检索到要点后，读取 `toc/<分区>/<书名>.md` 定位章节，再读取对应 `text/...txt` 的页码附近原文引用。
- 引用时注明：书/章标题、编者或作者、出版社、年份、许可与页码。

## 二、主题标签索引

- **3D食品打印**：Plant-based food products, precision fermentation and 3D food printing（2024）
- **AI**：Applications of Artificial Intelligence in Food Industry（2025）
- **GMP**：Good practices for the meat industry（2004）
- **HACCP**：FAO/WHO guidance to governments on the application of HACCP in small/less-developed businesses（2007）；Food quality and safety systems: A training manual on food hygiene and HACCP（1998）
- **中小企业**：Good packaging practices for micro, small and medium-sized food processing enterprises（2024）；Policy measures for micro, small and medium food processing enterprises（2015）
- **中试/中小企业**：Reducing food loss and waste in processing, distribution and retail of MSMEs（2024）
- **乳制品加工**：Dairy Products（2025）
- **乳化**：Food Colloids（2026）
- **乳品**：Health Promoting Compounds in Milk and Dairy Products（2026）；Dairy Products（2025）；Chemical and Technological Characterization of Dairy Products（2021）；Dairy Chemistry: A Practical Handbook（1920）
- **乳品加工**：Technical and investment guidelines for milk cooling centres（2015）；Agribusiness Handbook: Milk / Dairy Products（2009）；Milk Testing and Payment Systems（2009）；Milk Processing Toolkit: Milk（2007）
- **产业手册**：Agribusiness Handbook: Sunflower Crude and Refined Oils（2010）；Agribusiness Handbook: Fruit and Vegetable Processing（2009）；Agribusiness Handbook: Milk / Dairy Products（2009）；Agribusiness Handbook: Red Meat（2009）
- **价值链**：Processing for Prosperity（2011）；Value from Village Processing（2011）
- **优化算法**：Data-Driven Intelligent Modeling and Optimization Algorithms for Industrial Processes（2025）
- **保藏**：Preserving green leafy vegetables and fruits（2011）；Fruit Processing Toolkit: Preservatives（2007）；Handling and preservation of fruits and vegetables by combined methods for rural areas（2003）；Manual on fish canning（1988）；Home and Farm Food Preservation（1918）；Successful Canning and Preserving（1917）；Canning and Preserving of Food Products with Bacteriological Technique（1905）；The Art of Canning and Preserving as an Industry（1900）；The Preservation of Fishery Products for Food（1899）
- **保鲜**：Enhancing Shelf Life of Food Products（2026）
- **健康**：Health Promoting Compounds in Milk and Dairy Products（2026）；Nutritional Value of Meat and Meat Products and Their Role in Human Health（2026）
- **农村加工**：Processing for Prosperity（2011）；Value from Village Processing（2011）
- **冷冻**：Freezing of fruits and vegetables（2005）
- **冷却**：Technical and investment guidelines for milk cooling centres（2015）
- **冷链**：Solar energy and the cold chain（2025）；Sustainable food cold chains: Opportunities, challenges and the way forward（2022）；Technical and investment guidelines for milk cooling centres（2015）
- **分析**：Advances in the Design Analysis and Evaluation of Functional Foods（2026）；Extraction and Analysis of Chemical Compositions of Natural Products and Plants（2026）；Advances in Analysis of Food and Beverages（2025）；Advances in Analysis of Flavors and Fragrances（2025）
- **分析方法**：Development of Analytical Methods in the Field of Food Analysis（2024）
- **制粉**：Small mills in Africa（2006）
- **副产物**：Bioactive Compounds in Foods and Their ByProducts（2026）；The Use of Waste Products from the Food Industry to Obtain High ValueAdded Products（2024）；Fish silage production by fermentation（2024）；Production of high-value products from by-products of aquatic food processing（2024）；By-products of tuna processing（2013）
- **功能**：Bioactive Compounds in Foods（2025）；Current Research on Probiotics and Fermented Products（2024）；The Antioxidant Potential of Fermented Foods（2024）
- **功能成分**：Health Promoting Compounds in Milk and Dairy Products（2026）
- **功能特性**：Effect of Processing and Cooking on Physicochemical Sensory and Functional Properties of Food（2026）；Functionality and Food Applications of Plant Proteins Volume II（2025）；Functionality and Food Applications of Plant Proteins（2020）
- **功能配料**：Impact of Functional Ingredients on Technological Sensory and Health Properties of Bakery Products（2026）；Environmentally Friendly Manufacturing of Food Additives and Functional Ingredients（2026）
- **功能食品**：Development of Functional and Fortified Foods（2026）；Advances in the Design Analysis and Evaluation of Functional Foods（2026）；Bioactive Compounds in Foods and Their ByProducts（2026）；Functional Bakery Products（2025）；Marine Fish Oils as Functional Foods（2024）；Sustainable Functional Food Processing（2022）；Recent Advances and Future Trends in Fermented and Functional Foods（2021）
- **加工**：Cereals and Cereal-Based Foods（2025）
- **加工与烹饪**：Effect of Processing and Cooking on Physicochemical Sensory and Functional Properties of Food（2026）
- **加工品质**：Feeding and Processing Affect Meat Quality and Sensory Evaluation（2026）
- **加工工艺**：Sustainable Functional Food Processing（2022）
- **加工影响**：Effects of Processing on Food Composition Nutritional Value and Sensory Quality（2024）
- **加工技术**：Recent Advances in Biological and Technological Research of Fresh Fruit and Vegetable（2026）；The FAO-Thiaroye Processing Technique (FTT)（2021）
- **加工贮藏**：Mechanism and Engineering Research on Processing Storage and Preservation of Fresh Food（2024）；Physicochemical Sensory and Nutritional Properties of Foods Affected by Processing and Storage Series II（2024）
- **加工通则**：Reducing food loss and waste in processing, distribution and retail of MSMEs（2024）；Policy measures for micro, small and medium food processing enterprises（2015）；Processing for Prosperity（2011）；Value from Village Processing（2011）
- **包装**：Advanced Coatings and Films for Food Packing and Storage（2024）；Good packaging practices for micro, small and medium-sized food processing enterprises（2024）；Appropriate food packaging solutions for developing countries（2014）
- **包装材料**：Recent Advances in the Development of Thin Films（2024）
- **化学与工艺**：Chemical and Technological Characterization of Dairy Products（2021）
- **卫生**：Good practices for the meat industry（2004）；Food quality and safety systems: A training manual on food hygiene and HACCP（1998）；Text-book of Meat Hygiene（1939）
- **历史经典**：Text-book of Meat Hygiene（1939）；Dairy Chemistry: A Practical Handbook（1920）；Drying Vegetables and Fruits for Home Use（1919）；Home and Farm Food Preservation（1918）；Successful Canning and Preserving（1917）；Bread Making and Bread Baking（1915）；A Treatise on Flour, Yeast, Fermentation and Baking（1914）；Leavening Agents: Yeast, Leaven, Salt-rising Fermentation, Baking Powder（1914）；Canning and Preserving of Food Products with Bacteriological Technique（1905）；The Art of Canning and Preserving as an Industry（1900）；The Preservation of Fishery Products for Food（1899）；The Complete Confectioner, Pastry-Cook and Baker（1846）
- **发展中国家**：Appropriate food packaging solutions for developing countries（2014）
- **发酵食品**：Precision fermentation（2025）；Current Research on Probiotics and Fermented Products（2024）；The Antioxidant Potential of Fermented Foods（2024）；Fish silage production by fermentation（2024）；Recent Advances and Future Trends in Fermented and Functional Foods（2021）；Traditional fermented food and beverages for improved livelihoods（2011）；Cereals Processing Toolkit: Lactic Fermentation（2007）
- **可持续**：Food Waste Management and Sustainability（2026）；Food Science and Engineering for Sustainability（2025）；Sustainable Functional Food Processing（2022）；Sustainable food cold chains: Opportunities, challenges and the way forward（2022）
- **可持续蛋白**：Sustainable Protein Sources（2026）
- **品质**：Novel Thermal and Nonthermal Technologies towards Sustainability and Microbiological Food Safety and Quality（2026）
- **品质评价**：Processing Foods Process Optimization and Quality Assessment（2024）
- **增值**：Novel Foods Food-Grade Materials and Environmentally Friendly Compounds from Food Waste（2026）
- **多糖淀粉**：Research on the Properties of Polysaccharides Starch Protein Pectin and Fibre in Food Processing（2023）
- **天然产物**：Extraction and Analysis of Chemical Compositions of Natural Products and Plants（2026）
- **太阳能**：Solar energy and the cold chain（2025）
- **小规模加工**：Guide to small scale trout processing methods（2012）；Meat processing technology for small- to medium-scale producers（2007）；FAO/WHO guidance to governments on the application of HACCP in small/less-developed businesses（2007）；Small mills in Africa（2006）；Small-scale palm oil processing in Africa（2002）；Principles and practices of small- and medium-scale fruit juice processing（2001）；Small-scale poultry processing（1992）
- **工业化**：The Art of Canning and Preserving as an Industry（1900）
- **工具箱**：Fruit Processing Toolkit: Dried Fruit（2007）；Fruit Processing Toolkit: Preservatives（2007）；Cereals Processing Toolkit: Breads（2007）；Cereals Processing Toolkit: Lactic Fermentation（2007）；Cereals Processing Toolkit: Noodles（2007）；Milk Processing Toolkit: Milk（2007）；Meat Processing Toolkit: Pork（2007）；Meat Processing Toolkit: Poultry（2007）；Meat Processing Toolkit: Products Formulation（2007）；Roots and Tubers Processing Toolkit: Cassava Starch（2007）；Sugar Processing Toolkit: Sugarcane Syrup（2007）
- **工程技术**：Mechanism and Engineering Research on Processing Storage and Preservation of Fresh Food（2024）
- **工艺**：Plant Protein Processing（2026）
- **工艺优化**：Optimization of Nonthermal Technology in Food Processing（2026）
- **工艺工程**：Food Science and Engineering for Sustainability（2025）；Processing Foods Process Optimization and Quality Assessment（2024）
- **干燥**：Fruit Processing Toolkit: Dried Fruit（2007）；Drying Vegetables and Fruits for Home Use（1919）
- **应用**：Functionality and Food Applications of Plant Proteins Volume II（2025）；Application of Polymers in Food Sciences（2024）；Functionality and Food Applications of Plant Proteins（2020）
- **延长保质期**：Enhancing Shelf Life of Food Products（2026）
- **微波辅助**：Microwave and Ultrasound-Assisted Extraction for Plant Bioactive Compounds（2026）
- **微生物**：Canning and Preserving of Food Products with Bacteriological Technique（1905）
- **微生物安全**：Novel Thermal and Nonthermal Technologies towards Sustainability and Microbiological Food Safety and Quality（2026）
- **感官**：Effect of Processing and Cooking on Physicochemical Sensory and Functional Properties of Food（2026）；Impact of Functional Ingredients on Technological Sensory and Health Properties of Bakery Products（2026）；Feeding and Processing Affect Meat Quality and Sensory Evaluation（2026）；Physicochemical Sensory and Nutritional Properties of Foods Affected by Processing and Storage Series II（2024）
- **感官品质**：Effects of Processing on Food Composition Nutritional Value and Sensory Quality（2024）
- **抗氧化**：The Antioxidant Potential of Fermented Foods（2024）
- **提取**：Microwave and Ultrasound-Assisted Extraction for Plant Bioactive Compounds（2026）；Extraction and Analysis of Chemical Compositions of Natural Products and Plants（2026）
- **政策**：Policy measures for micro, small and medium food processing enterprises（2015）
- **数据驱动**：Applications of Artificial Intelligence in Food Industry（2025）
- **新兴技术**：Precision fermentation（2025）；Plant-based food products, precision fermentation and 3D food printing（2024）
- **新型杀菌**：Optimization of Nonthermal Technology in Food Processing（2026）；Application of Novel Thermal Technology in Foods Processing（2022）
- **新型食品**：Recent Trends in Designing Novel Foods（2026）
- **智能加工**：Applications of Artificial Intelligence in Food Industry（2025）；Data-Driven Intelligent Modeling and Optimization Algorithms for Industrial Processes（2025）
- **替代蛋白**：Sustainable Protein Sources（2026）
- **果汁**：Principles and practices of small- and medium-scale fruit juice processing（2001）
- **果蔬**：Recent Advances in Biological and Technological Research of Fresh Fruit and Vegetable（2026）
- **果蔬保鲜**：Mechanism and Engineering Research on Processing Storage and Preservation of Fresh Food（2024）
- **果蔬加工**：Thermal and Non-Thermal Treatments to Preserve and Encourage Bioactive Compounds in Fruit and Vegetables Based Products（2023）；Preserving green leafy vegetables and fruits（2011）；Processing of fresh-cut tropical fruits and vegetables: A technical guide（2010）；Agribusiness Handbook: Fruit and Vegetable Processing（2009）；Fruit Processing Toolkit: Dried Fruit（2007）；Fruit Processing Toolkit: Preservatives（2007）；Freezing of fruits and vegetables（2005）；Handling and preservation of fruits and vegetables by combined methods for rural areas（2003）；Quality control in fruit and vegetable processing（1988）；Drying Vegetables and Fruits for Home Use（1919）；Home and Farm Food Preservation（1918）
- **栅栏技术**：Handling and preservation of fruits and vegetables by combined methods for rural areas（2003）
- **检测**：Advances in Analysis of Food and Beverages（2025）；Development of Analytical Methods in the Field of Food Analysis（2024）；Milk Testing and Payment Systems（2009）
- **植物基**：Plant-based food products, precision fermentation and 3D food printing（2024）
- **植物蛋白**：Plant Protein Processing（2026）；Sustainable Protein Sources（2026）；Functionality and Food Applications of Plant Proteins Volume II（2025）；Functionality and Food Applications of Plant Proteins（2020）
- **水产**：Marine Fish Oils as Functional Foods（2024）
- **水产加工**：Recent Advances in Aquatic Food Products Processing（2024）；Fish silage production by fermentation（2024）；Production of high-value products from by-products of aquatic food processing（2024）；The FAO-Thiaroye Processing Technique (FTT)（2021）；Technical guide to fish canning（2013）；By-products of tuna processing（2013）；Guide to small scale trout processing methods（2012）；Manual on fish canning（1988）；The Preservation of Fishery Products for Food（1899）
- **水产品**：Recent Advances in Aquatic Food Products Processing（2024）
- **油脂加工**：Agribusiness Handbook: Sunflower Crude and Refined Oils（2010）；Small-scale palm oil processing in Africa（2002）
- **涂层**：Recent Advances in the Development of Thin Films（2024）
- **涂膜**：Advanced Coatings and Films for Food Packing and Storage（2024）
- **淀粉加工**：Roots and Tubers Processing Toolkit: Cassava Starch（2007）
- **烘焙**：Impact of Functional Ingredients on Technological Sensory and Health Properties of Bakery Products（2026）；Functional Bakery Products（2025）；Cereals Processing Toolkit: Breads（2007）；Bread Making and Bread Baking（1915）；A Treatise on Flour, Yeast, Fermentation and Baking（1914）；Leavening Agents: Yeast, Leaven, Salt-rising Fermentation, Baking Powder（1914）；The Complete Confectioner, Pastry-Cook and Baker（1846）
- **烟熏**：The FAO-Thiaroye Processing Technique (FTT)（2021）
- **热/非热**：Thermal and Non-Thermal Treatments to Preserve and Encourage Bioactive Compounds in Fruit and Vegetables Based Products（2023）
- **热加工**：Novel Thermal and Nonthermal Technologies towards Sustainability and Microbiological Food Safety and Quality（2026）；Application of Novel Thermal Technology in Foods Processing（2022）
- **猪肉**：Meat Processing Toolkit: Pork（2007）
- **生物活性**：Bioactive Compounds in Foods and Their ByProducts（2026）；Thermal and Non-Thermal Treatments to Preserve and Encourage Bioactive Compounds in Fruit and Vegetables Based Products（2023）
- **生物活性成分**：Bioactive Compounds in Foods（2025）
- **界面**：Food Colloids（2026）
- **益生菌**：Current Research on Probiotics and Fermented Products（2024）
- **真菌毒素**：On-farm mycotoxin control in food and feed grain: Training manual（2007）
- **禽类**：Meat Processing Toolkit: Poultry（2007）；Small-scale poultry processing（1992）
- **管理**：Food Waste Management and Sustainability（2026）
- **粮食**：Trends in Grain Processing for Food Industry（2025）
- **精密发酵**：Precision fermentation（2025）
- **糖加工**：Sugar Processing Toolkit: Sugarcane Syrup（2007）
- **糖果**：The Complete Confectioner, Pastry-Cook and Baker（1846）
- **纯化**：Recent Advances in Membrane Filtration and Purification Technologies（2026）
- **纳米技术**：Nanomaterials and Nanotechnology in Food（2026）
- **纳米材料**：Nanomaterials and Nanotechnology in Food（2026）
- **绿色制造**：Environmentally Friendly Manufacturing of Food Additives and Functional Ingredients（2026）
- **罐藏**：Technical guide to fish canning（2013）；Manual on fish canning（1988）；Successful Canning and Preserving（1917）；Canning and Preserving of Food Products with Bacteriological Technique（1905）；The Art of Canning and Preserving as an Industry（1900）
- **肉制品**：Nutritional Value of Meat and Meat Products and Their Role in Human Health（2026）；Feeding and Processing Affect Meat Quality and Sensory Evaluation（2026）；Text-book of Meat Hygiene（1939）
- **肉制品加工**：Agribusiness Handbook: Red Meat（2009）；Meat processing technology for small- to medium-scale producers（2007）；Meat Processing Toolkit: Pork（2007）；Meat Processing Toolkit: Poultry（2007）；Meat Processing Toolkit: Products Formulation（2007）；Good practices for the meat industry（2004）；Small-scale poultry processing（1992）
- **胶体**：Food Gels（2025）
- **膜分离**：Recent Advances in Membrane Filtration and Purification Technologies（2026）
- **膨松剂**：Leavening Agents: Yeast, Leaven, Salt-rising Fermentation, Baking Powder（1914）
- **营养**：Nutritional Value of Meat and Meat Products and Their Role in Human Health（2026）；Physicochemical Sensory and Nutritional Properties of Foods Affected by Processing and Storage Series II（2024）
- **营养强化**：Development of Functional and Fortified Foods（2026）；Qualitative and Nutritional Improvement of Cereal-Based Foods and Beverages（2021）
- **营养成分**：Effects of Processing on Food Composition Nutritional Value and Sensory Quality（2024）
- **薄膜**：Recent Advances in the Development of Thin Films（2024）
- **薯类**：Roots and Tubers Processing Toolkit: Cassava Starch（2007）
- **蛋白加工**：Plant Protein Processing（2026）
- **蛋白果胶**：Research on the Properties of Polysaccharides Starch Protein Pectin and Fibre in Food Processing（2023）
- **表征**：Chemical and Technological Characterization of Dairy Products（2021）
- **设计**：Recent Trends in Designing Novel Foods（2026）
- **设计评价**：Advances in the Design Analysis and Evaluation of Functional Foods（2026）
- **谷物**：Cereals and Cereal-Based Foods（2025）
- **谷物加工**：Trends in Grain Processing for Food Industry（2025）；On-farm post-harvest management of food grains（2009）；Cereals Processing Toolkit: Breads（2007）；Cereals Processing Toolkit: Lactic Fermentation（2007）；Cereals Processing Toolkit: Noodles（2007）；On-farm mycotoxin control in food and feed grain: Training manual（2007）；Small mills in Africa（2006）；A Treatise on Flour, Yeast, Fermentation and Baking（1914）
- **谷物食品**：Cereals and Cereal-Based Foods（2025）；Qualitative and Nutritional Improvement of Cereal-Based Foods and Beverages（2021）
- **货架期**：Enhancing Shelf Life of Food Products（2026）
- **质构**：Food Gels（2025）
- **质量**：Milk Testing and Payment Systems（2009）
- **质量控制**：Quality control in fruit and vegetable processing（1988）
- **贮藏**：Advanced Coatings and Films for Food Packing and Storage（2024）；Sustainable food cold chains: Opportunities, challenges and the way forward（2022）；On-farm post-harvest management of food grains（2009）
- **超声辅助**：Microwave and Ultrasound-Assisted Extraction for Plant Bioactive Compounds（2026）
- **趋势**：Recent Trends in Designing Novel Foods（2026）；Recent Advances and Future Trends in Fermented and Functional Foods（2021）
- **过滤**：Recent Advances in Membrane Filtration and Purification Technologies（2026）
- **过程优化**：Processing Foods Process Optimization and Quality Assessment（2024）
- **过程建模**：Data-Driven Intelligent Modeling and Optimization Algorithms for Industrial Processes（2025）
- **进展**：Recent Advances in Aquatic Food Products Processing（2024）
- **配方**：Development of Functional and Fortified Foods（2026）；Functional Bakery Products（2025）；Meat Processing Toolkit: Products Formulation（2007）
- **采后**：Recent Advances in Biological and Technological Research of Fresh Fruit and Vegetable（2026）；On-farm post-harvest management of food grains（2009）
- **非热加工**：Optimization of Nonthermal Technology in Food Processing（2026）；Novel Thermal and Nonthermal Technologies towards Sustainability and Microbiological Food Safety and Quality（2026）
- **面制品**：Cereals Processing Toolkit: Noodles（2007）
- **风味**：Advances in Analysis of Flavors and Fragrances（2025）
- **食品**：Nanomaterials and Nanotechnology in Food（2026）；Bioactive Compounds in Foods（2025）
- **食品凝胶**：Food Gels（2025）
- **食品分析**：Development of Analytical Methods in the Field of Food Analysis（2024）
- **食品加工**：Research on the Properties of Polysaccharides Starch Protein Pectin and Fibre in Food Processing（2023）；Application of Novel Thermal Technology in Foods Processing（2022）
- **食品化学**：Dairy Chemistry: A Practical Handbook（1920）
- **食品安全**：FAO/WHO guidance to governments on the application of HACCP in small/less-developed businesses（2007）；On-farm mycotoxin control in food and feed grain: Training manual（2007）；Food quality and safety systems: A training manual on food hygiene and HACCP（1998）
- **食品工业**：Trends in Grain Processing for Food Industry（2025）
- **食品废弃物**：Food Waste Management and Sustainability（2026）；Novel Foods Food-Grade Materials and Environmentally Friendly Compounds from Food Waste（2026）；The Use of Waste Products from the Food Industry to Obtain High ValueAdded Products（2024）
- **食品损耗**：Reducing food loss and waste in processing, distribution and retail of MSMEs（2024）
- **食品添加剂**：Environmentally Friendly Manufacturing of Food Additives and Functional Ingredients（2026）
- **食品科学**：Food Science and Engineering for Sustainability（2025）；Application of Polymers in Food Sciences（2024）
- **食品级材料**：Novel Foods Food-Grade Materials and Environmentally Friendly Compounds from Food Waste（2026）
- **食品胶体**：Food Colloids（2026）
- **食品饮料**：Advances in Analysis of Food and Beverages（2025）
- **饮料**：Qualitative and Nutritional Improvement of Cereal-Based Foods and Beverages（2021）
- **饮料加工**：Traditional fermented food and beverages for improved livelihoods（2011）；Principles and practices of small- and medium-scale fruit juice processing（2001）
- **香精**：Advances in Analysis of Flavors and Fragrances（2025）
- **高值化**：The Use of Waste Products from the Food Industry to Obtain High ValueAdded Products（2024）；Production of high-value products from by-products of aquatic food processing（2024）
- **高分子**：Application of Polymers in Food Sciences（2024）
- **鱼油**：Marine Fish Oils as Functional Foods（2024）
- **鲜切**：Processing of fresh-cut tropical fruits and vegetables: A technical guide（2010）

## MDPI Books（CC BY，可自由再分发）

| 书名 | 年 | 页 | 许可 | 全文 | 目录 | 来源 |
|---|---|---|---|---|---|---|
| Optimization of Nonthermal Technology in Food Processing | 2026 | 192 | CC BY 4.0 | `text/mdpi/Optimization_of_Nonthermal_Technology_in_Food_Processing_2026.txt` | `toc/mdpi/Optimization_of_Nonthermal_Technology_in_Food_Processing_2026.md` | https://doi.org/10.3390/books978-3-7258-7243-5 |
| Novel Thermal and Nonthermal Technologies towards Sustainability and Microbiological Food Safety and Quality | 2026 | 134 | CC BY 4.0 | `text/mdpi/Novel_Thermal_and_Nonthermal_Technologies_towards_Sustainability_and_Microbiological_Food_Safety_and_Quality_2026.txt` | `toc/mdpi/Novel_Thermal_and_Nonthermal_Technologies_towards_Sustainability_and_Microbiological_Food_Safety_and_Quality_2026.md` | https://www.mdpi.com/books |
| Microwave and Ultrasound-Assisted Extraction for Plant Bioactive Compounds | 2026 | 160 | CC BY 4.0 | `text/mdpi/Microwave_and_UltrasoundAssisted_Extraction_for_Plant_Bioactive_Compounds_2026.txt` | `toc/mdpi/Microwave_and_UltrasoundAssisted_Extraction_for_Plant_Bioactive_Compounds_2026.md` | https://www.mdpi.com/books |
| Enhancing Shelf Life of Food Products | 2026 | 248 | CC BY 4.0 | `text/mdpi/Enhancing_Shelf_Life_of_Food_Products_2026.txt` | `toc/mdpi/Enhancing_Shelf_Life_of_Food_Products_2026.md` | https://www.mdpi.com/books |
| Effect of Processing and Cooking on Physicochemical Sensory and Functional Properties of Food | 2026 | 320 | CC BY 4.0 | `text/mdpi/Effect_of_Processing_and_Cooking_on_Physicochemical_Sensory_and_Functional_Properties_of_Food_2026.txt` | `toc/mdpi/Effect_of_Processing_and_Cooking_on_Physicochemical_Sensory_and_Functional_Properties_of_Food_2026.md` | https://doi.org/10.3390/books978-3-7258-7079-0 |
| Impact of Functional Ingredients on Technological Sensory and Health Properties of Bakery Products | 2026 | 170 | CC BY 4.0 | `text/mdpi/Impact_of_Functional_Ingredients_on_Technological_Sensory_and_Health_Properties_of_Bakery_Products_2026.txt` | `toc/mdpi/Impact_of_Functional_Ingredients_on_Technological_Sensory_and_Health_Properties_of_Bakery_Products_2026.md` | https://www.mdpi.com/books |
| Health Promoting Compounds in Milk and Dairy Products | 2026 | 136 | CC BY 4.0 | `text/mdpi/Health_Promoting_Compounds_in_Milk_and_Dairy_Products_2026.txt` | `toc/mdpi/Health_Promoting_Compounds_in_Milk_and_Dairy_Products_2026.md` | https://doi.org/10.3390/books978-3-7258-7353-1 |
| Nutritional Value of Meat and Meat Products and Their Role in Human Health | 2026 | 266 | CC BY 4.0 | `text/mdpi/Nutritional_Value_of_Meat_and_Meat_Products_and_Their_Role_in_Human_Health_2026.txt` | `toc/mdpi/Nutritional_Value_of_Meat_and_Meat_Products_and_Their_Role_in_Human_Health_2026.md` | https://doi.org/10.3390/books978-3-7258-7273-2 |
| Feeding and Processing Affect Meat Quality and Sensory Evaluation | 2026 | 182 | CC BY 4.0 | `text/mdpi/Feeding_and_Processing_Affect_Meat_Quality_and_Sensory_Evaluation_2026.txt` | `toc/mdpi/Feeding_and_Processing_Affect_Meat_Quality_and_Sensory_Evaluation_2026.md` | https://doi.org/10.3390/books978-3-7258-6933-6 |
| Plant Protein Processing | 2026 | 198 | CC BY 4.0 | `text/mdpi/Plant_Protein_Processing_2026.txt` | `toc/mdpi/Plant_Protein_Processing_2026.md` | https://doi.org/10.3390/books978-3-7258-7676-1 |
| Sustainable Protein Sources | 2026 | 172 | CC BY 4.0 | `text/mdpi/Sustainable_Protein_Sources_2026.txt` | `toc/mdpi/Sustainable_Protein_Sources_2026.md` | https://doi.org/10.3390/books978-3-7258-7760-7 |
| Food Colloids | 2026 | 154 | CC BY 4.0 | `text/mdpi/Food_Colloids_2026.txt` | `toc/mdpi/Food_Colloids_2026.md` | https://doi.org/10.3390/books978-3-7258-7211-4 |
| Development of Functional and Fortified Foods | 2026 | 222 | CC BY 4.0 | `text/mdpi/Development_of_Functional_and_Fortified_Foods_2026.txt` | `toc/mdpi/Development_of_Functional_and_Fortified_Foods_2026.md` | https://www.mdpi.com/books |
| Advances in the Design Analysis and Evaluation of Functional Foods | 2026 | 186 | CC BY 4.0 | `text/mdpi/Advances_in_the_Design_Analysis_and_Evaluation_of_Functional_Foods_2026.txt` | `toc/mdpi/Advances_in_the_Design_Analysis_and_Evaluation_of_Functional_Foods_2026.md` | https://doi.org/10.3390/books978-3-7258-8940-2 |
| Recent Trends in Designing Novel Foods | 2026 | 208 | CC BY 4.0 | `text/mdpi/Recent_Trends_in_Designing_Novel_Foods_2026.txt` | `toc/mdpi/Recent_Trends_in_Designing_Novel_Foods_2026.md` | https://www.mdpi.com/books |
| Nanomaterials and Nanotechnology in Food | 2026 | 138 | CC BY 4.0 | `text/mdpi/Nanomaterials_and_Nanotechnology_in_Food_2026.txt` | `toc/mdpi/Nanomaterials_and_Nanotechnology_in_Food_2026.md` | https://doi.org/10.3390/books978-3-7258-8278-6 |
| Environmentally Friendly Manufacturing of Food Additives and Functional Ingredients | 2026 | 154 | CC BY 4.0 | `text/mdpi/Environmentally_Friendly_Manufacturing_of_Food_Additives_and_Functional_Ingredients_2026.txt` | `toc/mdpi/Environmentally_Friendly_Manufacturing_of_Food_Additives_and_Functional_Ingredients_2026.md` | https://doi.org/10.3390/books978-3-7258-7646-4 |
| Bioactive Compounds in Foods and Their ByProducts | 2026 | 356 | CC BY 4.0 | `text/mdpi/Bioactive_Compounds_in_Foods_and_Their_ByProducts_2026.txt` | `toc/mdpi/Bioactive_Compounds_in_Foods_and_Their_ByProducts_2026.md` | https://www.mdpi.com/books |
| Extraction and Analysis of Chemical Compositions of Natural Products and Plants | 2026 | 224 | CC BY 4.0 | `text/mdpi/Extraction_and_Analysis_of_Chemical_Compositions_of_Natural_Products_and_Plants_2026.txt` | `toc/mdpi/Extraction_and_Analysis_of_Chemical_Compositions_of_Natural_Products_and_Plants_2026.md` | https://doi.org/10.3390/books978-3-7258-8626-5 |
| Recent Advances in Biological and Technological Research of Fresh Fruit and Vegetable | 2026 | 228 | CC BY 4.0 | `text/mdpi/Recent_Advances_in_Biological_and_Technological_Research_of_Fresh_Fruit_and_Vegetable_2026.txt` | `toc/mdpi/Recent_Advances_in_Biological_and_Technological_Research_of_Fresh_Fruit_and_Vegetable_2026.md` | https://www.mdpi.com/books |
| Recent Advances in Membrane Filtration and Purification Technologies | 2026 | 130 | CC BY 4.0 | `text/mdpi/Recent_Advances_in_Membrane_Filtration_and_Purification_Technologies_2026.txt` | `toc/mdpi/Recent_Advances_in_Membrane_Filtration_and_Purification_Technologies_2026.md` | https://doi.org/10.3390/books978-3-7258-7598-6 |
| Food Waste Management and Sustainability | 2026 | 238 | CC BY 4.0 | `text/mdpi/Food_Waste_Management_and_Sustainability_2026.txt` | `toc/mdpi/Food_Waste_Management_and_Sustainability_2026.md` | https://doi.org/10.3390/books978-3-7258-7790-4 |
| Novel Foods Food-Grade Materials and Environmentally Friendly Compounds from Food Waste | 2026 | 276 | CC BY 4.0 | `text/mdpi/Novel_Foods_FoodGrade_Materials_and_Environmentally_Friendly_Compounds_from_Food_Waste_2026.txt` | `toc/mdpi/Novel_Foods_FoodGrade_Materials_and_Environmentally_Friendly_Compounds_from_Food_Waste_2026.md` | https://www.mdpi.com/books |
| Food Science and Engineering for Sustainability | 2025 | 206 | CC BY 4.0 | `text/mdpi/Food_Science_and_Engineering_for_Sustainability_2025.txt` | `toc/mdpi/Food_Science_and_Engineering_for_Sustainability_2025.md` | https://doi.org/10.3390/books978-3-7258-5388-5 |
| Applications of Artificial Intelligence in Food Industry | 2025 | 300 | CC BY 4.0 | `text/mdpi/Applications_of_Artificial_Intelligence_in_Food_Industry_2025.txt` | `toc/mdpi/Applications_of_Artificial_Intelligence_in_Food_Industry_2025.md` | https://doi.org/10.3390/books978-3-7258-4836-2 |
| Data-Driven Intelligent Modeling and Optimization Algorithms for Industrial Processes | 2025 | 256 | CC BY 4.0 | `text/mdpi/DataDriven_Intelligent_Modeling_and_Optimization_Algorithms_for_Industrial_Processes_2025.txt` | `toc/mdpi/DataDriven_Intelligent_Modeling_and_Optimization_Algorithms_for_Industrial_Processes_2025.md` | https://doi.org/10.3390/books978-3-7258-2986-6 |
| Trends in Grain Processing for Food Industry | 2025 | 240 | CC BY 4.0 | `text/mdpi/Trends_in_Grain_Processing_for_Food_Industry_2025.txt` | `toc/mdpi/Trends_in_Grain_Processing_for_Food_Industry_2025.md` | https://www.mdpi.com/books |
| Cereals and Cereal-Based Foods | 2025 | 214 | CC BY 4.0 | `text/mdpi/Cereals_and_CerealBased_Foods_2025.txt` | `toc/mdpi/Cereals_and_CerealBased_Foods_2025.md` | https://doi.org/10.3390/books978-3-7258-5696-1 |
| Functional Bakery Products | 2025 | 252 | CC BY 4.0 | `text/mdpi/Functional_Bakery_Products_2025.txt` | `toc/mdpi/Functional_Bakery_Products_2025.md` | https://www.mdpi.com/books |
| Dairy Products | 2025 | 180 | CC BY 4.0 | `text/mdpi/Dairy_Products_2025.txt` | `toc/mdpi/Dairy_Products_2025.md` | https://doi.org/10.3390/books978-3-7258-3550-8 |
| Functionality and Food Applications of Plant Proteins Volume II | 2025 | 266 | CC BY 4.0 | `text/mdpi/Functionality_and_Food_Applications_of_Plant_Proteins_Volume_II_2025.txt` | `toc/mdpi/Functionality_and_Food_Applications_of_Plant_Proteins_Volume_II_2025.md` | https://doi.org/10.3390/books978-3-7258-3577-5 |
| Food Gels | 2025 | 220 | CC BY 4.0 | `text/mdpi/Food_Gels_2025.txt` | `toc/mdpi/Food_Gels_2025.md` | https://doi.org/10.3390/books978-3-7258-5898-9 |
| Bioactive Compounds in Foods | 2025 | 232 | CC BY 4.0 | `text/mdpi/Bioactive_Compounds_in_Foods_2025.txt` | `toc/mdpi/Bioactive_Compounds_in_Foods_2025.md` | https://www.mdpi.com/books |
| Advances in Analysis of Food and Beverages | 2025 | 358 | CC BY 4.0 | `text/mdpi/Advances_in_Analysis_of_Food_and_Beverages_2025.txt` | `toc/mdpi/Advances_in_Analysis_of_Food_and_Beverages_2025.md` | https://doi.org/10.3390/books978-3-7258-7870-3 |
| Advances in Analysis of Flavors and Fragrances | 2025 | 606 | CC BY 4.0 | `text/mdpi/Advances_in_Analysis_of_Flavors_and_Fragrances_2025.txt` | `toc/mdpi/Advances_in_Analysis_of_Flavors_and_Fragrances_2025.md` | https://doi.org/10.3390/books978-3-7258-4500-2 |
| Processing Foods Process Optimization and Quality Assessment | 2024 | 216 | CC BY 4.0 | `text/mdpi/Processing_Foods_Process_Optimization_and_Quality_Assessment_2024.txt` | `toc/mdpi/Processing_Foods_Process_Optimization_and_Quality_Assessment_2024.md` | https://doi.org/10.3390/books978-3-0365-7779-1 |
| Mechanism and Engineering Research on Processing Storage and Preservation of Fresh Food | 2024 | 330 | CC BY 4.0 | `text/mdpi/Mechanism_and_Engineering_Research_on_Processing_Storage_and_Preservation_of_Fresh_Food_2024.txt` | `toc/mdpi/Mechanism_and_Engineering_Research_on_Processing_Storage_and_Preservation_of_Fresh_Food_2024.md` | https://doi.org/10.3390/books978-3-0365-9988-5 |
| Advanced Coatings and Films for Food Packing and Storage | 2024 | 226 | CC BY 4.0 | `text/mdpi/Advanced_Coatings_and_Films_for_Food_Packing_and_Storage_2024.txt` | `toc/mdpi/Advanced_Coatings_and_Films_for_Food_Packing_and_Storage_2024.md` | https://doi.org/10.3390/books978-3-7258-2708-4 |
| Recent Advances in the Development of Thin Films | 2024 | 208 | CC BY 4.0 | `text/mdpi/Recent_Advances_in_the_Development_of_Thin_Films_2024.txt` | `toc/mdpi/Recent_Advances_in_the_Development_of_Thin_Films_2024.md` | https://doi.org/10.3390/books978-3-7258-1856-3 |
| Effects of Processing on Food Composition Nutritional Value and Sensory Quality | 2024 | 184 | CC BY 4.0 | `text/mdpi/Effects_of_Processing_on_Food_Composition_Nutritional_Value_and_Sensory_Quality_2024.txt` | `toc/mdpi/Effects_of_Processing_on_Food_Composition_Nutritional_Value_and_Sensory_Quality_2024.md` | https://doi.org/10.3390/books978-3-0365-9952-6 |
| Physicochemical Sensory and Nutritional Properties of Foods Affected by Processing and Storage Series II | 2024 | 230 | CC BY 4.0 | `text/mdpi/Physicochemical_Sensory_and_Nutritional_Properties_of_Foods_Affected_by_Processing_and_Storage_Series_II_2024.txt` | `toc/mdpi/Physicochemical_Sensory_and_Nutritional_Properties_of_Foods_Affected_by_Processing_and_Storage_Series_II_2024.md` | https://www.mdpi.com/books |
| Recent Advances in Aquatic Food Products Processing | 2024 | 178 | CC BY 4.0 | `text/mdpi/Recent_Advances_in_Aquatic_Food_Products_Processing_2024.txt` | `toc/mdpi/Recent_Advances_in_Aquatic_Food_Products_Processing_2024.md` | https://www.mdpi.com/books |
| Marine Fish Oils as Functional Foods | 2024 | 170 | CC BY 4.0 | `text/mdpi/Marine_Fish_Oils_as_Functional_Foods_2024.txt` | `toc/mdpi/Marine_Fish_Oils_as_Functional_Foods_2024.md` | https://doi.org/10.3390/books978-3-7258-1224-0 |
| Application of Polymers in Food Sciences | 2024 | 268 | CC BY 4.0 | `text/mdpi/Application_of_Polymers_in_Food_Sciences_2024.txt` | `toc/mdpi/Application_of_Polymers_in_Food_Sciences_2024.md` | https://doi.org/10.3390/books978-3-7258-2193-8 |
| The Use of Waste Products from the Food Industry to Obtain High ValueAdded Products | 2024 | 202 | CC BY 4.0 | `text/mdpi/The_Use_of_Waste_Products_from_the_Food_Industry_to_Obtain_High_ValueAdded_Products_2024.txt` | `toc/mdpi/The_Use_of_Waste_Products_from_the_Food_Industry_to_Obtain_High_ValueAdded_Products_2024.md` | https://doi.org/10.3390/books978-3-7258-1484-8 |
| Current Research on Probiotics and Fermented Products | 2024 | 202 | CC BY 4.0 | `text/mdpi/Current_Research_on_Probiotics_and_Fermented_Products_2024.txt` | `toc/mdpi/Current_Research_on_Probiotics_and_Fermented_Products_2024.md` | https://www.mdpi.com/books |
| The Antioxidant Potential of Fermented Foods | 2024 | 234 | CC BY 4.0 | `text/mdpi/The_Antioxidant_Potential_of_Fermented_Foods_2024.txt` | `toc/mdpi/The_Antioxidant_Potential_of_Fermented_Foods_2024.md` | https://www.mdpi.com/books |
| Development of Analytical Methods in the Field of Food Analysis | 2024 | 198 | CC BY 4.0 | `text/mdpi/Development_of_Analytical_Methods_in_the_Field_of_Food_Analysis_2024.txt` | `toc/mdpi/Development_of_Analytical_Methods_in_the_Field_of_Food_Analysis_2024.md` | https://doi.org/10.3390/books978-3-0365-9811-6 |
| Thermal and Non-Thermal Treatments to Preserve and Encourage Bioactive Compounds in Fruit and Vegetables Based Products | 2023 | 308 | CC BY 4.0 | `text/mdpi/Thermal_and_NonThermal_Treatments_to_Preserve_and_Encourage_Bioactive_Compounds_in_Fruit_and_Vegetables_Based_Products_2023.txt` | `toc/mdpi/Thermal_and_NonThermal_Treatments_to_Preserve_and_Encourage_Bioactive_Compounds_in_Fruit_and_Vegetables_Based_Products_2023.md` | https://www.mdpi.com/books |
| Research on the Properties of Polysaccharides Starch Protein Pectin and Fibre in Food Processing | 2023 | 586 | CC BY 4.0 | `text/mdpi/Research_on_the_Properties_of_Polysaccharides_Starch_Protein_Pectin_and_Fibre_in_Food_Processing_2023.txt` | `toc/mdpi/Research_on_the_Properties_of_Polysaccharides_Starch_Protein_Pectin_and_Fibre_in_Food_Processing_2023.md` | https://doi.org/10.3390/books978-3-0365-9675-4 |
| Sustainable Functional Food Processing | 2022 | 456 | CC BY 4.0 | `text/mdpi/Sustainable_Functional_Food_Processing_2022.txt` | `toc/mdpi/Sustainable_Functional_Food_Processing_2022.md` | https://doi.org/10.3390/books978-3-0365-5302-3 |
| Application of Novel Thermal Technology in Foods Processing | 2022 | 178 | CC BY 4.0 | `text/mdpi/Application_of_Novel_Thermal_Technology_in_Foods_Processing_2022.txt` | `toc/mdpi/Application_of_Novel_Thermal_Technology_in_Foods_Processing_2022.md` | https://doi.org/10.3390/books978-3-0365-3003-1 |
| Qualitative and Nutritional Improvement of Cereal-Based Foods and Beverages | 2021 | 308 | CC BY 4.0 | `text/mdpi/Qualitative_and_Nutritional_Improvement_of_CerealBased_Foods_and_Beverages_2021.txt` | `toc/mdpi/Qualitative_and_Nutritional_Improvement_of_CerealBased_Foods_and_Beverages_2021.md` | https://doi.org/10.3390/books978-3-0365-0707-1 |
| Chemical and Technological Characterization of Dairy Products | 2021 | 218 | CC BY 4.0 | `text/mdpi/Chemical_and_Technological_Characterization_of_Dairy_Products_2021.txt` | `toc/mdpi/Chemical_and_Technological_Characterization_of_Dairy_Products_2021.md` | https://www.mdpi.com/books |
| Recent Advances and Future Trends in Fermented and Functional Foods | 2021 | 206 | CC BY 4.0 | `text/mdpi/Recent_Advances_and_Future_Trends_in_Fermented_and_Functional_Foods_2021.txt` | `toc/mdpi/Recent_Advances_and_Future_Trends_in_Fermented_and_Functional_Foods_2021.md` | https://www.mdpi.com/books |
| Functionality and Food Applications of Plant Proteins | 2020 | 274 | CC BY 4.0 | `text/mdpi/Functionality_and_Food_Applications_of_Plant_Proteins_2020.txt` | `toc/mdpi/Functionality_and_Food_Applications_of_Plant_Proteins_2020.md` | https://www.mdpi.com/books |

## FAO 出版物（开放获取，多为 CC BY-NC-SA 3.0 IGO）

| 书名 | 年 | 页 | 许可 | 全文 | 目录 | 来源 |
|---|---|---|---|---|---|---|
| Solar energy and the cold chain | 2025 | 200 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Solar_Energy_and_the_Cold_Chain_2025.txt` | `toc/fao/Solar_Energy_and_the_Cold_Chain_2025.md` | https://www.fao.org/3/cd5864en/cd5864en.pdf |
| Precision fermentation | 2025 | 68 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Precision_Fermentation_2025.txt` | `toc/fao/Precision_Fermentation_2025.md` | https://www.fao.org/3/cd4448en/cd4448en.pdf |
| Reducing food loss and waste in processing, distribution and retail of MSMEs | 2024 | 98 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Reducing_Food_Loss_Waste_MSME_Processing_2024.txt` | `toc/fao/Reducing_Food_Loss_Waste_MSME_Processing_2024.md` | https://www.fao.org/3/cd3803en/cd3803en.pdf |
| Fish silage production by fermentation | 2024 | 30 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Fish_Silage_Production_by_Fermentation_2024.txt` | `toc/fao/Fish_Silage_Production_by_Fermentation_2024.md` | https://www.fao.org/3/cd0799en/cd0799en.pdf |
| Production of high-value products from by-products of aquatic food processing | 2024 | 48 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/High_Value_Products_By_Products_Aquatic_Food_2024.txt` | `toc/fao/High_Value_Products_By_Products_Aquatic_Food_2024.md` | https://www.fao.org/3/cd3041en/cd3041en.pdf |
| Good packaging practices for micro, small and medium-sized food processing enterprises | 2024 | 92 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Good_Packaging_Practices_MSME_2024.txt` | `toc/fao/Good_Packaging_Practices_MSME_2024.md` | https://www.fao.org/3/cd0605en/cd0605en.pdf |
| Plant-based food products, precision fermentation and 3D food printing | 2024 | 120 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Plant_Based_Precision_Fermentation_3D_Food_Printing_2024.txt` | `toc/fao/Plant_Based_Precision_Fermentation_3D_Food_Printing_2024.md` | https://www.fao.org/3/cd2430en/cd2430en.pdf |
| Sustainable food cold chains: Opportunities, challenges and the way forward | 2022 | 122 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Sustainable_Food_Cold_Chains_2022.txt` | `toc/fao/Sustainable_Food_Cold_Chains_2022.md` | https://www.fao.org/3/cc0923en/cc0923en.pdf |
| The FAO-Thiaroye Processing Technique (FTT) | 2021 | 79 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Thiaroye_Processing_Technique_FTT_2021.txt` | `toc/fao/FAO_Thiaroye_Processing_Technique_FTT_2021.md` | https://www.fao.org/3/cb3299en/cb3299en.pdf |
| Policy measures for micro, small and medium food processing enterprises | 2015 | 290 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Policy_Measures_MSME_Food_Processing_2015.txt` | `toc/fao/Policy_Measures_MSME_Food_Processing_2015.md` | https://www.fao.org/3/i4299e/i4299e.pdf |
| Technical and investment guidelines for milk cooling centres | 2015 | 118 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Milk_Cooling_Centres_Guidelines_2015.txt` | `toc/fao/Milk_Cooling_Centres_Guidelines_2015.md` | https://www.fao.org/3/i5791e/i5791e.pdf |
| Appropriate food packaging solutions for developing countries | 2014 | 38 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Appropriate_Food_Packaging_Solutions_Developing_Countries_2014.txt` | `toc/fao/Appropriate_Food_Packaging_Solutions_Developing_Countries_2014.md` | https://www.fao.org/3/i3684e/i3684e.pdf |
| Technical guide to fish canning | 2013 | 79 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Technical_Guide_to_Fish_Canning_2013.txt` | `toc/fao/Technical_Guide_to_Fish_Canning_2013.md` | https://www.fao.org/3/bb214e/bb214e.pdf |
| By-products of tuna processing | 2013 | 55 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/By_Products_of_Tuna_Processing_2013.txt` | `toc/fao/By_Products_of_Tuna_Processing_2013.md` | https://www.fao.org/3/bb215e/bb215e.pdf |
| Guide to small scale trout processing methods | 2012 | 22 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Guide_Small_Scale_Trout_Processing_2012.txt` | `toc/fao/Guide_Small_Scale_Trout_Processing_2012.md` | https://www.fao.org/3/ap342en/ap342en.pdf |
| Processing for Prosperity | 2011 | 110 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Processing_for_Prosperity_2011.txt` | `toc/fao/Processing_for_Prosperity_2011.md` | https://www.fao.org/3/i2468e/i2468e.pdf |
| Value from Village Processing | 2011 | 111 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Value_from_Village_Processing_2011.txt` | `toc/fao/Value_from_Village_Processing_2011.md` | https://www.fao.org/3/i2467e/i2467e.pdf |
| Traditional fermented food and beverages for improved livelihoods | 2011 | 86 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Traditional_Fermented_Food_Beverages_Livelihoods_2011.txt` | `toc/fao/Traditional_Fermented_Food_Beverages_Livelihoods_2011.md` | https://www.fao.org/3/i2477e/i2477e.pdf |
| Preserving green leafy vegetables and fruits | 2011 | 4 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Preserving_Green_Leafy_Vegetables_and_Fruits_2011.txt` | `toc/fao/Preserving_Green_Leafy_Vegetables_and_Fruits_2011.md` | https://www.fao.org/3/ca2556en/ca2556en.pdf |
| Processing of fresh-cut tropical fruits and vegetables: A technical guide | 2010 | 102 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Processing_Fresh_Cut_Tropical_Fruits_Vegetables_2010.txt` | `toc/fao/Processing_Fresh_Cut_Tropical_Fruits_Vegetables_2010.md` | https://www.fao.org/3/i1909e/i1909e.pdf |
| Agribusiness Handbook: Sunflower Crude and Refined Oils | 2010 | 41 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Agribusiness_Handbook_Sunflower_Oils_2010.txt` | `toc/fao/Agribusiness_Handbook_Sunflower_Oils_2010.md` | https://www.fao.org/3/al375e/al375e.pdf |
| Agribusiness Handbook: Fruit and Vegetable Processing | 2009 | 93 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Agribusiness_Handbook_Fruit_Vegetable_Processing_2009.txt` | `toc/fao/Agribusiness_Handbook_Fruit_Vegetable_Processing_2009.md` | https://www.fao.org/3/al177e/al177e.pdf |
| Agribusiness Handbook: Milk / Dairy Products | 2009 | 49 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Agribusiness_Handbook_Milk_Dairy_Products_2009.txt` | `toc/fao/Agribusiness_Handbook_Milk_Dairy_Products_2009.md` | https://www.fao.org/3/al179e/al179e.pdf |
| Milk Testing and Payment Systems | 2009 | 89 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Milk_Testing_and_Payment_Systems_2009.txt` | `toc/fao/Milk_Testing_and_Payment_Systems_2009.md` | https://www.fao.org/3/i0980e/i0980e.pdf |
| Agribusiness Handbook: Red Meat | 2009 | 55 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Agribusiness_Handbook_Red_Meat_2009.txt` | `toc/fao/Agribusiness_Handbook_Red_Meat_2009.md` | https://www.fao.org/3/al178e/al178e.pdf |
| On-farm post-harvest management of food grains | 2009 | 70 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/On_Farm_Post_Harvest_Management_Food_Grains_2009.txt` | `toc/fao/On_Farm_Post_Harvest_Management_Food_Grains_2009.md` | https://www.fao.org/3/i0959e/i0959e.pdf |
| Meat processing technology for small- to medium-scale producers | 2007 | 470 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Meat_Processing_Technology_Small_Medium_Producers_2007.txt` | `toc/fao/Meat_Processing_Technology_Small_Medium_Producers_2007.md` | https://www.fao.org/3/ai407e/ai407e.pdf |
| FAO/WHO guidance to governments on the application of HACCP in small/less-developed businesses | 2007 | 84 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_WHO_HACCP_Small_Businesses_2007.txt` | `toc/fao/FAO_WHO_HACCP_Small_Businesses_2007.md` | https://www.fao.org/3/a0799e/a0799e.pdf |
| Fruit Processing Toolkit: Dried Fruit | 2007 | 13 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Fruit_Processing_Toolkit_Dried_Fruit_2007.txt` | `toc/fao/FAO_Fruit_Processing_Toolkit_Dried_Fruit_2007.md` | https://www.fao.org/3/au111e/au111e.pdf |
| Fruit Processing Toolkit: Preservatives | 2007 | 8 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Fruit_Processing_Toolkit_Preservatives_2007.txt` | `toc/fao/FAO_Fruit_Processing_Toolkit_Preservatives_2007.md` | https://www.fao.org/3/au117e/au117e.pdf |
| Cereals Processing Toolkit: Breads | 2007 | 20 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Cereals_Processing_Toolkit_Breads_2007.txt` | `toc/fao/FAO_Cereals_Processing_Toolkit_Breads_2007.md` | https://www.fao.org/3/au108e/au108e.pdf |
| Cereals Processing Toolkit: Lactic Fermentation | 2007 | 5 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Cereals_Processing_Toolkit_Lactic_Fermentation_2007.txt` | `toc/fao/FAO_Cereals_Processing_Toolkit_Lactic_Fermentation_2007.md` | https://www.fao.org/3/au107e/au107e.pdf |
| Cereals Processing Toolkit: Noodles | 2007 | 7 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Cereals_Processing_Toolkit_Noodles_2007.txt` | `toc/fao/FAO_Cereals_Processing_Toolkit_Noodles_2007.md` | https://www.fao.org/3/au109e/au109e.pdf |
| Milk Processing Toolkit: Milk | 2007 | 6 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Milk_Processing_Toolkit_Milk_2007.txt` | `toc/fao/FAO_Milk_Processing_Toolkit_Milk_2007.md` | https://www.fao.org/3/au136e/au136e.pdf |
| Meat Processing Toolkit: Pork | 2007 | 19 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Meat_Processing_Toolkit_Pork_2007.txt` | `toc/fao/FAO_Meat_Processing_Toolkit_Pork_2007.md` | https://www.fao.org/3/au130e/au130e.pdf |
| Meat Processing Toolkit: Poultry | 2007 | 23 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Meat_Processing_Toolkit_Poultry_2007.txt` | `toc/fao/FAO_Meat_Processing_Toolkit_Poultry_2007.md` | https://www.fao.org/3/au131e/au131e.pdf |
| Meat Processing Toolkit: Products Formulation | 2007 | 11 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Meat_Processing_Toolkit_Products_Formulation_2007.txt` | `toc/fao/FAO_Meat_Processing_Toolkit_Products_Formulation_2007.md` | https://www.fao.org/3/au132e/au132e.pdf |
| Roots and Tubers Processing Toolkit: Cassava Starch | 2007 | 4 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Roots_Tubers_Processing_Toolkit_Cassava_Starch_2007.txt` | `toc/fao/FAO_Roots_Tubers_Processing_Toolkit_Cassava_Starch_2007.md` | https://www.fao.org/3/au142e/au142e.pdf |
| Sugar Processing Toolkit: Sugarcane Syrup | 2007 | 3 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/FAO_Sugar_Processing_Toolkit_Sugarcane_Syrup_2007.txt` | `toc/fao/FAO_Sugar_Processing_Toolkit_Sugarcane_Syrup_2007.md` | https://www.fao.org/3/au155e/au155e.pdf |
| On-farm mycotoxin control in food and feed grain: Training manual | 2007 | 45 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/On_Farm_Mycotoxin_Control_Food_Feed_Grain_2007.txt` | `toc/fao/On_Farm_Mycotoxin_Control_Food_Feed_Grain_2007.md` | https://www.fao.org/3/a1417e/a1417e.pdf |
| Small mills in Africa | 2006 | 34 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Small_Mills_in_Africa_2006.txt` | `toc/fao/Small_Mills_in_Africa_2006.md` | https://www.fao.org/3/j8482e/j8482e.pdf |
| Freezing of fruits and vegetables | 2005 | 76 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Freezing_of_Fruits_and_Vegetables_2005.txt` | `toc/fao/Freezing_of_Fruits_and_Vegetables_2005.md` | https://www.fao.org/3/y5979e/y5979e.pdf |
| Good practices for the meat industry | 2004 | 322 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Good_Practices_for_the_Meat_Industry_2004.txt` | `toc/fao/Good_Practices_for_the_Meat_Industry_2004.md` | https://www.fao.org/3/y5454e/y5454e.pdf |
| Handling and preservation of fruits and vegetables by combined methods for rural areas | 2003 | 8 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Handling_Preservation_Fruits_Vegetables_Combined_Methods_2003.txt` | `toc/fao/Handling_Preservation_Fruits_Vegetables_Combined_Methods_2003.md` | https://www.fao.org/3/y4358e/y4358e.pdf |
| Small-scale palm oil processing in Africa | 2002 | 59 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Small_Scale_Palm_Oil_Processing_Africa_2002.txt` | `toc/fao/Small_Scale_Palm_Oil_Processing_Africa_2002.md` | https://www.fao.org/3/y4355e/y4355e.pdf |
| Principles and practices of small- and medium-scale fruit juice processing | 2001 | 221 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Principles_Practices_Small_Medium_Fruit_Juice_Processing_2001.txt` | `toc/fao/Principles_Practices_Small_Medium_Fruit_Juice_Processing_2001.md` | https://www.fao.org/3/y2515e/y2515e.pdf |
| Food quality and safety systems: A training manual on food hygiene and HACCP | 1998 | 178 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Food_Quality_Safety_Systems_HACCP_Training_Manual_1998.txt` | `toc/fao/Food_Quality_Safety_Systems_HACCP_Training_Manual_1998.md` | https://www.fao.org/3/w8088e/w8088e.pdf |
| Small-scale poultry processing | 1992 | 124 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Small_Scale_Poultry_Processing_1992.txt` | `toc/fao/Small_Scale_Poultry_Processing_1992.md` | https://www.fao.org/3/t0561e/t0561e.pdf |
| Manual on fish canning | 1988 | 79 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Manual_on_Fish_Canning_1988.txt` | `toc/fao/Manual_on_Fish_Canning_1988.md` | https://www.fao.org/3/t0007e/t0007e.pdf |
| Quality control in fruit and vegetable processing | 1988 | 72 | © FAO（开放获取，多为 CC BY-NC-SA 3.0 IGO） | `text/fao/Quality_Control_Fruit_Vegetable_Processing_1988.txt` | `toc/fao/Quality_Control_Fruit_Vegetable_Processing_1988.md` | https://www.fao.org/3/t0029e/t0029e.pdf |

## 公共领域 / 历史经典（Archive.org）

| 书名 | 年 | 页 | 许可 | 全文 | 目录 | 来源 |
|---|---|---|---|---|---|---|
| Text-book of Meat Hygiene | 1939 | 484 | Public Domain | `text/public_domain/Text_Book_of_Meat_Hygiene_1939.txt` | `toc/public_domain/Text_Book_of_Meat_Hygiene_1939.md` | https://archive.org/details/textbookofmeathy00edelrich |
| Dairy Chemistry: A Practical Handbook | 1920 | 512 | Public Domain | `text/public_domain/Dairy_Chemistry_1920.txt` | `toc/public_domain/Dairy_Chemistry_1920.md` | https://archive.org/details/dairychemistrypr00richrich |
| Drying Vegetables and Fruits for Home Use | 1919 | 28 | Public Domain | `text/public_domain/Drying_Vegetables_and_Fruits_for_Home_Use_1919.txt` | `toc/public_domain/Drying_Vegetables_and_Fruits_for_Home_Use_1919.md` | https://archive.org/details/dryingvegetables00lund |
| Home and Farm Food Preservation | 1918 | 314 | Public Domain | `text/public_domain/Home_and_Farm_Food_Preservation_1918.txt` | `toc/public_domain/Home_and_Farm_Food_Preservation_1918.md` | https://archive.org/details/homefarmfoodpres00crue |
| Successful Canning and Preserving | 1917 | 412 | Public Domain | `text/public_domain/Successful_Canning_and_Preserving_1917.txt` | `toc/public_domain/Successful_Canning_and_Preserving_1917.md` | https://archive.org/details/successfulcannin00powe |
| Bread Making and Bread Baking | 1915 | 136 | Public Domain | `text/public_domain/Bread_Making_and_Bread_Baking_1915.txt` | `toc/public_domain/Bread_Making_and_Bread_Baking_1915.md` | https://archive.org/details/breadmakingbread00brot |
| A Treatise on Flour, Yeast, Fermentation and Baking | 1914 | 132 | Public Domain | `text/public_domain/Treatise_on_Flour_Yeast_Fermentation_and_Baking_1914.txt` | `toc/public_domain/Treatise_on_Flour_Yeast_Fermentation_and_Baking_1914.md` | https://archive.org/details/treatiseonfloury00wilh |
| Leavening Agents: Yeast, Leaven, Salt-rising Fermentation, Baking Powder | 1914 | 116 | Public Domain | `text/public_domain/Leavening_Agents_1914.txt` | `toc/public_domain/Leavening_Agents_1914.md` | https://archive.org/details/leaveningagentsy00hartrich |
| Canning and Preserving of Food Products with Bacteriological Technique | 1905 | 478 | Public Domain | `text/public_domain/Canning_and_Preserving_of_Food_Products_1905.txt` | `toc/public_domain/Canning_and_Preserving_of_Food_Products_1905.md` | https://archive.org/details/canningpreservin00duckrich |
| The Art of Canning and Preserving as an Industry | 1900 | 224 | Public Domain | `text/public_domain/The_Art_of_Canning_and_Preserving_as_an_Industry_1900.txt` | `toc/public_domain/The_Art_of_Canning_and_Preserving_as_an_Industry_1900.md` | https://archive.org/details/artofcanningpres00pacrrich |
| The Preservation of Fishery Products for Food | 1899 | 254 | Public Domain | `text/public_domain/Preservation_of_Fishery_Products_for_Food_1899.txt` | `toc/public_domain/Preservation_of_Fishery_Products_for_Food_1899.md` | https://archive.org/details/preservationoffi00stev |
| The Complete Confectioner, Pastry-Cook and Baker | 1846 | 164 | Public Domain | `text/public_domain/The_Complete_Confectioner_Pastry_Cook_and_Baker_1846.txt` | `toc/public_domain/The_Complete_Confectioner_Pastry_Cook_and_Baker_1846.md` | https://archive.org/details/completeconfecti00parkrich |

---
*由食品加工专家维护；新增电子书请更新 `sources_*.json` 后运行 `python3 tools/make_index.py` 重建索引。*
