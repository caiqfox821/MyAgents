# 育种电子书库 · 开放获取书目

> 本目录由**育种专家**维护，收录**合法开放获取（CC BY）**的种质资源、分子/数量遗传、QTL/GWAS、MAS/基因组选择、基因编辑、抗病抗逆与品质育种、果树/蔬菜/食用菌/药用植物育种等专著。
> 全部为可自由下载的原版全文（**MDPI Books, CC BY**）；使用与再分发请署名原作者/出版社。
> 更新日期：2026-10-07 ｜ 共计 **16 册**，**3990 页**，约 **718 MB**。

## 目录结构

```
books/
├── mdpi/            MDPI Books 开放获取全书（CC BY，可自由再分发）
├── text/mdpi/       每本书的可检索纯文本（pdftotext 生成，按页 \f 分隔）
├── toc/mdpi/        每本书的自动目录（Contents / Chapters）
├── tools/           检索与编目工具（search_books / read_page / build_booklib）
├── catalog.json     结构化元数据（标题/年/页/许可/来源/标签/目录）
├── INDEX.md         全文索引（主题标签 + 书目表）
└── README.md        本文件
```

## 一、如何使用（给育种专家）

```bash
# 全文检索（多词 AND，返回 书|页码|原文）
python3 references/books/tools/search_books.py "QTL" "LOD" --context 1
python3 references/books/tools/search_books.py "marker-assisted selection" --books
python3 references/books/tools/search_books.py "CRISPR" --book Tomato          # 限定某书
# 命中页码后，按页读取原文
python3 references/books/tools/read_page.py Advances_in_Crop_Molecular_Breeding 85
```

- 检索到要点后，读取 `toc/mdpi/<书名>.md` 定位章节，再到 `text/mdpi/<书名>.txt` 对应页码附近取原文引用。
- 引用格式：`编者/作者. 书名. MDPI, 年份. 许可: CC BY. 页码.`

**要点沉淀**：原著定量证据已逐条沉淀到 `references/证据条目与出处.md`（按主题分节 + 表格条目，标注书库页码），与种植/发酵/食品加工/育苗专家同构。

## 二、书目（MDPI Books，CC BY，16 册）

| 书名 | 年 | 主题 |
|---|---|---|
| Advances in Crop Molecular Breeding and Genetics | 2025 | QTL/GWAS/MAS/MABC/CRISPR/配合力 |
| QTL Mapping of Seed Quality Traits in Crops | 2025 | 种子品质 QTL |
| Crop Functional Genomics and Biological Breeding | 2025 | 功能基因组、生物育种 |
| Crop Functional Genomics and Biological Breeding (2nd Ed.) | 2026 | 功能基因组、生物育种 |
| Research on Plant Genomics and Breeding | 2025 | 植物基因组与育种 |
| Research on Plant Genomics and Breeding 2023 | 2025 | 植物基因组与育种 |
| Molecular Breeding and Genetics Research in Plants | 2025 | 分子育种与遗传 |
| Genes, Genetics and Breeding of Tomato | 2025 | 番茄遗传育种 |
| Genetics and Molecular Breeding of Fruit Tree Species | 2025 | 果树分子育种 |
| Advances in Molecular Breeding of Vegetable Crops | 2022 | 蔬菜分子育种 |
| Genetics and Breeding of Edible Mushroom | 2025 | 食用菌遗传育种 |
| Phylogenetics, Genetics, and Breeding of Medicinal Plants | 2024 | 药用植物遗传育种 |
| Advances in Research for Horticultural Crops Breeding and Genetics | 2025 | 园艺作物育种 |
| Berry Crops Production: Cultivation, Breeding and Health Benefits | 2025 | 小浆果育种 |
| Molecular Mechanisms in Plant Stress Tolerance | 2026 | 抗逆分子机制 |
| Molecular Mechanisms Associated with Plant Tolerance upon Abiotic Stress | 2025 | 非生物胁迫分子机制 |

## 三、许可与合规

- **MDPI**：**CC BY 4.0（署名）**，可自由阅读、下载、再分发与改编，**署名原作者/出版社**即可。
- 引用时请署名原作者与出版社，并保留来源 DOI/URL（见 `catalog.json` 与 `INDEX.md`）。
- 仅收录开放获取资源，不含商业版权教材；商业权威教材（如 Falconer、Hallauer 等）请通过正规渠道获取。

---
*本索引由育种专家维护。新增电子书后运行 `python3 tools/build_booklib.py . <manifest.json>` 重建。*
