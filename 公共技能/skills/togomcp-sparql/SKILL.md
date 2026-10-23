---
name: togomcp-sparql
description: TogoMCP / RDF Portal 生命科学知识图谱查询技能。用于规范查询 47 个 RDF 数据库（MediaDive 培养基、BacDive 菌株、BRENDA 酶、MassBank 质谱、ChEBI/PubChem 化合物、LIPID MAPS/SwissLipids 脂质、UniProt/PDB/Reactome 蛋白与通路、Taxonomy 分类、TogoID ID 转换等）。覆盖图钉选、MIE schema 读取、SPARQL 编写、静默失败陷阱规避与大结果集 bulk 模式。当需要培养基配方、菌株特性、酶学参数、参考质谱图、化合物结构、代谢/通路、分类学或跨库 ID 转换时加载。
---

# TogoMCP / RDF Portal SPARQL 查询技能

## 何时使用

- 需要 **MediaDive / BacDive / BRENDA / MassBank / ChEBI / PubChem / UniProt** 等库里的**实测数据**，而不是文献里的定性描述。
- 需要**跨库联表**：如「化合物名 → InChIKey → 参考谱图 → 所属通路」。
- 需要**ID 转换**（TogoID）或名称→标识符归一化。

不适用：只要综述性结论时用文献检索工具；只要标准条文时查「公共知识/标准规范」。

## 五条硬规则（违反会**静默**出错）

1. **每条 SPARQL 必须钉住图（graph）** —— 用 `FROM <http://rdfportal.org/dataset/<库key>>`。
   多个库**共用一个端点**，不钉图会**不报错**地返回错误值或膨胀行数。这是最危险的坑。
2. **写查询前先读 schema** —— `get_MIE_file(database="<key>")`。
   MIE 文件含该库**实时**的 graph 列表、前缀定义、静默失败陷阱与**已被验证的示例查询**（含期望行数/首行值）。**照抄其示例比自创安全**。
3. **连续 `run_sparql` ≤ 2 次**；任何非 SPARQL 调用（含 `get_MIE_file`）后计数清零。不要把 SPARQL 当循环用。
4. **先限定再取数**：先 `COUNT` 或 `LIMIT` 试探，不要直接拉全表；单查询约 **60 s** 上限。
5. **1000 行以上或规模未知 → bulk 模式**（分批 + 落盘脚本），避免超时和上下文爆炸；交互式提问不要用文件系统工具，直接 `run_sparql`。

## 工作流

1. **判定问题类型**：有界（要一个具体事实）→ 直接查；探索性（规模未知）→ 先 `COUNT` / 取样。
2. **选库**（见下表）→ 得到 `key` 与端点名。
3. **`get_MIE_file`** → 读 graph、前缀、陷阱、verified 示例。
4. **写最小查询**：`PREFIX` + `FROM` + 双重过滤（分类锚点 + 字面量或 IRI）→ `LIMIT`。
5. **`run_sparql(database=..., sparql_query=...)`**。
6. **校验**：用 `COUNT` 与 MIE 里的 documented count 对账；返回 **0 行**时先怀疑：图没钉 / 类名大小写 / 字面量 vs IRI。

### 查询骨架

```sparql
PREFIX <本体前缀>: <本体IRI>
SELECT ?x ?label
FROM <http://rdfportal.org/dataset/<库key>>
WHERE {
  ?x a <类IRI> ;              # ① 分类锚点：把搜索空间钉到该库该类型
     <谓词> ?label .          # ② 目标谓词
  FILTER(...)                 # ③ 必要时过滤（注意字面量 vs IRI）
}
LIMIT 20
```

## 库选择速查（问什么 → 用哪个 key）

