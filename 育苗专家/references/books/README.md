# 育苗电子书库 · 开放获取书目

> 本目录由**育苗专家**维护，收录**合法开放获取（CC BY / OA）**的种子萌发、种子处理、组织培养与微繁、扦插/压条/嫁接、设施育苗、基质与壮苗、食用菌菌种繁育等专著。
> 全部为可自由下载的原版全文，许可为 **CC BY（MDPI）**；使用与再分发请遵守授权（署名原作者/出版社）。
> 更新日期：2026-10-07 ｜ 共计 **14 册**，约 **577 MB**。

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

## 一、如何使用（给育苗专家）

```bash
# 全文检索（多词 AND，返回 书|页码|原文）
python3 references/books/tools/search_books.py "germination" --context 1
python3 references/books/tools/search_books.py "micropropagation" --books      # 各书命中统计
python3 references/books/tools/search_books.py "TDZ" --book Advancement        # 限定某书
# 命中页码后，按页读取原文
python3 references/books/tools/read_page.py Plant_Biostimulants 80
```

- 检索到要点后，读取 `toc/mdpi/<书名>.md` 定位章节，再到 `text/mdpi/<书名>.txt` 对应页码附近取原文引用。
- 引用格式：`编者/作者. 书名. MDPI, 年份. 许可: CC BY. 页码.`

**要点沉淀**：原著定量证据已逐条沉淀到 `references/证据条目与出处.md`（按主题分节 + 表格条目，标注书库页码），与种植/发酵/食品加工专家同构。

## 二、书目（MDPI Books，CC BY，14 册）

| 书名 | 年 | 主题 |
|---|---|---|
| Seed Germination and Micropropagation of Ornamental Plants | 2024 | 种子萌发、微繁 |
| Seed Priming Approaches That Achieve Environmental Stress Tolerance | 2024 | 种子引发、壮苗、抗逆 |
| Innovative Micropropagation of Horticultural and Medicinal Plants | 2025 | 组培快繁、脱毒、药用植物 |
| Plant Tissue Culture and Plant Somatic Embryogenesis | 2025 | 组织培养、体细胞胚胎 |
| Plant Genetic Resources In Vitro Culture | 2024 | 离体培养、种质保存 |
| Propagation and Flowering of Ornamental Plants | 2026 | 扦插繁殖、种子休眠、花期 |
| Advancement in Propagation, Breeding, Cultivation and Marketing of Ornamentals | 2024 | 繁殖、基质、嫁接、设施 |
| Protected Cultivation of Horticultural Crops | 2025 | 设施育苗、环境调控 |
| Advances in Propagation and Cultivation of Mushroom | 2026 | 食用菌菌种繁育、栽培料 |
| Plant Biostimulants in Sustainable Horticulture and Agriculture | 2024 | 生物刺激素、壮苗、种子包衣 |
| Vegetable Genetics and Genomics | 2025 | 蔬菜、嫁接育苗 |
| Vegetable Genomics and Breeding Research | 2026 | 蔬菜、育种 |
| Advances in Research for Horticultural Crops Breeding and Genetics | 2025 | 园艺作物、育种 |
| Soil Quality and Innovation in Agriculture | 2025 | 基质、土壤质量 |

## 三、许可与合规

- **MDPI**：**CC BY 4.0（署名）**，可自由阅读、下载、再分发与改编，**署名原作者/出版社**即可。
- 引用时请署名原作者与出版社，并保留来源 DOI/URL（见 `catalog.json` 与 `INDEX.md`）。
- 仅收录开放获取资源，不含商业版权教材；商业权威教材请通过正规渠道获取。

---
*本索引由育苗专家维护。新增电子书后运行 `python3 tools/build_booklib.py . <manifest.json>` 重建。*
