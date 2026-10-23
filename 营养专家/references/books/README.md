# 营养专家电子书库 · 开放获取书目

> 本目录由**营养专家**维护，收录**合法开放获取（Open Access）**的营养、膳食与慢病营养专著/指南/报告的全文 PDF。
> 许可：**MDPI = CC BY 4.0**（可自由再分发）；**WHO = 开放获取，多为 CC BY-NC-SA 3.0 IGO**（署名-非商业-相同方式共享）。
> 更新日期：2026-10-20 ｜ 已收录 **MDPI 99 册 + WHO 123 篇 = 222 册/篇**（含全文文本 211 份）。
> ⚠️ **仅收录开放获取资源**，不含任何商业版权教材的盗版副本；引用与再利用请遵守各来源许可。

## 目录结构

```
books/
├── mdpi/            MDPI Books 开放获取全书（CC BY 4.0）
├── who/             WHO 指南/报告（开放获取，CC BY-NC-SA 3.0 IGO）
├── text/<分区>/     每本书的可检索纯文本（pdftotext -layout 生成，按页 \f 分隔）
├── toc/<分区>/      每本书的自动目录（Contents / Chapters）
├── tools/           发现/下载/检索/编目工具
│   ├── discover_mdpi.py  MDPI 书目发现（Crossref REST → reprint id）
│   ├── curate_mdpi.py    人类营养主题筛选与打标
│   ├── discover_who.py   WHO IRIS（DSpace 7 REST）指南发现 + PDF 直链解析
│   ├── fetch_fao.py      FAO 出版物下载（doc_id 直链）
│   ├── fetch_papers.py   PAPERS/EuropePMC 开放获取文献抓取
│   ├── build_booklib.py  下载（完整性校验+断点续传）+ 全文抽取 + 编目
│   ├── search_books.py   全文检索（多词 AND，返回 书|页码|原文）
│   └── read_page.py      按页读原文
├── sources_mdpi.json     MDPI 书源清单（id/标题/年/标签）
├── sources_mdpi_raw.json MDPI 全量发现结果（317 册，未筛选）
├── sources_who.json      WHO 指南清单（uuid/标题/年/pdf_url/来源）
├── catalog.json          结构化元数据（标题/年/页/许可/标签/目录/全文路径）
└── INDEX.md              全文索引（主题标签 + 分区书目表）
```

## 一、如何使用（给营养专家）

```bash
# 全文检索（多词 AND，返回 书|页码|原文）
python3 references/books/tools/search_books.py "Mediterranean diet" --context 1
python3 references/books/tools/search_books.py "sodium intake" --books          # 各书命中统计
python3 references/books/tools/search_books.py "recommend" --book who           # 仅在 WHO 分区内检索
# 命中页码后按页读原文
python3 references/books/tools/read_page.py Guideline_sodium_intake_for_adults_and_children 10
python3 references/books/tools/read_page.py Mediterranean_Diet_on_Metabolic 52
```

- 检索到要点后，读 `toc/<分区>/<书名>.md` 定位章节，再到 `text/...txt` 对应页码取原文。
- 引用格式：`编者/机构. 书名或指南名. 出版社/WHO, 年份. 许可. 书库 p.N.`

## 二、收录范围

- **MDPI（99 册，CC BY 4.0）**：人类营养与膳食、慢病营养（肥胖/糖尿病/代谢与心血管/肿瘤/肝肾）、微量营养素与维生素 D、母婴与儿童营养、老年与肌少症、肠道菌群、补剂与功能成分、营养流行病与公共卫生、膳食模式与摄入、运动营养等。
- **WHO（123 篇，开放获取）**：膳食与慢病指南（钠/钾/糖/脂肪/碳水/非糖甜味剂/低钠盐替代品/财政政策）、微量营养素补充与食品强化（维 A/铁/锌/钙/MNP/面粉强化）、母婴与婴幼儿喂养、肥胖综合管理、身体活动、学校营养、营养不良管理等。

## 三、许可与合规

- **MDPI**：CC BY 4.0，署名即可自由使用、再分发与改编。
- **WHO**：多为 CC BY-NC-SA 3.0 IGO，署名 WHO 且非商业使用、相同方式共享。
- 引用建议：`WHO. Guideline: … 年份. 许可. 获取自 https://iris.who.int/handle/…`

## 四、重建流程

```bash
python3 tools/discover_mdpi.py      # 发现 MDPI 书目（→ sources_mdpi_raw.json）
python3 tools/curate_mdpi.py        # 主题筛选与打标（→ sources_mdpi.json）
python3 tools/discover_who.py       # 发现 WHO 指南与 PDF 直链（→ sources_who.json）
python3 tools/build_booklib.py . sources_mdpi.json sources_who.json --jobs 4
python3 tools/fetch_papers.py --max 10     # PAPERS/EuropePMC 文献 + 全文
```

> 免责：书目元数据（年份、页数）以出版商/机构页面为准；本索引用于内部检索，指南推荐、剂量与结论请回归原文与现行标准核验。

---
*本索引由营养专家维护。新增电子书请在此登记，并注明来源与许可。*