| 要查什么 | key | 端点 |
|---|---|---|
| 微生物**培养基配方/成分** | `mediadive` | primary |
| **菌株**表型、培养条件、分类 | `bacdive` | primary |
| **酶**、EC 号、动力学参数 | `brenda` | primary |
| **参考质谱图**（真实谱图、峰、SPLASH） | `massbank` | primary |
| 化合物/代谢物**本体与结构** | `chebi` | ebi |
| 化合物**结构检索**（子结构/相似性） | `idsm` | idsm |
| 化合物记录（CID） | `pubchem` | pubchem |
| **脂质** | `lipidmaps` ・ `swisslipids` | lipidmaps ・ swisslipids |
| 蛋白/序列/功能 | `uniprot` ・ `pdb` | sib ・ pdb |
| 蛋白组实验/鉴定 | `jpostdb` | primary |
| 反应 / 通路 | `rhea` ・ `reactome` ・ `wikipathways` ・ `go` | sib ・ ebi ・ wikipathways ・ primary |
| 基因 / 变异 / 表型 | `ensembl` ・ `ncbigene` ・ `hgnc` ・ `clinvar` ・ `togovar` | ebi ・ ncbi ・ primary ・ ncbi ・ togovar |
| 疾病 / 表型本体 | `mondo` ・ `nando` ・ `medgen` ・ `mesh` | primary ・ primary ・ ncbi ・ primary |
| 分类学（Taxonomy） | `taxonomy` | primary |
| 抗菌药抗性 | `amrportal` | ebi |
| 微生物资源/保藏号 | `nbrc` ・ `bh26microbes` | primary ・ microbes |
| 糖链（Glycoscience） | `glycosmos` | glycosmos |
| 植物 | `marpolbase` | marpolbase |
| 表达谱 | `bgee` | sib |
| 直系同源 | `oma` | sib |
| GWAS | `gwascatalog` | ebi |
| 文献 / 实体共现 | `pubmed` ・ `pubtator` | ncbi |
| 超二级结构 | `supercon` | nims |
| 序列归档 | `ddbj` | ddbj |

> `primary` 端点被 **20 个库**共占（bacdive、mediadive、brenda、massbank、hgnc、jpostdb、nbrc、mogplus、hco、mco、ontology、fantabio、pubcasefinder、jogo、tismed、mesh、go、taxonomy、mondo、nando），**用它的库必须钉图**。
> 图 URI 统一为 `http://rdfportal.org/dataset/<key>`；**唯一例外：`lipidmaps` 无命名图**（不要 `FROM`）。
> 有些库**有关键词检索工具**（如 `search_uniprot_entity`、`search_pdb_entity`、`search_mesh_descriptor`、`search_chembl_molecule/target`、OLS4 的 `searchClasses` 等），优先用它把**名称换成 ID**，再进 SPARQL。
> **MediaDive / BacDive / BRENDA / MassBank / LIPID MAPS 没有关键词搜索工具**，只能 `get_MIE_file` + `run_sparql`。不要猜 dataset key。

## 已验证示例（2026-10-18 实测可跑）

### 1) MediaDive：培养基总数
```sparql
PREFIX schema: <https://purl.dsmz.de/schema/>
SELECT (COUNT(DISTINCT ?m) AS ?n)
FROM <http://rdfportal.org/dataset/mediadive>
WHERE { ?m a schema:Medium . }
```
→ `3291`（文档口径约 3289，随数据更新漂移属正常）

### 2) MediaDive：同时含两种指定成分的培养基（AND 组合）
```sparql
PREFIX schema: <https://purl.dsmz.de/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?medium ?label
FROM <http://rdfportal.org/dataset/mediadive>
WHERE {
  ?c1 schema:partOfMedium ?medium ; schema:containsIngredient <https://purl.dsmz.de/mediadive/ingredient/16> .
  ?c2 schema:partOfMedium ?medium ; schema:containsIngredient <https://purl.dsmz.de/mediadive/ingredient/5> .
  ?medium rdfs:label ?label .
}
ORDER BY ?label
LIMIT 30
```
→ 30 行（如 "1/10 PYGV MEDIUM modified"）。每个成分重复一段即可做 AND。

### 3) BRENDA：某 EC 号下的酶与来源生物
```sparql
PREFIX d3o: <https://purl.dsmz.de/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?enzyme ?orgLabel
FROM <http://rdfportal.org/dataset/brenda>
WHERE {
  ?enzyme d3o:isClassifiedAs <https://purl.dsmz.de/brenda/ec/1.1.1.1> ;
          d3o:foundIn ?organism .
  ?organism rdfs:label ?orgLabel .
}
LIMIT 3
```
→ `https://purl.dsmz.de/brenda/enzyme/248` ← "Rattus norvegicus Mn-SOD" 等

