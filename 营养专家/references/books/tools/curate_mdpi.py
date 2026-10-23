#!/usr/bin/env python3
"""从 sources_mdpi_raw.json 筛出「人类营养 / 膳食与慢病」主题书目 -> sources_mdpi.json"""
import json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw = json.load(open(os.path.join(ROOT, "sources_mdpi_raw.json"), encoding="utf-8"))

# 排除：动/植物/土壤/矿物/地质/水产饲料等非「人类营养」对象
BLOCK = re.compile(r"\b(animal|fish|shellfish|rumen|ruminant|poultry|swine|pig|calf|calves|"
                   r"cattle|feedlot|forage|silage|soil|plant nutrition|plant nutrient|fertiliz|"
                   r"crop|cropping|mineral exploration|mineral processing|ore|gold|granitoid|"
                   r"porphyry|igneous|hydrometallurg|rock|geolog|water buffalo|equine|canine|"
                   r"feline|beef|broiler|aquacultur|eel|shrimp|rubber|elastomer|photocatal|"
                   r"battery|electric vehicle|lubricat|nanomaterial|nanostructure|crystal|"
                   r"semiconductor|biomedical imaging|implant|surgery|aneurysm|electrophysiolog|"
                   r"mycos|gram-negative|dentistry|periodontitis|toxicolog|imaging|"
                   r"echocardiograph|computed tomography|molecular pharmacology|"
                   r"iron nutrition in plants|hemodialysis|waste reduction|food sustainab|"
                   r"body image|medicinal plant|phytochemical composition of plants|"
                   r"food processing industry)\b", re.I)

KEEP = re.compile(r"nutrition|diet|nutrient|vitamin|micronutri|obes|diabet|metabolic syndrome|"
                  r"sarcopen|malnutri|eating|dietary|mediterranean|nutraceutical|functional food|"
                  r"bioactive|food supplement|body composition|hypertension|hypercholesterol|"
                  r"cardiovascular|glycemic|cancer patient|chronic disease|clinical nutrition|"
                  r"nutritional status|nutritional assessment|healthy ageing|healthy aging|"
                  r"micronutrient intake|infant|pediatric|premature|preterm|maternal|pregnan|"
                  r"adolescen|older adult|elderly|bone health|gut microbiome|weight loss|"
                  r"food security|amino acid supplementation|risk of type 2 diabetes", re.I)

TAG = [
    (r"obes|weight loss|body composition|overweight", "肥胖/体重管理"),
    (r"diabet|glyc|insulin", "糖尿病"),
    (r"metabolic|cadiovascular|cardiovascular|hypertension|hypercholesterol|lipid|cholesterol|fatty acid", "代谢与心血管"),
    (r"cancer|oncolog|anticancer", "肿瘤营养"),
    (r"vitamin|micronutri|mineral|selenium|zinc|iron|calcium|folate|iodine", "微量营养素"),
    (r"dietary pattern|diet|eating|mediterranean|vegetarian|dietary habit|dietary intake|food environment|food security", "膳食模式/摄入"),
    (r"sport|exercise|muscle|sarcopen|physical performance|physical activity|performance|training", "运动/肌少症"),
    (r"infant|pediatric|preterm|premature|maternal|pregnan|fetal|neonate|growth|adolescen|child", "母婴/儿童"),
    (r"aging|ageing|elder|older|geriatric|age-related", "老年营养"),
    (r"gut|microbiom|probiotic|prebiotic|gastro|digestion|digestive", "肠道/菌群"),
    (r"supplement|nutraceutical|functional food|bioactive|antioxidant|phytochemic|plant extract|natural product", "补剂/功能成分"),
    (r"epidemiolog|public health|health outcome|behavior|behaviour|quality of life|social determinant", "公共卫生/行为"),
    (r"immune|inflamm", "免疫/炎症"),
    (r"bone|osteopor", "骨骼营养"),
    (r"liver|renal|kidney|chronic disease|clinical nutrition|nutritional assessment", "临床营养"),
    (r"gene|epigenet|interaction", "基因-膳食"),
]


def tags_for(t):
    ts = [tag for pat, tag in TAG if re.search(pat, t, re.I)]
    return ts or ["营养综合"]


keep = []
for e in raw:
    t = e["title"]
    if BLOCK.search(t):
        continue
    if not KEEP.search(t):
        continue
    e["tags"] = tags_for(t)
    e["sub"] = "mdpi"
    e["publisher"] = "MDPI"
    e["license"] = "CC BY 4.0"
    e["source"] = f"https://doi.org/{e['doi']}"
    keep.append(e)

keep.sort(key=lambda x: (-(x["year"] or 0), x["title"]))
json.dump(keep, open(os.path.join(ROOT, "sources_mdpi.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("curated", len(keep))
for e in keep:
    print(f"  {e['id']:>6} {e['year']} {e['title'][:66]}  {e['tags']}")
