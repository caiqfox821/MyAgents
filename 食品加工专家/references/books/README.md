# 食品加工电子书库 · 开放获取书目

> 本目录由**食品加工专家**维护，收录**合法开放获取（Open Access / 公共领域）**的食品加工、食品工程、单元操作、包装、货架期、品类加工与功能配料专著/技术手册 PDF。
> 全部为可自由下载的原版全文，许可为 **CC BY（MDPI）**、**开放获取（FAO）** 或 **公共领域（Archive.org）**；使用与再分发请遵守各书授权（见「许可与合规」）。
> 更新日期：2026-10-07 ｜ 共计 **118 册/篇**（MDPI 56 + FAO 50 + 公共领域 12），约 **1.8 GB**，**20,816 页**；年代跨度 1846–2026。

## 目录结构

```
books/
├── mdpi/            MDPI Books 开放获取全书（CC BY，可自由再分发）
├── fao/             FAO 开放获取出版物/技术手册（多为 CC BY-NC-SA 3.0 IGO）
├── public_domain/   公共领域 / 历史经典（Archive.org，含 OCR 全文）
├── text/<分区>/     每本书的可检索纯文本（pdftotext 生成，按页 \f 分隔）
├── toc/<分区>/      每本书的自动目录（Contents / Chapters）
├── tools/           检索与编目工具（search_books / read_page / make_index / fetch_*）
├── sources_mdpi.json          MDPI 书源清单（id / 标题 / 标签 / 年份）
├── sources_fao.json           FAO 书源清单（doc_id / 标题 / 标签 / 年份）
├── sources_public_domain.json 公共领域书源清单
├── catalog.json               结构化元数据（标题/年/页/许可/标签/目录）
└── INDEX.md                   全文索引（主题标签 + 分区书目表）
```

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

- 检索到要点后，读取 `toc/<分区>/<书名>.md` 定位章节，再到 `text/...txt` 对应页码附近取原文引用。
- 引用格式：`编者/作者. 书名. 出版社, 年份. 许可: CC BY. 页码.`

**要点沉淀**：各主题的"书库对应资源 + 书库强化要点 + 检索式"已沉淀到 `references/` 五份知识文件的 **"书库对应资源（电子书库沉淀）"** 小节：
`加工单元操作.md`、`配方设计与稳定体系.md`、`货架期与包装.md`、`中试放大与产线.md`、`标准规范与法规-食品加工.md`。

## 二、MDPI Books（56 册，CC BY，可自由再分发）

主题覆盖：工艺工程与过程优化、热加工与非热加工（HPP/PEF/超声/微波/冷等离子）、干燥、膜分离、包装与涂膜、货架期、谷物与烘焙、乳品、肉与水产、植物蛋白、食品胶体与凝胶、多糖淀粉、功能食品与营养强化、纳米技术、食品废弃物高值化、分析检测与风味。完整书单见 `INDEX.md`。

## 三、FAO 出版物（50 册/篇，开放获取）

FAO 是发展中国家小规模食品加工最重要的技术来源，侧重实用手册与工具箱（Processing Toolkit），主题覆盖：食品加工通则与中小企业、果蔬加工/保藏/冷冻/鲜切、乳品冷却与加工、水产罐藏/烟熏（FTT）/发酵/副产物高值化、肉品加工与屠宰、谷物制粉与采后、油脂加工（棕榈/葵花）、薯类淀粉、糖加工、发酵食品、包装、冷链、HACCP 与食品安全、精密发酵与 3D 食品打印等。

## 四、公共领域 / 历史经典（12 册，Archive.org）

涵盖罐藏保藏（1900–1917）、果蔬干燥（1919）、水产保藏（1899）、乳品化学（1920）、烘焙与膨松剂（1846–1915）、肉品卫生（1939）等，用于追溯工艺原理与技术演进。

## 五、许可与合规

- **MDPI**：CC BY 4.0（署名）授权，可自由阅读、下载、再分发与改编，**署名原作者/出版社**即可。
- **FAO**：多为 **CC BY-NC-SA 3.0 IGO**（署名-非商业-相同方式共享），可自由阅读、下载、非商业再分发；引用与再利用请署名 FAO 并遵守其条款。
- **公共领域**：出版年代久远或已进入公共领域，可自由使用；Archive.org 扫描件请保留出处说明。
- 本库**仅收录开放获取资源**，不含任何商业版权教材的盗版副本。
- 引用建议格式：`编者/机构. 书名. 出版社, 年份. 许可. 获取自 <DOI/URL>`。

## 六、商业权威教材（仅推荐，需购买/图书馆借阅）

以下为食品加工领域公认权威，**未下载**（受版权保护），建议通过图书馆或正规渠道获取：

| 书名 | 作者/出版社 | 定位 |
|---|---|---|
| *Food Processing Technology: Principles and Practice* | P. Fellows, Woodhead | 食品加工技术标准教材 |
| *Introduction to Food Engineering* | Singh & Heldman, Academic Press | 食品工程与单元操作经典 |
| *Handbook of Food Engineering* | Heldman & Lund, CRC Press | 食品工程手册 |
| *Food Science* | Norman Potter & Hotchkiss, Springer | 食品科学导论经典 |
| *Principles of Food Sanitation* | Marriott et al., Springer | 食品卫生与清洗 |
| *Fennema's Food Chemistry* | Damodaran & Parkin, CRC Press | 食品化学权威 |
| 《食品工艺学》《食品工程原理》 | 国内高校教材（无锡江南大学/中国农大版） | 中文核心教材 |
| 《食品化学》《食品微生物学》 | 国内高校教材 | 中文基础教材 |

## 七、来源与核验

- MDPI Books：`https://www.mdpi.com/books`（CC BY，PDF 直链 `https://mdpi-res.com/bookfiles/...`）
- FAO：`https://openknowledge.fao.org`（FAO Knowledge Repository，PDF 直链 `https://www.fao.org/3/<id>/<id>.pdf`）
- Archive.org：公共领域扫描件 `https://archive.org/details/<id>`
- 检索入口：DOAB `https://directory.doabooks.org`、OAPEN `https://library.oapen.org`、OpenAlex `https://api.openalex.org`
- 维护：新增书目后更新 `sources_*.json`，执行 `python3 tools/make_index.py` 重建 `catalog.json`/`INDEX.md`/`toc/`。

> 免责：书目元数据（年份、版次、页数）以出版商页面为准；本索引用于内部检索，工艺参数、限量与结论请回归原书与现行标准核验。

---
*本索引由食品加工专家维护。新增电子书请在此登记，并注明来源与许可。*