### 4) MassBank：按 **InChIKey** 反查参考谱图（未知物鉴定核心）
```sparql
PREFIX mb: <http://www.massbank.jp/ontology/>
PREFIX schema: <https://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?spectrum ?title ?npeaks
FROM <http://rdfportal.org/dataset/massbank>
WHERE {
  ?spectrum a mb:MassSpectrum ;
            mb:compound ?c ;
            skos:definition ?title ;
            mb:pk_num_peak ?npeaks .
  ?c schema:inChIKey <http://identifiers.org/inchikey/PTGXAUBQBSGPKF-UHFFFAOYSA-N> .
}
LIMIT 5
```
→ 5 张 Nylidrin 谱图（不同仪器/碰撞能），如 `MSBNK-HBM4EU-HB002729` 47 峰

### 5) MassBank：按 accession 读一条记录的结构
```sparql
PREFIX mb: <http://www.massbank.jp/ontology/>
PREFIX schema: <https://schema.org/>
SELECT ?formula ?mass ?inchikey ?smiles
FROM <http://rdfportal.org/dataset/massbank>
WHERE {
  <https://identifiers.org/massbank/MSBNK-HBM4EU-HB000204> mb:compound ?c .
  ?c schema:molecularFormula ?formula ;
     mb:ch_exact_mass ?mass ;
     schema:smiles ?smiles .
  OPTIONAL { ?c schema:inChIKey ?inchikey }
}
```
→ 1 行（Nylidrin）

## 静默失败陷阱清单（务必照抄，别凭直觉改）

**通用**
- 图未钉 → 静默错误/膨胀（头号杀手）。
- **类型不要泛化**：字面量写成 IRI、IRI 写成字符串，都返回 0 行不报错。
- `regex()` 每个分支要加括号，并带 flags 参数，否则静默 0 行。

**MediaDive**
- `schema:` 展开为 **DSMZ 私有本体** `https://purl.dsmz.de/schema/`，**不是 schema.org**。
- 每个培养基**同时**被记为 `schema:Medium` 与 `schema:CultureMedium`。
- 与 `bacdive` 共端点：同用 DSMZ 类但 IRI 不重叠，正常不会串行。
- 成分路线：`?component schema:partOfMedium ?medium ; schema:containsIngredient <ingredient IRI>`。

**BRENDA**
- 前缀写 **`d3o:`**（同一个 DSMZ 本体），**不要**写成 `schema:`。
- 常用：`d3o:isClassifiedAs`（指向 EC）、`d3o:foundIn`（指向生物）。

**MassBank**
- 这里的 `schema:` 才是**真 schema.org**（https）。
- 化学物质类必须**全小写**：`<https://schema.org/chemicalsubstance>`；写成 `schema:ChemicalSubstance` → **0 行**。
- `schema:inChIKey` 是 **IRI**，且是 **http 不是 https**：`<http://identifiers.org/inchikey/KEY>`；当字符串匹配 → 0 行。
- 谱图 → 化合物用 `mb:compound`；谱名用 `skos:definition`（人读标题，可多值）。
- `mb:pk_num_peak`（xsd:integer）、`mb:pk_splash`（结构无关谱哈希）。
- **MassBank 没有"名称→IRI"索引**：要按化合物名找谱图，先用 ChEBI/PubChem/ChEMBL 把名称换成 InChIKey，再走上面的结构锚定路线。
- `COUNT(?c)` 数的是**谱图**不是分子；分子去重用 `COUNT(DISTINCT ?inchikey)`（= **17,921** 个独特分子）。
- 覆盖率参考：InChIKey 98.81%、CAS 69.63%、PubChem CID 55.32% —— 任意药样清单命中率低是**设计使然**，不是查询错误。

## 跨库联表与 ID 转换（TogoID）

- 化合物联表走 **InChIKey**，各方复用同一套 IRI `<http://identifiers.org/inchikey/KEY>` 可直接 join：
  `http://rdfportal.org/dataset/togoid/relation/{pubchem_compound | chebi | chembl_compound | hmdb}-inchi_key`
- 一般 ID 转换优先用 TogoID 工具（`togoid_convert` 等），不要手写多跳 join。

## 结果校验（交付前必做）

1. **`COUNT` 对账**：与 MIE 文档中的 documented count 比对，数量级一致才可信。
2. **首行 sanity check**：核对 MIE 里 `verified.has_values` / `first_row`。
3. **0 行三查**：图钉了吗？类名大小写对吗？字面量 vs IRI 对吗？
4. **行数异常大**：多半是图没钉，被同端点的其他库串进来了。
5. 交付时**注明库名与检索日期**；涉及生物活性/限量结论时提示"以实验测定/现行标准为准"。
