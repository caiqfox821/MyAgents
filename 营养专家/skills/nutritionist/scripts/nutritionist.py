import sys
import json
import os
import math
import tempfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Micro Hei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

MODES = ("met", "macro", "meal", "body")

KCAL_PER_G = {"protein": 4, "carbs": 4, "fat": 9}

GUIDELINES = {
    "cn_2022": {
        "label": "中国居民膳食指南 2022",
        "carbs_pct": (50, 65),
        "protein_pct": (10, 20),
        "fat_pct": (20, 30),
    },
    "us_dga_2025": {
        "label": "美国膳食指南 DGA 2025–2030",
        "carbs_pct": (45, 65),
        "protein_pct": (10, 35),
        "fat_pct": (20, 35),
    },
}

ACTIVITY_PROTEIN = {
    "sedentary": (0.8, 1.0),
    "low": (1.0, 1.2),
    "moderate": (1.2, 1.5),
}

ACTIVITY_MET_CUTOFFS = {
    "sedentary": (0, 500),
    "low": (500, 1000),
    "moderate": (1000, float("inf")),
}

WHO_PA = "WHO guidelines on physical activity and sedentary behaviour (2020)"
WHO_MET_MIN_WEEK = {"minimal": 500, "optimal": 1000}
WHO_MIN = 500
WHO_OPT = 1000

COMMON_METS = {
    "散步": 2.5, "慢走": 2.5, "walking": 2.5,
    "快走": 5.0, "brisk walking": 5.0, "brisk_walking": 5.0,
    "慢跑": 9.2, "jogging": 9.2,
    "跑步": 10.0, "running": 10.0,
    "骑行": 6.0, "cycling": 6.0, "biking": 6.0,
    "游泳": 8.0, "swimming": 8.0,
    "瑜伽": 2.5, "yoga": 2.5,
    "力量训练": 5.0, "weight training": 5.0, "strength": 5.0,
    "椭圆机": 6.0, "elliptical": 6.0,
    "HIIT": 8.0, "hiit": 8.0,
    "太极": 3.0, "tai chi": 3.0, "taichi": 3.0,
    "跳绳": 10.0, "jump rope": 10.0, "skipping": 10.0,
    "爬山": 7.0, "hiking": 7.0,
    "跳舞": 4.5, "dancing": 4.5,
    "羽毛球": 5.5, "badminton": 5.5,
    "篮球": 6.5, "basketball": 6.5,
    "足球": 7.0, "football": 7.0, "soccer": 7.0,
    "乒乓球": 4.0, "table tennis": 4.0,
    "网球": 6.0, "tennis": 6.0,
    "拉伸": 2.0, "stretching": 2.0,
    "普拉提": 3.0, "pilates": 3.0,
}

SPEED_MET = {
    "3": 2.5, "4": 2.9, "5": 3.5, "6": 5.0,
    "7": 9.2, "8": 10.5, "9": 11.8, "10": 13.0,
    "3km/h": 2.5, "4km/h": 2.9, "5km/h": 3.5, "6km/h": 5.0,
    "7min/km": 9.2, "6min/km": 10.5, "5min/km": 11.8, "4min/km": 13.0,
}

FOOD_NUTRITION = {
    "鸡胸肉":   {"protein": 23, "carbs": 0,  "fat": 1.2,  "unit": "100g"},
    "鸡蛋":     {"protein": 13, "carbs": 1.5, "fat": 9,   "unit": "100g"},
    "牛奶":     {"protein": 3.0, "carbs": 4.8, "fat": 3.6, "unit": "100ml"},
    "豆腐":     {"protein": 8.1, "carbs": 3.0, "fat": 3.7, "unit": "100g"},
    "牛肉(瘦)": {"protein": 20, "carbs": 0,  "fat": 4.2,  "unit": "100g"},
    "猪肉(瘦)": {"protein": 20, "carbs": 0,  "fat": 6.2,  "unit": "100g"},
    "三文鱼":   {"protein": 20, "carbs": 0,  "fat": 13,   "unit": "100g"},
    "虾仁":     {"protein": 18, "carbs": 0,  "fat": 0.8,  "unit": "100g"},
    "糙米":     {"protein": 2.8, "carbs": 26, "fat": 0.6, "unit": "100g"},
    "白米饭":   {"protein": 2.6, "carbs": 28, "fat": 0.3, "unit": "100g"},
    "全麦面包": {"protein": 9,  "carbs": 49, "fat": 3.4,  "unit": "100g"},
    "燕麦":     {"protein": 13, "carbs": 66, "fat": 6.5,  "unit": "100g"},
    "红薯":     {"protein": 1.6, "carbs": 20, "fat": 0.1, "unit": "100g"},
    "西兰花":   {"protein": 2.8, "carbs": 7,  "fat": 0.4, "unit": "100g"},
    "菠菜":     {"protein": 2.9, "carbs": 3.6, "fat": 0.4, "unit": "100g"},
    "橄榄油":   {"protein": 0,  "carbs": 0,  "fat": 100,  "unit": "100ml"},
    "香蕉":     {"protein": 1.1, "carbs": 23, "fat": 0.3, "unit": "100g"},
    "苹果":     {"protein": 0.3, "carbs": 14, "fat": 0.2, "unit": "100g"},
    "白米粥":   {"protein": 1.0, "carbs": 10, "fat": 0.1, "unit": "100g"},
    "肉包子":   {"protein": 8.0, "carbs": 28, "fat": 5.0, "unit": "100g"},
    "绿豆沙":   {"protein": 4.0, "carbs": 25, "fat": 2.0, "unit": "100g"},
    "青菜":     {"protein": 1.5, "carbs": 3.0, "fat": 0.2, "unit": "100g"},
    "可乐":     {"protein": 0,   "carbs": 10.6, "fat": 0,   "unit": "100ml"},
    "豆腐干":   {"protein": 16,  "carbs": 4.0, "fat": 8.0, "unit": "100g"},
    "馒头":     {"protein": 7.0, "carbs": 45,  "fat": 1.0, "unit": "100g"},
    "无糖酸奶": {"protein": 3.5, "carbs": 5.0, "fat": 3.0, "unit": "100ml"},
    "宫保鸡丁": {"protein": 18,  "carbs": 8.0, "fat": 8.0, "unit": "100g"},
    "木耳炒鸡蛋":{"protein": 10,  "carbs": 3.0, "fat": 7.0, "unit": "100g"},
    "芹菜炒豆干":{"protein": 8.0, "carbs": 5.0, "fat": 5.0, "unit": "100g"},
    "带鱼":     {"protein": 18,  "carbs": 0,   "fat": 5.0, "unit": "100g"},
    "拿铁":     {"protein": 3.0, "carbs": 4.0, "fat": 2.0, "unit": "100ml"},
    "红豆面包": {"protein": 7.0, "carbs": 50,  "fat": 5.0, "unit": "100g"},
    "红烧猪肉": {"protein": 14,  "carbs": 3.0, "fat": 28,   "unit": "100g"},
    "茄子":     {"protein": 1.0, "carbs": 5.0, "fat": 0.2, "unit": "100g"},
    "辣椒":     {"protein": 1.5, "carbs": 5.0, "fat": 0.3, "unit": "100g"},
    "空心菜":   {"protein": 2.5, "carbs": 3.0, "fat": 0.3, "unit": "100g"},
    "河虾":     {"protein": 16,  "carbs": 0,   "fat": 1.5, "unit": "100g"},
    "红烧排骨": {"protein": 16,  "carbs": 3.0, "fat": 15,  "unit": "100g"},
    "丝瓜":     {"protein": 1.0, "carbs": 4.0, "fat": 0.2, "unit": "100g"},
    "生菜":     {"protein": 1.4, "carbs": 2.9, "fat": 0.2, "unit": "100g"},
    "西红柿":   {"protein": 0.9, "carbs": 3.9, "fat": 0.2, "unit": "100g"},
    "玉米":     {"protein": 4.0, "carbs": 22,  "fat": 1.2, "unit": "100g"},
    "红烧肉":   {"protein": 14,  "carbs": 3.0, "fat": 20,  "unit": "100g"},
    "鱼":       {"protein": 18,  "carbs": 0,   "fat": 5.0, "unit": "100g"},
    "咸菜":     {"protein": 1.5, "carbs": 4.0, "fat": 0.5, "unit": "100g"},
    "菜包":     {"protein": 6.0, "carbs": 30,  "fat": 3.0, "unit": "100g"},
    "糯米烧卖": {"protein": 5.0, "carbs": 35,  "fat": 6.0, "unit": "100g"},
    "杂粮饭":   {"protein": 3.0, "carbs": 25,  "fat": 0.5, "unit": "100g"},
    "土豆":     {"protein": 2.0, "carbs": 17,  "fat": 0.2, "unit": "100g"},
    "胡萝卜":   {"protein": 1.0, "carbs": 10,  "fat": 0.2, "unit": "100g"},
    "青椒":     {"protein": 1.0, "carbs": 4.0, "fat": 0.3, "unit": "100g"},
    "韭菜":     {"protein": 2.4, "carbs": 4.5, "fat": 0.4, "unit": "100g"},
    "南瓜":     {"protein": 1.0, "carbs": 7.0, "fat": 0.1, "unit": "100g"},
    "美式咖啡": {"protein": 0.1, "carbs": 0,   "fat": 0,   "unit": "100ml"},
    "蛋糕":     {"protein": 4.0, "carbs": 35,  "fat": 12,  "unit": "100g"},
}

# ==================== 体型 / 内脏脂肪 / 性别化营养 ====================
# 数据来源见 SKILL.md 附录；以下阈值均为成人（18–64 岁）常用口径。

SEX_ALIASES = {
    "男": "male", "男性": "male", "male": "male", "m": "male", "man": "male",
    "女": "female", "女性": "female", "female": "female", "f": "female", "woman": "female",
}

# BMI 三套口径：中国官方（性别中立）+ WHO 亚洲行动点 + 日本肥胖学会
BMI_STANDARDS = {
    "cn": {
        "label": "中国成人（WS/T 428—2013；肥胖症诊疗指南 2024）",
        "low": 18.5, "normal_hi": 24.0, "overweight_hi": 28.0,
    },
    "who_asia": {"label": "WHO 亚洲人群行动点", "overweight": 23.0, "obese": 27.5},
    "japan": {"label": "日本肥胖学会 JASSO", "obese": 25.0},
}

# 与白人 BMI 25 / 30 等危时的中国人 BMI 值（Obesity 2015, n=30 万级）
# fat = 同体脂率口径；risk = 同代谢风险（体脂+脂肪分布）口径
BMI_EQUIVALENT = {
    "male": {"fat": (23.0, 27.9), "risk": (22.5, 25.9)},
    "female": {"fat": (24.4, 32.5), "risk": (22.8, 26.6)},
}

# 腰围切点（cm）：前期 / 中心型肥胖
WAIST_STANDARDS = {
    "cn": {"male": (85.0, 90.0), "female": (80.0, 85.0)},
    "japan": {"male": (85.0, 85.0), "female": (90.0, 90.0)},
    "whtr": 0.5,
}

# 体脂率（%）：男 >25 / 女 >30 为体脂过多（肥胖症诊疗指南 2024）
# nwo = 亚洲人“正常体重肥胖”体脂阈值（系统评价 meta 分析）
BODY_FAT_STANDARDS = {
    "male": {"essential": (3.0, 5.0), "normal": (10.0, 20.0), "high": (20.0, 25.0),
             "obese": 25.0, "nwo": 20.6},
    "female": {"essential": (8.0, 12.0), "normal": (18.0, 28.0), "high": (28.0, 30.0),
               "obese": 30.0, "nwo": 33.4},
}

# 内脏脂肪：VFA（CT/MRI 金标准）、VFL（生物电阻抗体脂秤等级）
VISCERAL_STANDARDS = {
    "vfa_normal": 100.0, "vfa_high": 150.0, "vfa_cn_ref": 80.0,
    "vfl_normal": 9.0, "vfl_high": 14.0,
}

# 中国人内脏脂肪指数 CVAI（Xia et al. 2016）
CVAI_COEF = {
    "male": {"const": -267.93, "age": 0.68, "bmi": 0.03, "wc": 4.00,
             "lgtg": 22.00, "hdl": -16.32, "cutoff": 101.80},
    "female": {"const": -187.32, "age": 1.71, "bmi": 4.23, "wc": 1.12,
               "lgtg": 39.76, "hdl": -11.66, "cutoff": 88.42},
}

# 中国居民膳食营养素参考摄入量（2023 版，18–64 岁一般人群，轻身体活动）
DRIS_2023 = {
    "male": {
        "protein_rni": 65, "iron_rni": 12, "zinc_rni": 12, "calcium_rni": 800,
        "va_rni": 770, "fiber_ai": (25, 30), "energy_ref": 2150, "alcohol_max": 25,
    },
    "female": {
        "protein_rni": 55, "iron_rni": 18, "iron_rni_no_menses": 10, "zinc_rni": 8.5,
        "calcium_rni": 800, "va_rni": 660, "fiber_ai": (25, 30),
        "energy_ref": 1700, "alcohol_max": 15,
    },
}

# 身体活动水平系数（PAL），用于 Mifflin-St Jeor 估算能量需要量
PAL_FACTORS = {"sedentary": 1.4, "low": 1.5, "moderate": 1.7, "high": 1.9}

# 微量营养素（每 100g/100ml，估算值；用于达成率参考，非实验室检测）
MICRO_NUTRITION = {
    "鸡胸肉":   {"iron": 0.6, "zinc": 0.5, "calcium": 3,   "fiber": 0.0},
    "鸡蛋":     {"iron": 1.6, "zinc": 1.1, "calcium": 56,  "fiber": 0.0},
    "牛奶":     {"iron": 0.1, "zinc": 0.4, "calcium": 104, "fiber": 0.0},
    "豆腐":     {"iron": 1.9, "zinc": 1.1, "calcium": 138, "fiber": 0.4},
    "牛肉(瘦)": {"iron": 2.8, "zinc": 3.7, "calcium": 9,   "fiber": 0.0},
    "猪肉(瘦)": {"iron": 1.6, "zinc": 2.9, "calcium": 6,   "fiber": 0.0},
    "三文鱼":   {"iron": 0.3, "zinc": 0.4, "calcium": 12,  "fiber": 0.0},
    "虾仁":     {"iron": 0.5, "zinc": 1.0, "calcium": 60,  "fiber": 0.0},
    "豆腐干":   {"iron": 4.9, "zinc": 1.7, "calcium": 300, "fiber": 0.8},
    "鱼":       {"iron": 0.5, "zinc": 0.5, "calcium": 38,  "fiber": 0.0},
    "带鱼":     {"iron": 1.2, "zinc": 0.7, "calcium": 28,  "fiber": 0.0},
    "河虾":     {"iron": 0.6, "zinc": 1.0, "calcium": 60,  "fiber": 0.0},
    "无糖酸奶": {"iron": 0.1, "zinc": 0.4, "calcium": 118, "fiber": 0.0},
    "拿铁":     {"iron": 0.1, "zinc": 0.3, "calcium": 70,  "fiber": 0.0},
    "糙米":     {"iron": 1.1, "zinc": 1.7, "calcium": 11,  "fiber": 0.6},
    "白米饭":   {"iron": 0.2, "zinc": 0.4, "calcium": 3,   "fiber": 0.1},
    "杂粮饭":   {"iron": 0.8, "zinc": 0.6, "calcium": 8,   "fiber": 0.5},
    "全麦面包": {"iron": 2.5, "zinc": 1.8, "calcium": 30,  "fiber": 4.0},
    "燕麦":     {"iron": 4.2, "zinc": 2.6, "calcium": 54,  "fiber": 6.0},
    "红薯":     {"iron": 0.5, "zinc": 0.2, "calcium": 23,  "fiber": 1.6},
    "土豆":     {"iron": 0.8, "zinc": 0.3, "calcium": 8,   "fiber": 1.1},
    "玉米":     {"iron": 1.1, "zinc": 0.9, "calcium": 3,   "fiber": 2.9},
    "西兰花":   {"iron": 1.0, "zinc": 0.4, "calcium": 50,  "fiber": 1.6},
    "菠菜":     {"iron": 2.9, "zinc": 0.85, "calcium": 66, "fiber": 1.7},
    "青菜":     {"iron": 1.2, "zinc": 0.3, "calcium": 90,  "fiber": 1.1},
    "生菜":     {"iron": 0.9, "zinc": 0.3, "calcium": 34,  "fiber": 0.7},
    "空心菜":   {"iron": 2.3, "zinc": 0.3, "calcium": 99,  "fiber": 1.4},
    "韭菜":     {"iron": 1.6, "zinc": 0.4, "calcium": 42,  "fiber": 1.4},
    "西红柿":   {"iron": 0.4, "zinc": 0.1, "calcium": 10,  "fiber": 0.5},
    "青椒":     {"iron": 0.8, "zinc": 0.2, "calcium": 14,  "fiber": 1.4},
    "茄子":     {"iron": 0.5, "zinc": 0.2, "calcium": 24,  "fiber": 1.3},
    "辣椒":     {"iron": 0.8, "zinc": 0.2, "calcium": 37,  "fiber": 2.1},
    "丝瓜":     {"iron": 0.4, "zinc": 0.2, "calcium": 14,  "fiber": 0.6},
    "南瓜":     {"iron": 0.4, "zinc": 0.2, "calcium": 16,  "fiber": 0.8},
    "胡萝卜":   {"iron": 1.0, "zinc": 0.2, "calcium": 32,  "fiber": 1.1},
    "香蕉":     {"iron": 0.4, "zinc": 0.2, "calcium": 7,   "fiber": 1.2},
    "苹果":     {"iron": 0.1, "zinc": 0.05, "calcium": 4,  "fiber": 1.2},
    "橄榄油":   {"iron": 0.0, "zinc": 0.0, "calcium": 1,   "fiber": 0.0},
    "馒头":     {"iron": 1.8, "zinc": 0.7, "calcium": 38,  "fiber": 1.3},
    "白米粥":   {"iron": 0.1, "zinc": 0.1, "calcium": 2,   "fiber": 0.05},
    "肉包子":   {"iron": 1.2, "zinc": 0.9, "calcium": 20,  "fiber": 1.0},
    "菜包":     {"iron": 1.0, "zinc": 0.6, "calcium": 40,  "fiber": 1.2},
    "糯米烧卖": {"iron": 1.0, "zinc": 0.7, "calcium": 15,  "fiber": 0.8},
    "红豆面包": {"iron": 1.5, "zinc": 0.7, "calcium": 30,  "fiber": 1.5},
    "蛋糕":     {"iron": 0.6, "zinc": 0.3, "calcium": 40,  "fiber": 0.5},
    "绿豆沙":   {"iron": 1.0, "zinc": 0.4, "calcium": 20,  "fiber": 1.5},
    "宫保鸡丁": {"iron": 1.0, "zinc": 0.8, "calcium": 15,  "fiber": 0.6},
    "木耳炒鸡蛋": {"iron": 2.0, "zinc": 0.9, "calcium": 45, "fiber": 1.0},
    "芹菜炒豆干": {"iron": 2.5, "zinc": 1.0, "calcium": 120, "fiber": 1.0},
    "红烧猪肉": {"iron": 1.0, "zinc": 1.5, "calcium": 6,   "fiber": 0.2},
    "红烧排骨": {"iron": 1.3, "zinc": 1.8, "calcium": 8,   "fiber": 0.1},
    "红烧肉":   {"iron": 0.9, "zinc": 1.2, "calcium": 5,   "fiber": 0.1},
    "咸菜":     {"iron": 1.5, "zinc": 0.2, "calcium": 60,  "fiber": 0.8},
    "可乐":     {"iron": 0.0, "zinc": 0.0, "calcium": 2,   "fiber": 0.0},
    "美式咖啡": {"iron": 0.0, "zinc": 0.0, "calcium": 2,   "fiber": 0.0},
}

# 内脏脂肪偏高时的营养对策（按证据强度排序，用于报告建议）
VISCERAL_ADVICE = [
    "减重 5%–10%：内脏脂肪下降幅度通常大于皮下脂肪；即使体重只降 3%–5%，肝脏脂肪与内脏脂肪已可改善。",
    "能量缺口 300–500 kcal/日：女性不低于 1200 kcal/日、男性不低于 1400–1500 kcal/日，避免极低热量饮食丢瘦体重。",
    "添加糖 <25 g/日、坚决减少含糖饮料：果糖经肝脏 de novo lipogenesis 直接促进内脏/肝脏脂肪沉积。",
    "主食换成全谷、杂豆、薯类：膳食纤维 25–30 g/日，可降低餐后胰岛素与甘油三酯。",
    "蛋白质 1.2–1.6 g/kg/日：减重期保瘦体重，优先鱼、禽、蛋、豆制品；红肉与加工肉限量。",
    "每周 2 次以上深海鱼（EPA+DHA 0.25–2.0 g/日），用橄榄油、坚果替代饱和脂肪，饱和脂肪 <10%E。",
    "严格限酒：男 ≤25 g、女 ≤15 g 酒精/日；内脏脂肪偏高者建议戒酒（酒精直接增加肝脏脂肪合成）。",
    "运动：中等强度有氧 ≥150 min/周（或高强度 75 min/周）+ 抗阻训练 2 次/周；HIIT 可作为替代。",
    "睡眠 7–9 h、避免夜间进食：睡眠不足与皮质醇升高会选择性增加内脏脂肪。",
]

PROTEIN_MEALS = ["鸡胸肉", "鸡蛋", "牛奶", "豆腐", "牛肉(瘦)", "猪肉(瘦)", "三文鱼", "虾仁", "豆腐干", "鱼"]
DAIRY_FOODS = ["牛奶", "无糖酸奶", "拿铁"]
STAPLES = ["白米饭", "糙米", "燕麦", "红薯"]
VEGGIES = ["西兰花", "菠菜", "青菜", "生菜"]
OTHERS = ["全麦面包", "香蕉", "苹果", "橄榄油"]


def estimate_met(keyword):
    keyword = str(keyword).strip().lower()
    if keyword in COMMON_METS:
        return COMMON_METS[keyword]
    if keyword in SPEED_MET:
        return SPEED_MET[keyword]
    for k, v in COMMON_METS.items():
        if k in keyword or keyword in k:
            return v
    for k, v in SPEED_MET.items():
        if k in keyword or keyword in k:
            return v
    return None


def calc_met(met, weight, minutes):
    met_min = round(met * minutes, 1)
    kcal = round(met * weight * minutes * 3.5 / 200, 1)
    return met_min, kcal


def who_judge(met_min_per_week):
    if met_min_per_week >= WHO_OPT:
        return "达标（最优）"
    elif met_min_per_week >= WHO_MIN:
        return "达标（最低）"
    else:
        return "未达标"


def run_met(params):
    exercises = params.get("exercises", [])
    weight = params.get("weight", 60)
    weekly_activities = params.get("weekly_activities", None)

    if weekly_activities:
        exercises = weekly_activities

    total_met_min = 0.0
    total_kcal = 0.0
    details = []

    for ex in exercises:
        name = ex.get("name", ex.get("运动", ""))
        duration = ex.get("minutes", ex.get("duration", ex.get("分钟", 30)))
        freq = ex.get("frequency", ex.get("freq", ex.get("频次", 1)))
        met = ex.get("met", None)
        if met is None:
            met = estimate_met(name)
        if met is None:
            details.append({
                "name": name, "minutes": duration, "freq": freq,
                "error": f"无法识别运动方式: {name}"
            })
            continue
        single_met_min, single_kcal = calc_met(met, weight, duration)
        total_met_min += single_met_min * freq
        total_kcal += single_kcal * freq
        details.append({
            "name": name, "met": met, "minutes": duration, "freq": freq,
            "met_min_per_session": single_met_min,
            "kcal_per_session": single_kcal,
            "met_min_total": round(single_met_min * freq, 1),
            "kcal_total": round(single_kcal * freq, 1),
        })

    return {
        "mode": "met",
        "weight_kg": weight,
        "total_met_min_per_week": round(total_met_min, 1),
        "total_kcal_per_week": round(total_kcal, 1),
        "who_minimum": WHO_MIN,
        "who_optimal": WHO_OPT,
        "who_judgment": who_judge(total_met_min),
        "details": details,
    }


def get_activity_level(steps):
    if steps < 3000:
        return "sedentary"
    elif steps < 8000:
        return "low"
    else:
        return "moderate"


def met_min_to_activity(met_min_per_week):
    for level, (lo, hi) in ACTIVITY_MET_CUTOFFS.items():
        if lo <= met_min_per_week < hi:
            return level
    return "moderate"


def calc_food(food_name, amount):
    info = FOOD_NUTRITION.get(food_name)
    if not info:
        return None
    factor = amount / 100
    return {
        "protein": round(info["protein"] * factor, 1),
        "carbs": round(info["carbs"] * factor, 1),
        "fat": round(info["fat"] * factor, 1),
    }


def pick_best(items, target_protein, exclude=None, max_amount=400):
    exclude = exclude or []
    candidates = [i for i in items if i not in exclude]
    if not candidates:
        candidates = items
    best = None
    best_diff = float("inf")
    for name in candidates:
        info = FOOD_NUTRITION[name]
        per_100 = info["protein"]
        if per_100 <= 0:
            continue
        amt = round(target_protein / per_100 * 100, 0)
        if amt < 20:
            amt = 20
        if amt > max_amount:
            continue
        actual = per_100 * amt / 100
        diff = abs(actual - target_protein)
        if diff < best_diff:
            best_diff = diff
            best = (name, amt)
    if best is None:
        for name in candidates:
            info = FOOD_NUTRITION[name]
            if info["protein"] <= 0:
                continue
            amt = round(target_protein / info["protein"] * 100, 0)
            amt = min(max(amt, 20), max_amount)
            actual = info["protein"] * amt / 100
            diff = abs(actual - target_protein)
            if best is None or diff < best_diff:
                best_diff = diff
                best = (name, amt)
    return best


def make_rose_chart(data, title, filename):
    labels = list(data.keys())
    sizes = list(data.values())
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    angles = [i / len(labels) * 2 * 3.14159 for i in range(len(labels))]
    angles += angles[:1]
    sizes_plot = sizes + sizes[:1]
    ax.fill(angles, sizes_plot, alpha=0.25)
    ax.plot(angles, sizes_plot, linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title(title, pad=20, fontsize=12)
    plt.tight_layout()
    fig.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close(fig)


def set_cell_text(cell, text, bold=False, font_name="宋体", font_size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(str(text))
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    for run_elem in p.runs:
        run_elem.font.name = font_name


def add_styled_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], h, bold=True, font_size=9)
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            set_cell_text(table.rows[r_idx + 1].cells[c_idx], val, font_size=9)
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Cm(w)
    return table


def new_doc():
    doc = Document()
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(10)
    style.element.rPr.rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", "宋体")
    return doc


def add_bullets(doc, suggestions, font_size=10):
    for s in suggestions:
        p = doc.add_paragraph(s, style="List Bullet")
        for run in p.runs:
            run.font.name = "宋体"
            run.font.size = Pt(font_size)


def output_dir():
    return os.getcwd()


# ==================== 体型 / 内脏脂肪 / 性别化营养 ====================


def norm_sex(value):
    if value is None:
        return None
    return SEX_ALIASES.get(str(value).strip().lower())


def bmi_cn_category(bmi):
    s = BMI_STANDARDS["cn"]
    if bmi < s["low"]:
        return "体重过低"
    if bmi < s["normal_hi"]:
        return "正常体重"
    if bmi < s["overweight_hi"]:
        return "超重"
    return "肥胖"


def bmi_assess(bmi, sex):
    if bmi is None:
        return None
    cn = bmi_cn_category(bmi)
    who = "肥胖" if bmi >= BMI_STANDARDS["who_asia"]["obese"] else (
        "超重" if bmi >= BMI_STANDARDS["who_asia"]["overweight"] else "正常")
    jp = "肥胖" if bmi >= BMI_STANDARDS["japan"]["obese"] else "非肥胖"
    res = {"bmi": bmi, "cn": cn, "who_asia": who, "japan": jp}
    if sex:
        fat_ov, fat_ob = BMI_EQUIVALENT[sex]["fat"]
        risk_ov, risk_ob = BMI_EQUIVALENT[sex]["risk"]
        res["sex"] = sex
        res["fat_equivalent"] = {"overweight": fat_ov, "obese": fat_ob,
                                 "level": "肥胖" if bmi >= fat_ob else (
                                     "超重" if bmi >= fat_ov else "正常")}
        res["risk_equivalent"] = {"overweight": risk_ov, "obese": risk_ob,
                                  "level": "高风险" if bmi >= risk_ob else (
                                      "中风险" if bmi >= risk_ov else "低风险")}
    return res


def waist_assess(waist, sex, height):
    if waist is None:
        return None
    res = {"waist": waist}
    if sex:
        pre, obese = WAIST_STANDARDS["cn"][sex]
        res["cn_level"] = "中心型肥胖" if waist >= obese else (
            "中心型肥胖前期" if waist >= pre else "正常")
        res["cn_cutoffs"] = {"pre": pre, "obese": obese}
        jp_cut = WAIST_STANDARDS["japan"][sex][1]
        res["japan_visceral_suspect"] = waist >= jp_cut
        res["japan_cutoff"] = jp_cut
    if height:
        whtr = round(waist / height, 3)
        res["whtr"] = whtr
        res["whtr_level"] = "超标" if whtr >= WAIST_STANDARDS["whtr"] else "正常"
    return res


def body_fat_assess(bf, sex):
    if bf is None or not sex:
        return None
    st = BODY_FAT_STANDARDS[sex]
    if bf < st["essential"][1]:
        level = "过低（可能影响内分泌）"
    elif bf < st["normal"][1]:
        level = "正常"
    elif bf < st["obese"]:
        level = "偏高"
    else:
        level = "体脂过多"
    return {"body_fat": bf, "level": level, "obese_cut": st["obese"],
            "nwo_cut": st["nwo"], "nwo": bf >= st["nwo"] and bf < st["obese"]}


def cvai_calc(sex, age, bmi, waist, tg, hdl):
    if not sex or None in (age, bmi, waist, tg, hdl):
        return None
    if tg <= 0 or hdl <= 0:
        return None
    c = CVAI_COEF[sex]
    value = (c["const"] + c["age"] * age + c["bmi"] * bmi + c["wc"] * waist
             + c["lgtg"] * math.log10(tg) + c["hdl"] * hdl)
    return round(value, 2)


def visceral_assess(ctx):
    """综合 VFA / VFL / CVAI / 腰围，给出内脏脂肪分级。"""
    sex = ctx.get("sex")
    bmi = ctx.get("bmi")
    waist = ctx.get("waist")
    vfa = ctx.get("vfa")
    vfl = ctx.get("vfl")
    cvai = cvai_calc(sex, ctx.get("age"), bmi, waist, ctx.get("tg"), ctx.get("hdl"))

    items = []
    flags = []
    if vfa is not None:
        if vfa >= VISCERAL_STANDARDS["vfa_high"]:
            level = "高"
        elif vfa >= VISCERAL_STANDARDS["vfa_normal"]:
            level = "偏高"
        else:
            level = "正常"
        items.append(("内脏脂肪面积 VFA", vfa, "cm²", "<100 正常 / 100–150 偏高 / ≥150 高", level))
        if level == "高":
            flags.append("high")
        elif level == "偏高":
            flags.append("mid")
    if vfl is not None:
        if vfl >= VISCERAL_STANDARDS["vfl_high"]:
            level = "高"
        elif vfl >= VISCERAL_STANDARDS["vfl_normal"]:
            level = "偏高"
        else:
            level = "标准"
        items.append(("内脏脂肪等级 VFL", vfl, "级", "1–9 标准 / 10–14 偏高 / ≥15 高", level))
        if level == "高":
            flags.append("high")
        elif level == "偏高":
            flags.append("mid")
    if cvai is not None:
        cutoff = CVAI_COEF[sex]["cutoff"]
        level = "高于参考切点" if cvai >= cutoff else "低于参考切点"
        items.append(("中国人内脏脂肪指数 CVAI", cvai, "", f"参考切点 {cutoff}", level))
        if cvai >= cutoff:
            flags.append("mid")
    if waist is not None and sex:
        pre, obese = WAIST_STANDARDS["cn"][sex]
        if waist >= obese:
            flags.append("mid")
        elif waist >= pre:
            flags.append("mid")

    if "high" in flags:
        overall = "高"
    elif "mid" in flags:
        overall = "偏高"
    elif items:
        overall = "正常"
    else:
        overall = "未评估（缺腰围/内脏脂肪数据）"

    return {"items": items, "overall": overall, "cvai": cvai,
            "visceral_obesity": bool(bmi is not None and bmi >= 25 and vfa is not None
                                     and vfa >= VISCERAL_STANDARDS["vfa_normal"])}


def bmr_mifflin(sex, weight, height, age):
    if not sex or height is None or age is None:
        return None
    base = 10 * weight + 6.25 * height - 5 * age
    return round(base + (5 if sex == "male" else -161), 0)


def energy_estimate(ctx):
    bmr = bmr_mifflin(ctx.get("sex"), ctx.get("weight"), ctx.get("height"), ctx.get("age"))
    if bmr is None:
        return None
    pal = PAL_FACTORS.get(ctx.get("activity_level", "low"), 1.5)
    return {"bmr": bmr, "pal": pal, "eer": round(bmr * pal, 0)}


def gender_targets(ctx):
    """按性别（+年龄）给出营养目标，突出男女差异。"""
    sex = ctx.get("sex")
    if not sex:
        return None
    age = ctx.get("age")
    d = dict(DRIS_2023[sex])
    iron = d["iron_rni"]
    iron_note = "有月经"
    if sex == "female" and age is not None and age >= 50:
        iron = d["iron_rni_no_menses"]
        iron_note = "无月经/绝经后"
    d["iron_target"] = iron
    d["iron_note"] = iron_note
    d["energy_est"] = energy_estimate(ctx)
    d["protein_gkg"] = ACTIVITY_PROTEIN.get(ctx.get("activity_level", "low"), (1.0, 1.2))
    return d


def micro_totals(items):
    """items: [{'name','amount'}] → 微量营养素估算 + 覆盖率。"""
    totals = {"iron": 0.0, "zinc": 0.0, "calcium": 0.0, "fiber": 0.0}
    covered = 0
    for it in items:
        micro = MICRO_NUTRITION.get(it.get("name"))
        if not micro:
            continue
        covered += 1
        factor = it.get("amount", 0) / 100.0
        for k in totals:
            totals[k] += micro[k] * factor
    return {k: round(v, 1) for k, v in totals.items()}, covered, len(items)


def _num(v, nd=1):
    if v is None:
        return "—"
    if isinstance(v, str):
        return v
    return f"{v:.{nd}f}"


def _as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_ctx(params):
    sex = norm_sex(params.get("sex", params.get("gender")))
    weight = _as_float(params.get("weight"))
    height = _as_float(params.get("height"))
    bmi = round(weight / ((height / 100) ** 2), 1) if weight and height else None
    steps = _as_float(params.get("steps"))
    act = _as_float(params.get("activity"))
    if act is not None:
        activity_level = met_min_to_activity(act)
    elif steps is not None:
        activity_level = get_activity_level(steps)
    else:
        activity_level = "low"
    return {
        "sex": sex,
        "age": _as_float(params.get("age")),
        "weight": weight,
        "height": height,
        "bmi": bmi,
        "waist": _as_float(params.get("waist")),
        "hip": _as_float(params.get("hip")),
        "body_fat": _as_float(params.get("body_fat")),
        "vfl": _as_float(params.get("visceral_fat_level")),
        "vfa": _as_float(params.get("visceral_fat_area")),
        "tg": _as_float(params.get("tg")),
        "hdl": _as_float(params.get("hdl")),
        "steps": steps,
        "activity_level": activity_level,
    }


CN_NUM = {"一": "1", "二": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8"}


def build_body_section(doc, ctx, no):
    """插入“体型与内脏脂肪评估”整节，返回综合判定。"""
    n = CN_NUM.get(no, no)
    bmi = ctx.get("bmi")
    ba = bmi_assess(bmi, ctx.get("sex"))
    wa = waist_assess(ctx.get("waist"), ctx.get("sex"), ctx.get("height"))
    bf = body_fat_assess(ctx.get("body_fat"), ctx.get("sex"))
    va = visceral_assess(ctx)

    doc.add_heading(f"{no}、体型与内脏脂肪评估", level=2)

    if ba:
        doc.add_heading(f"{n}.1 BMI 多口径对照（东亚人群）", level=3)
        rows = [["中国成人标准", _num(bmi), "18.5–23.9 正常 / 24.0–27.9 超重 / ≥28.0 肥胖", ba["cn"]]]
        rows.append(["WHO 亚洲行动点", _num(bmi), "23.0 超重 / 27.5 肥胖", ba["who_asia"]])
        rows.append(["日本 JASSO", _num(bmi), "≥25.0 肥胖", ba["japan"]])
        if "fat_equivalent" in ba:
            fe = ba["fat_equivalent"]
            rows.append(["体脂等危口径（分性别）", _num(bmi),
                         f"超重 ≥{fe['overweight']} / 肥胖 ≥{fe['obese']}", fe["level"]])
            re_ = ba["risk_equivalent"]
            rows.append(["代谢风险等危口径（分性别）", _num(bmi),
                         f"中风险 ≥{re_['overweight']} / 高风险 ≥{re_['obese']}", re_["level"]])
        add_styled_table(doc, ["口径", "BMI", "判读区间", "本次判定"], rows, col_widths=[4.4, 1.8, 6.6, 2.8])
        doc.add_paragraph("")

        sex = ctx.get("sex")
        if sex:
            other = "female" if sex == "male" else "male"
            doc.add_paragraph(
                f"性别差异提示：同等 BMI 下女性体脂率通常比男性高 8–10 个百分点，"
                f"按“同体脂率”换算，女性肥胖对应 BMI 约 {BMI_EQUIVALENT['female']['fat'][1]}、"
                f"男性约 {BMI_EQUIVALENT['male']['fat'][1]}，即女性在同一体脂水平下可以对应更高的 BMI；"
                f"但按“同代谢风险”换算两者非常接近（女 {BMI_EQUIVALENT['female']['risk'][1]} / "
                f"男 {BMI_EQUIVALENT['male']['risk'][1]}）。因此女性 BMI 略高不等于风险更低，"
                f"必须同时看腰围与体脂率。官方中国标准（24/28）本身不区分性别。"
            )
            doc.add_paragraph("")

    if wa:
        doc.add_heading(f"{n}.2 腰围与中心型肥胖", level=3)
        rows = [["腰围", f"{_num(wa['waist'])} cm", "中国：男 ≥90 / 女 ≥85 cm 为中心型肥胖", wa.get("cn_level", "—")]]
        if "cn_cutoffs" in wa:
            c = wa["cn_cutoffs"]
            rows.append(["中国分级切点", f"{c['pre']:.0f} / {c['obese']:.0f} cm", "前期 / 中心型肥胖", wa["cn_level"]])
        if "japan_cutoff" in wa:
            rows.append(["日本内脏脂肪型肥胖筛查", f"{wa['japan_cutoff']:.0f} cm",
                         "男 ≥85 / 女 ≥90 cm（与中国相反）",
                         "疑似" if wa["japan_visceral_suspect"] else "未达"])
        if "whtr" in wa:
            rows.append(["腰高比 WHtR", _num(wa["whtr"], 3), "<0.5 正常；≥0.5 提示内脏脂肪偏高", wa["whtr_level"]])
        add_styled_table(doc, ["指标", "数值", "参考", "判定"], rows, col_widths=[3.6, 2.6, 6.8, 2.6])
        doc.add_paragraph("")

    if bf:
        doc.add_heading(f"{n}.3 体脂率", level=3)
        rows = [["体脂率", f"{_num(bf['body_fat'])} %",
                 f"男 >25% / 女 >30% 为体脂过多；亚洲正常体重肥胖阈值 男 {BODY_FAT_STANDARDS['male']['nwo']}% / 女 {BODY_FAT_STANDARDS['female']['nwo']}%",
                 bf["level"]]]
        if bf.get("nwo"):
            rows.append(["正常体重肥胖（NWO）", "是", "BMI 未达肥胖但体脂已超阈值", "需干预"])
        add_styled_table(doc, ["指标", "数值", "参考", "判定"], rows, col_widths=[3.6, 2.6, 6.8, 2.6])
        doc.add_paragraph("")

    doc.add_heading(f"{n}.4 内脏脂肪", level=3)
    if va["items"]:
        def _fmt(val, unit):
            if unit == "cm²":
                return f"{val:.0f} cm²"
            if unit == "级":
                return f"{val:.0f} 级" if float(val).is_integer() else f"{val:.1f} 级"
            return f"{val:.1f}"
        rows = [[name, _fmt(val, unit), ref, level]
                for name, val, unit, ref, level in va["items"]]
        add_styled_table(doc, ["指标", "数值", "参考", "判定"], rows, col_widths=[4.6, 3.0, 5.6, 2.4])
    else:
        p = doc.add_paragraph("未提供腰围、内脏脂肪面积或甘油三酯/HDL-C，无法计算内脏脂肪指标。"
                              "建议补充：腰围（必需）、体脂秤内脏脂肪等级、或体检的 VFA / TG / HDL-C。")
        for run in p.runs:
            run.font.name = "宋体"
            run.font.size = Pt(9)
    doc.add_paragraph("")
    doc.add_heading(f"{n}.5 综合判定", level=3)
    rows = [["内脏脂肪综合分级", va["overall"]],
            ["内脏脂肪型肥胖（BMI≥25 且 VFA≥100 cm²）", "是" if va["visceral_obesity"] else "否/数据不足"]]
    if va["cvai"] is not None:
        rows.append(["CVAI", f"{va['cvai']:.1f}（切点 {CVAI_COEF[ctx['sex']]['cutoff']:.1f}）"])
    add_styled_table(doc, ["项目", "结果"], rows, col_widths=[7.8, 7.8])
    doc.add_paragraph("")
    return va


def build_gender_target_section(doc, ctx, no):
    n = CN_NUM.get(no, no)
    gt = gender_targets(ctx)
    if not gt:
        return None
    doc.add_heading(f"{no}、性别化营养目标与达成", level=2)
    doc.add_heading(f"{n}.1 性别化目标值（DRIs 2023）", level=3)
    return gender_target_table(doc, ctx)


def gender_target_table(doc, ctx):
    gt = gender_targets(ctx)
    if not gt:
        return None
    sex_label = "男" if ctx["sex"] == "male" else "女"
    rows = [
        ["蛋白质 RNI", f"{gt['protein_rni']} g/日", f"{gt['protein_gkg'][0]}–{gt['protein_gkg'][1]} g/kg/日（按活动水平）"],
        ["铁 RNI", f"{gt['iron_target']} mg/日", gt["iron_note"] + ("；女性经期需求显著高于男性" if ctx["sex"] == "female" else "")],
        ["锌 RNI", f"{_num(gt['zinc_rni'])} mg/日", "男性高于女性"],
        ["钙 RNI", f"{gt['calcium_rni']} mg/日", "男女相同；绝经后重点保证"],
        ["维生素 A RNI", f"{gt['va_rni']} μgRAE/日", "男性高于女性"],
        ["膳食纤维 AI", f"{gt['fiber_ai'][0]}–{gt['fiber_ai'][1]} g/日", "男女相同"],
        ["酒精上限", f"≤{gt['alcohol_max']} g/日", "男性上限高于女性（女性体脂高、乙醇分布容积小）"],
    ]
    if gt["energy_est"]:
        rows.insert(0, ["能量需要量（估算）",
                        f"{gt['energy_est']['eer']:.0f} kcal/日",
                        f"BMR {gt['energy_est']['bmr']:.0f} × PAL {gt['energy_est']['pal']}"])
    add_styled_table(doc, ["营养素", f"{sex_label}性目标", "说明"], rows, col_widths=[4.6, 3.4, 7.4])
    doc.add_paragraph("")
    return gt


def run_macro(params):
    name = params.get("name", "未提供")
    gender = params.get("gender", "未提供")
    age = params.get("age", "未提供")
    weight = params["weight"]
    steps = params["steps"]
    target_protein = params["target_protein"]
    foods = params["foods"]

    activity = get_activity_level(steps)
    protein_range = ACTIVITY_PROTEIN[activity]
    protein_rec_low = round(weight * protein_range[0], 1)
    protein_rec_high = round(weight * protein_range[1], 1)

    food_details = []
    totals = {"protein": 0.0, "carbs": 0.0, "fat": 0.0}
    for item in foods:
        res = calc_food(item["name"], item["amount"])
        if res:
            food_details.append({**item, **res})
            for k in totals:
                totals[k] += res[k]
    for k in totals:
        totals[k] = round(totals[k], 1)

    total_kcal = round(
        totals["protein"] * KCAL_PER_G["protein"]
        + totals["carbs"] * KCAL_PER_G["carbs"]
        + totals["fat"] * KCAL_PER_G["fat"],
        2,
    )
    protein_kcal = round(totals["protein"] * KCAL_PER_G["protein"], 1)
    carbs_kcal = round(totals["carbs"] * KCAL_PER_G["carbs"], 1)
    fat_kcal = round(totals["fat"] * KCAL_PER_G["fat"], 1)
    protein_pct = round(protein_kcal / total_kcal * 100, 1) if total_kcal else 0
    carbs_pct = round(carbs_kcal / total_kcal * 100, 1) if total_kcal else 0
    fat_pct = round(fat_kcal / total_kcal * 100, 1) if total_kcal else 0
    carb_protein_ratio = (
        round(totals["carbs"] / totals["protein"], 1) if totals["protein"] else "N/A"
    )

    doc = new_doc()
    p_title = doc.add_heading("个人膳食宏量营养素报告", level=0)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p_title.runs:
        run.font.name = "宋体"
    doc.add_paragraph("")

    doc.add_heading("一、个人基本信息", level=2)
    ctx = build_ctx(params)
    micro, micro_covered, micro_total = micro_totals(foods)
    info_data = [
        ("姓名", str(name)),
        ("性别", str(gender)),
        ("年龄", str(age)),
        ("体重 (kg)", str(weight)),
    ]
    if ctx["height"]:
        info_data.append(("身高 (cm)", str(ctx["height"])))
        info_data.append(("BMI (kg/m²)", str(ctx["bmi"])))
    if ctx["waist"]:
        info_data.append(("腰围 (cm)", str(ctx["waist"])))
    info_data += [
        ("日常步数 (步/日)", str(steps)),
        ("每日蛋白质目标 (g)", str(target_protein)),
    ]
    info_table = doc.add_table(rows=len(info_data), cols=2)
    info_table.style = "Table Grid"
    for i, (k, v) in enumerate(info_data):
        set_cell_text(info_table.rows[i].cells[0], k, bold=True)
        set_cell_text(info_table.rows[i].cells[1], v)
    doc.add_paragraph("")

    va = build_body_section(doc, ctx, "二")

    doc.add_heading("三、食材明细", level=2)
    food_headers = ["食材", "消耗量", "蛋白质 (g)", "碳水 (g)", "脂肪 (g)"]
    food_rows = []
    for fd in food_details:
        food_rows.append([
            fd["name"],
            str(fd["amount"]) + ("g" if FOOD_NUTRITION.get(fd["name"], {}).get("unit") != "100ml" else "ml"),
            fd["protein"],
            fd["carbs"],
            fd["fat"],
        ])
    add_styled_table(doc, food_headers, food_rows)
    doc.add_paragraph("")

    doc.add_heading("四、宏量营养素分析", level=2)
    doc.add_heading("4.1 汇总表", level=3)
    summary_headers = ["营养素", "总重量 (g)", "热量 (kcal)", "供能占比 (%)"]
    summary_rows = [
        ["蛋白质", totals["protein"], protein_kcal, protein_pct],
        ["碳水化合物", totals["carbs"], carbs_kcal, carbs_pct],
        ["脂肪", totals["fat"], fat_kcal, fat_pct],
        ["合计", round(sum(totals.values()), 1), total_kcal, round(protein_pct + carbs_pct + fat_pct, 1)],
    ]
    add_styled_table(doc, summary_headers, summary_rows)
    doc.add_paragraph("")
    ratio_para = doc.add_paragraph()
    ratio_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_ratio = ratio_para.add_run(f"碳水 : 蛋白质重量比 = {carb_protein_ratio} : 1")
    run_ratio.font.name = "宋体"
    run_ratio.font.size = Pt(10)
    doc.add_paragraph("")

    doc.add_heading("4.2 宏量营养素供能占比雷达图", level=3)
    chart1_path = os.path.join(tempfile.gettempdir(), f"nutri_rose_energy_{os.getpid()}.png")
    make_rose_chart(
        {"蛋白质": protein_pct, "碳水化合物": carbs_pct, "脂肪": fat_pct},
        "宏量营养素供能占比 (%)",
        chart1_path,
    )
    doc.add_picture(chart1_path, width=Inches(4.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("")

    doc.add_heading("4.3 摄入宏量营养素质量雷达图", level=3)
    chart2_path = os.path.join(tempfile.gettempdir(), f"nutri_rose_mass_{os.getpid()}.png")
    make_rose_chart(
        {"蛋白质": totals["protein"], "碳水化合物": totals["carbs"], "脂肪": totals["fat"]},
        "摄入宏量营养素质量 (g)",
        chart2_path,
    )
    doc.add_picture(chart2_path, width=Inches(4.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("")

    doc.add_heading("五、基于双指南的膳食结构评估", level=2)
    for key, gl in GUIDELINES.items():
        doc.add_heading(gl["label"], level=3)
        eval_headers = ["营养素", "当前占比 (%)", "推荐区间 (%)", "判定"]
        eval_rows = [
            ["蛋白质", protein_pct, f"{gl['protein_pct'][0]}-{gl['protein_pct'][1]}",
             "合规" if gl["protein_pct"][0] <= protein_pct <= gl["protein_pct"][1] else "偏离"],
            ["碳水化合物", carbs_pct, f"{gl['carbs_pct'][0]}-{gl['carbs_pct'][1]}",
             "合规" if gl["carbs_pct"][0] <= carbs_pct <= gl["carbs_pct"][1] else "偏离"],
            ["脂肪", fat_pct, f"{gl['fat_pct'][0]}-{gl['fat_pct'][1]}",
             "合规" if gl["fat_pct"][0] <= fat_pct <= gl["fat_pct"][1] else "偏离"],
        ]
        add_styled_table(doc, eval_headers, eval_rows)
        doc.add_paragraph("")

    gt = build_gender_target_section(doc, ctx, "六")
    if gt:
        doc.add_heading("6.2 微量营养素估算达成", level=3)
        p_cov = doc.add_paragraph(
            f"覆盖率：{micro_covered}/{micro_total} 种食材有内置微量营养素数据"
            f"（另 {micro_total - micro_covered} 种未覆盖，未计入合计）。以下为估算值，非实验室检测。"
        )
        for run in p_cov.runs:
            run.font.name = "宋体"
            run.font.size = Pt(9)
        rows = []
        protein_target = target_protein
        rows.append(["蛋白质", f"{totals['protein']} g", f"{protein_target} g",
                     f"{round(totals['protein'] / protein_target * 100, 1) if protein_target else 0} %"])
        rows.append(["铁", f"{micro['iron']} mg", f"{gt['iron_target']} mg",
                     f"{round(micro['iron'] / gt['iron_target'] * 100, 1)} %"])
        rows.append(["锌", f"{micro['zinc']} mg", f"{gt['zinc_rni']} mg",
                     f"{round(micro['zinc'] / gt['zinc_rni'] * 100, 1)} %"])
        rows.append(["钙", f"{micro['calcium']} mg", f"{gt['calcium_rni']} mg",
                     f"{round(micro['calcium'] / gt['calcium_rni'] * 100, 1)} %"])
        rows.append(["膳食纤维", f"{micro['fiber']} g", f"{gt['fiber_ai'][0]}–{gt['fiber_ai'][1]} g",
                     "低于下限" if micro["fiber"] < gt["fiber_ai"][0] else "达标"])
        add_styled_table(doc, ["营养素", "估算摄入", "性别化目标", "达成率"], rows,
                         col_widths=[3.6, 3.6, 4.6, 3.6])
        doc.add_paragraph("")

    doc.add_heading("七、膳食结构调整建议", level=2)
    suggestions = []
    if totals["protein"] < target_protein:
        suggestions.append(
            f"蛋白质摄入不足：当前 {totals['protein']}g，目标 {target_protein}g，建议增加鸡胸肉、鸡蛋、豆制品等高蛋白食材。"
        )
    elif totals["protein"] > target_protein * 1.3:
        suggestions.append(
            f"蛋白质摄入偏高：当前 {totals['protein']}g，目标 {target_protein}g，建议适当减少蛋白类食材。"
        )
    if protein_pct < GUIDELINES["cn_2022"]["protein_pct"][0]:
        suggestions.append(f"蛋白质供能比 {protein_pct}% 低于中国指南下限 {GUIDELINES['cn_2022']['protein_pct'][0]}%，建议增加蛋白质摄入。")
    if carbs_pct > GUIDELINES["cn_2022"]["carbs_pct"][1]:
        suggestions.append(f"碳水供能比 {carbs_pct}% 高于中国指南上限 {GUIDELINES['cn_2022']['carbs_pct'][1]}%，建议减少精制碳水。")
    if fat_pct < GUIDELINES["cn_2022"]["fat_pct"][0]:
        suggestions.append(f"脂肪供能比 {fat_pct}% 低于中国指南下限 {GUIDELINES['cn_2022']['fat_pct'][0]}%，可适当增加优质脂肪。")
    if fat_pct > GUIDELINES["cn_2022"]["fat_pct"][1]:
        suggestions.append(f"脂肪供能比 {fat_pct}% 高于中国指南上限 {GUIDELINES['cn_2022']['fat_pct'][1]}%，建议减少油脂摄入。")
    suggestions.append(f"按当前活动水平（{activity}），蛋白质推荐摄入量为 {protein_rec_low}–{protein_rec_high} g/日。")
    total_protein_ratio = round(totals["protein"] / weight, 1) if weight else 0
    suggestions.append(f"当前蛋白质摄入量折合 {total_protein_ratio} g/kg 体重/日。")
    if gt and ctx["sex"] == "female" and micro["iron"] < gt["iron_target"]:
        suggestions.append(
            f"女性铁需求高于男性（RNI {gt['iron_target']} mg/日，{gt['iron_note']}），"
            f"本次估算摄入 {micro['iron']} mg，建议每周 2–3 次动物血/肝脏/瘦红肉，并搭配富含维生素 C 的蔬果促进吸收。"
        )
    ba = bmi_assess(ctx["bmi"], ctx["sex"])
    if ba and ba["cn"] in ("超重", "肥胖"):
        extra = f"；按体脂等危口径为{ba['fat_equivalent']['level']}，建议以减脂而非单纯减重为目标" if "fat_equivalent" in ba else ""
        suggestions.append(f"BMI {ctx['bmi']} 属{ba['cn']}（中国标准 24/28）{extra}。")
    if va["overall"] in ("偏高", "高"):
        suggestions.append(f"内脏脂肪综合分级为“{va['overall']}”，优先执行以下对策：")
        suggestions.extend(VISCERAL_ADVICE[:6])
    if not suggestions:
        suggestions.append("当前膳食结构基本合理，建议继续保持均衡搭配。")
    add_bullets(doc, suggestions)
    doc.add_paragraph("")

    doc.add_heading("八、附录：计算依据", level=2)
    appendix_text = (
        f"热量换算系数：蛋白质 {KCAL_PER_G['protein']} kcal/g，碳水化合物 {KCAL_PER_G['carbs']} kcal/g，脂肪 {KCAL_PER_G['fat']} kcal/g。\n"
        f"活动水平分级：步数 < 3000 → 静态; 3000–8000 → 低活动; ≥ 8000 → 中活动。\n"
        f"蛋白质推荐：静态 {ACTIVITY_PROTEIN['sedentary']} g/kg/日; 低活动 {ACTIVITY_PROTEIN['low']} g/kg/日; 中活动 {ACTIVITY_PROTEIN['moderate']} g/kg/日。\n"
        f"中国指南 2022 供能比：碳水 50–65%，蛋白 10–20%，脂肪 20–30%。\n"
        f"美国 DGA 2025–2030 供能比：碳水 45–65%，蛋白 10–35%，脂肪 20–35%。\n"
        f"食材营养数据来源：内置统一营养成分表（以每 100g/100ml 计）；微量营养素为估算值。\n"
        f"BMI：中国成人 WS/T 428—2013（18.5/24.0/28.0）；WHO 亚洲行动点 23.0/27.5；日本 JASSO 25.0；"
        f"体脂/代谢等危换算见 Obesity 2015（中国人群）。\n"
        f"腰围：中国男 ≥90、女 ≥85 cm 为中心型肥胖；日本内脏脂肪型肥胖筛查男 ≥85、女 ≥90 cm；腰高比 ≥0.5 提示风险。\n"
        f"体脂率：男 >25%、女 >30% 为体脂过多（肥胖症诊疗指南 2024）；亚洲正常体重肥胖阈值男 20.6%、女 33.4%。\n"
        f"内脏脂肪面积：CT/MRI ≥100 cm² 为内脏脂肪型肥胖（日本肥胖学会），100–150 偏高、≥150 高；"
        f"生物电阻抗体脂秤等级 1–9 标准、10–14 偏高、≥15 高。\n"
        f"CVAI（Xia et al. 2016）：男 = −267.93 + 0.68×年龄 + 0.03×BMI + 4.00×腰围 + 22.00×lgTG − 16.32×HDL-C；"
        f"女 = −187.32 + 1.71×年龄 + 4.23×BMI + 1.12×腰围 + 39.76×lgTG − 11.66×HDL-C；"
        f"参考切点男 101.80、女 88.42（CHARLS 心脑血管结局）。\n"
        f"能量估算：Mifflin-St Jeor（男 +5、女 −161）× PAL（静态 1.4 / 低 1.5 / 中 1.7 / 高 1.9）。\n"
        f"DRIs 2023（18–64 岁，轻身体活动）：蛋白质 男 65 / 女 55 g；铁 男 12 / 女 18 mg（无月经 10 mg）；"
        f"锌 男 12 / 女 8.5 mg；钙 800 mg；维生素 A 男 770 / 女 660 μgRAE；膳食纤维 25–30 g；"
        f"酒精上限 男 25 / 女 15 g/日。\n"
        f"内脏脂肪营养对策（完整）：\n"
        + "\n".join(f"  {i + 1}. {a}" for i, a in enumerate(VISCERAL_ADVICE))
    )
    p_appendix = doc.add_paragraph(appendix_text)
    for run in p_appendix.runs:
        run.font.name = "宋体"
        run.font.size = Pt(9)
    p_appendix.paragraph_format.line_spacing = Pt(14)

    output_path = os.path.join(output_dir(), f"{name}-个人膳食宏量营养素报告.docx")
    doc.save(output_path)
    return output_path


def run_meal(params):
    name = params.get("name", "未提供")
    gender = params.get("gender", "未提供")
    age = params.get("age", "未提供")
    weight = params["weight"]
    height = params.get("height", None)
    activity_input = params.get("activity", params.get("steps", 6000))
    target_protein = params["target_protein"]
    allowed_meats = params.get("allowed_meats", ["鸡胸肉", "猪肉(瘦)"])
    allowed_eggs = params.get("allowed_eggs", ["鸡蛋"])
    allowed_dairy = params.get("allowed_dairy", ["牛奶"])
    allowed_soy = params.get("allowed_soy", ["豆腐", "豆腐干"])
    preferred = params.get("preferred_foods", [])
    lunch_staple = params.get("lunch_staple", "白米饭")
    dinner_staple = params.get("dinner_staple", "白米饭")
    use_oats = params.get("use_oats", False)
    use_sweet_potato = params.get("use_sweet_potato", False)
    weight_loss_goal = params.get("weight_loss_goal", None)
    fat_loss_goal = params.get("fat_loss_goal", None)

    if isinstance(activity_input, (int, float)):
        activity = met_min_to_activity(activity_input)
        met_min_weekly = activity_input
    else:
        activity = "low"
        met_min_weekly = 600

    protein_range = ACTIVITY_PROTEIN[activity]
    rec_low = round(weight * protein_range[0], 1)
    rec_high = round(weight * protein_range[1], 1)
    bmi = round(weight / ((height / 100) ** 2), 1) if height else None

    kcal_per_kg_fat = 7700
    suggested_weeks = 8
    if weight_loss_goal:
        total_deficit = weight_loss_goal * kcal_per_kg_fat
        daily_deficit = round(total_deficit / (suggested_weeks * 7), 0)
    else:
        daily_deficit = 0

    protein_pool = allowed_meats + allowed_eggs + allowed_dairy + allowed_soy
    protein_pool = [p for p in protein_pool if p in FOOD_NUTRITION]
    if preferred:
        preferred_in_pool = [p for p in preferred if p in protein_pool]
        if preferred_in_pool:
            protein_pool = preferred_in_pool + [p for p in protein_pool if p not in preferred_in_pool]
    protein_pool = list(dict.fromkeys(protein_pool))
    main_protein_pool = [p for p in protein_pool if p not in DAIRY_FOODS]
    if not main_protein_pool:
        main_protein_pool = protein_pool

    meal_ratio = {"早餐": 0.25, "午餐": 0.35, "晚餐": 0.30, "加餐": 0.10}
    meal_protein_targets = {k: round(target_protein * v, 1) for k, v in meal_ratio.items()}
    meal_plan = {}
    used = []
    meal_staples = {"早餐": None, "午餐": lunch_staple, "晚餐": dinner_staple, "加餐": None}
    if use_oats:
        meal_staples["早餐"] = "燕麦"
    if use_sweet_potato and meal_staples["早餐"] is None:
        meal_staples["早餐"] = "红薯"

    for meal, p_target in meal_protein_targets.items():
        items = []
        p_accum = c_accum = f_accum = 0.0
        if meal == "加餐":
            fruit_name = None
            for pf in preferred:
                if pf in ("香蕉", "苹果"):
                    fruit_name = pf
                    break
            if not fruit_name:
                fruit_name = "香蕉"
            fruit_amt = 150
            fruit_res = calc_food(fruit_name, fruit_amt)
            if fruit_res:
                items.append({"name": fruit_name, "amount": fruit_amt, **fruit_res})
                p_accum += fruit_res["protein"]; c_accum += fruit_res["carbs"]; f_accum += fruit_res["fat"]
            if "牛奶" in protein_pool:
                milk_res = calc_food("牛奶", 200)
                if milk_res:
                    items.append({"name": "牛奶", "amount": 200, **milk_res})
                    p_accum += milk_res["protein"]; c_accum += milk_res["carbs"]; f_accum += milk_res["fat"]
        else:
            staple_name = meal_staples.get(meal)
            if staple_name and staple_name in FOOD_NUTRITION:
                staple_amt = 200 if staple_name in ("白米饭", "糙米") else 100
                staple_res = calc_food(staple_name, staple_amt)
                if staple_res:
                    items.append({"name": staple_name, "amount": staple_amt, **staple_res})
                    p_accum += staple_res["protein"]; c_accum += staple_res["carbs"]; f_accum += staple_res["fat"]
            chosen = pick_best(main_protein_pool, p_target, exclude=used)
            if chosen:
                pname, pamt = chosen
                used.append(pname)
                if len(used) > len(main_protein_pool) - 1:
                    used = []
                pres = calc_food(pname, pamt)
                if pres:
                    items.append({"name": pname, "amount": pamt, **pres})
                    p_accum += pres["protein"]; c_accum += pres["carbs"]; f_accum += pres["fat"]
            if meal in ("午餐", "晚餐"):
                veg_list = [v for v in VEGGIES if v in FOOD_NUTRITION]
                veg_name = veg_list[0] if veg_list else "青菜"
                veg_res = calc_food(veg_name, 150)
                if veg_res:
                    items.append({"name": veg_name, "amount": 150, **veg_res})
                    p_accum += veg_res["protein"]; c_accum += veg_res["carbs"]; f_accum += veg_res["fat"]
                oil_res = calc_food("橄榄油", 5)
                if oil_res:
                    items.append({"name": "橄榄油", "amount": 5, **oil_res})
                    f_accum += oil_res["fat"]
            if meal == "早餐" and "牛奶" in protein_pool and "牛奶" not in [i["name"] for i in items]:
                milk_res = calc_food("牛奶", 200)
                if milk_res:
                    items.append({"name": "牛奶", "amount": 200, **milk_res})
                    p_accum += milk_res["protein"]; c_accum += milk_res["carbs"]; f_accum += milk_res["fat"]
        meal_plan[meal] = {
            "items": items,
            "total": {"protein": round(p_accum, 1), "carbs": round(c_accum, 1), "fat": round(f_accum, 1)},
        }

    totals = {"protein": 0.0, "carbs": 0.0, "fat": 0.0}
    for mp in meal_plan.values():
        for k in totals:
            totals[k] += mp["total"][k]
    for k in totals:
        totals[k] = round(totals[k], 1)

    total_kcal = round(totals["protein"] * KCAL_PER_G["protein"] + totals["carbs"] * KCAL_PER_G["carbs"] + totals["fat"] * KCAL_PER_G["fat"], 1)
    protein_kcal = round(totals["protein"] * KCAL_PER_G["protein"], 1)
    carbs_kcal = round(totals["carbs"] * KCAL_PER_G["carbs"], 1)
    fat_kcal = round(totals["fat"] * KCAL_PER_G["fat"], 1)
    protein_pct = round(protein_kcal / total_kcal * 100, 1) if total_kcal else 0
    carbs_pct = round(carbs_kcal / total_kcal * 100, 1) if total_kcal else 0
    fat_pct = round(fat_kcal / total_kcal * 100, 1) if total_kcal else 0
    carb_protein_ratio = round(totals["carbs"] / totals["protein"], 1) if totals["protein"] else "N/A"

    who_compliance = "达标"
    if met_min_weekly < WHO_MET_MIN_WEEK["minimal"]:
        who_compliance = "未达标"
    elif met_min_weekly < WHO_MET_MIN_WEEK["optimal"]:
        who_compliance = "最低达标"

    meal_items = [it for mp in meal_plan.values() for it in mp["items"]]
    micro, micro_covered, micro_total = micro_totals(meal_items)

    doc = new_doc()
    p_title = doc.add_heading("个人精准配餐报告", level=0)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p_title.runs:
        run.font.name = "宋体"
    doc.add_paragraph("")

    doc.add_heading("一、个人信息", level=2)
    ctx = build_ctx(params)
    ctx["bmi"] = bmi
    info_rows = [("姓名", str(name)), ("性别", str(gender)), ("年龄", str(age)), ("体重 (kg)", str(weight))]
    if height:
        info_rows.append(("身高 (cm)", str(height)))
        info_rows.append(("BMI", str(bmi)))
    if ctx["waist"]:
        info_rows.append(("腰围 (cm)", str(ctx["waist"])))
    info_rows += [("日常运动量 (MET·min/周)", str(met_min_weekly)),
                  ("活动水平", activity),
                  ("WHO 运动量判定", who_compliance)]
    info_table = doc.add_table(rows=len(info_rows), cols=2)
    info_table.style = "Table Grid"
    for i, (k, v) in enumerate(info_rows):
        set_cell_text(info_table.rows[i].cells[0], k, bold=True)
        set_cell_text(info_table.rows[i].cells[1], v)
    doc.add_paragraph("")

    va = build_body_section(doc, ctx, "二")

    doc.add_heading("三、需求汇总", level=2)
    doc.add_heading("3.1 配餐约束", level=3)
    req_rows = [("蛋白质推荐区间 (g/日)", f"{rec_low} – {rec_high}"),
                ("目标蛋白质 (g/日)", str(target_protein)),
                ("蛋白质食材库", ", ".join(protein_pool)),
                ("午餐主食", lunch_staple), ("晚餐主食", dinner_staple)]
    if use_oats:
        req_rows.append(("早餐替换", "燕麦"))
    if use_sweet_potato:
        req_rows.append(("早餐替换", "红薯"))
    req_table = doc.add_table(rows=len(req_rows), cols=2)
    req_table.style = "Table Grid"
    for i, (k, v) in enumerate(req_rows):
        set_cell_text(req_table.rows[i].cells[0], k, bold=True)
        set_cell_text(req_table.rows[i].cells[1], v)
    doc.add_paragraph("")
    doc.add_heading("3.2 性别化营养目标", level=3)
    gt = gender_target_table(doc, ctx)

    doc.add_heading("四、配餐建议", level=2)
    for meal in ("早餐", "午餐", "晚餐", "加餐"):
        doc.add_heading(meal, level=3)
        mp = meal_plan[meal]
        headers = ["食材", "用量"]
        rows = []
        for item in mp["items"]:
            unit = "ml" if FOOD_NUTRITION.get(item["name"], {}).get("unit") == "100ml" else "g"
            amt = int(item["amount"]) if item["amount"] == int(item["amount"]) else item["amount"]
            rows.append([item["name"], f"{amt}{unit}"])
        add_styled_table(doc, headers, rows, col_widths=[4, 4])
        p_sub = doc.add_paragraph()
        run_sub = p_sub.add_run(
            f"本餐小计：蛋白质 {mp['total']['protein']}g | 碳水 {mp['total']['carbs']}g | 脂肪 {mp['total']['fat']}g"
        )
        run_sub.font.name = "宋体"
        run_sub.font.size = Pt(9)
        doc.add_paragraph("")

    doc.add_heading("五、营养素计算", level=2)
    doc.add_heading("5.1 宏量汇总表", level=3)
    add_styled_table(doc, ["营养素", "总重量 (g)", "热量 (kcal)", "供能占比 (%)"], [
        ["蛋白质", totals["protein"], protein_kcal, protein_pct],
        ["碳水化合物", totals["carbs"], carbs_kcal, carbs_pct],
        ["脂肪", totals["fat"], fat_kcal, fat_pct],
        ["合计", round(sum(totals.values()), 1), total_kcal, round(protein_pct + carbs_pct + fat_pct, 1)],
    ])
    doc.add_paragraph("")
    p_ratio = doc.add_paragraph()
    run_r = p_ratio.add_run(f"碳水 : 蛋白质重量比 = {carb_protein_ratio} : 1")
    run_r.font.name = "宋体"
    run_r.font.size = Pt(10)
    doc.add_paragraph("")

    doc.add_heading("5.2 分餐营养素分布", level=3)
    dist_rows = []
    for meal in ("早餐", "午餐", "晚餐", "加餐"):
        mp = meal_plan[meal]
        dist_rows.append([meal, mp["total"]["protein"], mp["total"]["carbs"], mp["total"]["fat"]])
    add_styled_table(doc, ["餐次", "蛋白质 (g)", "碳水 (g)", "脂肪 (g)"], dist_rows)
    doc.add_paragraph("")

    doc.add_heading("5.3 膳食指南评估", level=3)
    for key, gl in GUIDELINES.items():
        doc.add_heading(gl["label"], level=4)
        add_styled_table(doc, ["营养素", "当前占比 (%)", "推荐区间 (%)", "判定"], [
            ["蛋白质", protein_pct, f"{gl['protein_pct'][0]}-{gl['protein_pct'][1]}",
             "合规" if gl["protein_pct"][0] <= protein_pct <= gl["protein_pct"][1] else "偏离"],
            ["碳水化合物", carbs_pct, f"{gl['carbs_pct'][0]}-{gl['carbs_pct'][1]}",
             "合规" if gl["carbs_pct"][0] <= carbs_pct <= gl["carbs_pct"][1] else "偏离"],
            ["脂肪", fat_pct, f"{gl['fat_pct'][0]}-{gl['fat_pct'][1]}",
             "合规" if gl["fat_pct"][0] <= fat_pct <= gl["fat_pct"][1] else "偏离"],
        ])
        doc.add_paragraph("")

    doc.add_heading("5.4 运动量指南评估", level=3)
    who_rows = [
        ("指南", WHO_PA),
        ("当前运动量", f"{met_min_weekly} MET·min/周"),
        ("最低推荐", f"≥{WHO_MET_MIN_WEEK['minimal']} MET·min/周"),
        ("最优推荐", f"≥{WHO_MET_MIN_WEEK['optimal']} MET·min/周"),
        ("判定", who_compliance),
    ]
    who_table = doc.add_table(rows=len(who_rows), cols=2)
    who_table.style = "Table Grid"
    for i, (k, v) in enumerate(who_rows):
        set_cell_text(who_table.rows[i].cells[0], k, bold=True)
        set_cell_text(who_table.rows[i].cells[1], v)
    doc.add_paragraph("")

    if weight_loss_goal:
        target_weight = round(weight - weight_loss_goal, 1)
        doc.add_heading("5.5 减重计划", level=3)
        loss_rows = [
            ("当前体重", f"{weight} kg"),
            ("减重目标", f"{weight_loss_goal} kg"),
            ("目标体重", f"{target_weight} kg"),
            ("建议周期", f"{suggested_weeks} 周"),
            ("每日热量缺口", f"{daily_deficit:.0f} kcal"),
            ("减脂 1kg ≈ 7,700 kcal", ""),
        ]
        loss_table = doc.add_table(rows=len(loss_rows), cols=2)
        loss_table.style = "Table Grid"
        for i, (k, v) in enumerate(loss_rows):
            set_cell_text(loss_table.rows[i].cells[0], k, bold=True)
            set_cell_text(loss_table.rows[i].cells[1], v)
        doc.add_paragraph("")

    if gt:
        doc.add_heading("5.6 微量营养素估算达成", level=3)
        p_cov = doc.add_paragraph(
            f"覆盖率：{micro_covered}/{micro_total} 种食材有内置微量营养素数据，未覆盖食材未计入。估算值仅供参考。"
        )
        for run in p_cov.runs:
            run.font.name = "宋体"
            run.font.size = Pt(9)
        micro_rows = [
            ["蛋白质", f"{totals['protein']} g", f"{target_protein} g",
             f"{round(totals['protein'] / target_protein * 100, 1)} %"],
            ["铁", f"{micro['iron']} mg", f"{gt['iron_target']} mg",
             f"{round(micro['iron'] / gt['iron_target'] * 100, 1)} %"],
            ["锌", f"{micro['zinc']} mg", f"{gt['zinc_rni']} mg",
             f"{round(micro['zinc'] / gt['zinc_rni'] * 100, 1)} %"],
            ["钙", f"{micro['calcium']} mg", f"{gt['calcium_rni']} mg",
             f"{round(micro['calcium'] / gt['calcium_rni'] * 100, 1)} %"],
            ["膳食纤维", f"{micro['fiber']} g", f"{gt['fiber_ai'][0]}–{gt['fiber_ai'][1]} g",
             "低于下限" if micro["fiber"] < gt["fiber_ai"][0] else "达标"],
        ]
        add_styled_table(doc, ["营养素", "估算摄入", "性别化目标", "达成率"], micro_rows,
                         col_widths=[3.6, 3.6, 4.6, 3.6])
        doc.add_paragraph("")

    doc.add_heading("六、调整建议", level=2)
    suggestions = []
    if weight_loss_goal:
        suggestions.append(
            f"减重 {weight_loss_goal}kg 目标：每日需制造约 {daily_deficit:.0f} kcal 热量缺口，"
            f"建议周期 {suggested_weeks} 周。当前配餐总热量约 {total_kcal} kcal/日，"
            f"建议结合运动消耗 {met_min_weekly} MET·min/周以达成缺口。"
        )
    if totals["protein"] < rec_low:
        suggestions.append(f"蛋白质摄入 {totals['protein']}g 低于推荐下限 {rec_low}g，建议增加蛋白类食材。")
    elif totals["protein"] > rec_high * 1.2:
        suggestions.append(f"蛋白质摄入 {totals['protein']}g 显著高于推荐上限 {rec_high}g，建议适当减少。")
    if protein_pct < GUIDELINES["cn_2022"]["protein_pct"][0]:
        suggestions.append(f"蛋白质供能比 {protein_pct}% 低于中国指南下限，建议增加蛋白质。")
    if carbs_pct > GUIDELINES["cn_2022"]["carbs_pct"][1]:
        suggestions.append(f"碳水供能比 {carbs_pct}% 高于中国指南上限，建议减少主食用量或替换为低升糖主食。")
    if carbs_pct < GUIDELINES["cn_2022"]["carbs_pct"][0]:
        suggestions.append(f"碳水供能比 {carbs_pct}% 低于中国指南下限，建议增加主食或蔬果。")
    if fat_pct > GUIDELINES["cn_2022"]["fat_pct"][1]:
        suggestions.append(f"脂肪供能比 {fat_pct}% 高于中国指南上限，建议减少油脂或高脂食材。")
    if fat_pct < GUIDELINES["cn_2022"]["fat_pct"][0]:
        suggestions.append(f"脂肪供能比 {fat_pct}% 低于中国指南下限，可适当增加优质脂肪。")
    if who_compliance != "达标":
        suggestions.append(f"当前运动量 {met_min_weekly} MET·min/周 未达 WHO 最优推荐 (≥{WHO_MET_MIN_WEEK['optimal']})，建议增加运动量。")
    if gt and ctx["sex"] == "female" and micro["iron"] < gt["iron_target"]:
        suggestions.append(
            f"女性铁需求 {gt['iron_target']} mg/日（{gt['iron_note']}），本次配餐估算 {micro['iron']} mg，"
            f"建议每周 2–3 次瘦红肉/动物血/肝脏，并搭配维生素 C 促进吸收。"
        )
    if va["overall"] in ("偏高", "高"):
        suggestions.append(f"内脏脂肪综合分级为“{va['overall']}”，优先执行以下对策：")
        suggestions.extend(VISCERAL_ADVICE[:6])
    if not suggestions:
        suggestions.append("当前配餐结构基本合理，建议继续保持均衡搭配。")
    suggestions.append(f"按 {activity} 活动水平，蛋白质推荐 {rec_low}–{rec_high} g/日。")
    add_bullets(doc, suggestions)
    doc.add_paragraph("")

    doc.add_heading("附录：计算依据", level=2)
    appendix = (
        f"热量换算：蛋白质 {KCAL_PER_G['protein']} kcal/g，碳水 {KCAL_PER_G['carbs']} kcal/g，脂肪 {KCAL_PER_G['fat']} kcal/g。\n"
        f"活动水平划分：<500 MET·min/周=sedentary, 500-1000=low, ≥1000=moderate。\n"
        f"蛋白质推荐：sedentary {ACTIVITY_PROTEIN['sedentary']}，low {ACTIVITY_PROTEIN['low']}，moderate {ACTIVITY_PROTEIN['moderate']} g/kg/日。\n"
        f"中国指南 2022：碳水 50-65%，蛋白 10-20%，脂肪 20-30%。\n"
        f"美国 DGA 2025-2030：碳水 45-65%，蛋白 10-35%，脂肪 20-35%。\n"
        f"WHO 运动指南：≥500 MET·min/周（最低），≥1000 MET·min/周（最优）。\n"
        f"食材营养数据：内置统一营养成分表（每 100g/100ml）；微量营养素为估算值。\n"
        f"BMI：中国成人 WS/T 428—2013（18.5/24.0/28.0）；WHO 亚洲 23.0/27.5；日本 JASSO 25.0；"
        f"体脂等危口径 男 23.0/27.9、女 24.4/32.5；代谢风险等危口径 男 22.5/25.9、女 22.8/26.6。\n"
        f"腰围：中国男 ≥90、女 ≥85 cm；日本男 ≥85、女 ≥90 cm；腰高比 ≥0.5 提示风险。\n"
        f"体脂率：男 >25%、女 >30% 为体脂过多；亚洲正常体重肥胖阈值 男 20.6%、女 33.4%。\n"
        f"内脏脂肪面积：≥100 cm² 为内脏脂肪型肥胖（100–150 偏高、≥150 高）；体脂秤等级 10–14 偏高、≥15 高。\n"
        f"CVAI：男 −267.93+0.68×年龄+0.03×BMI+4.00×腰围+22.00×lgTG−16.32×HDL-C（切点 101.80）；"
        f"女 −187.32+1.71×年龄+4.23×BMI+1.12×腰围+39.76×lgTG−11.66×HDL-C（切点 88.42）。\n"
        f"能量估算：Mifflin-St Jeor（男 +5、女 −161）× PAL。\n"
        f"DRIs 2023：蛋白质 男 65 / 女 55 g；铁 男 12 / 女 18 mg（无月经 10 mg）；锌 男 12 / 女 8.5 mg；"
        f"钙 800 mg；维生素 A 男 770 / 女 660 μgRAE；膳食纤维 25–30 g；酒精上限 男 25 / 女 15 g/日。\n"
        f"MET 计算：kcal = MET × 体重(kg) × 时间(min) × 3.5 / 200。"
    )
    p_app = doc.add_paragraph(appendix)
    for run in p_app.runs:
        run.font.name = "宋体"
        run.font.size = Pt(9)
    p_app.paragraph_format.line_spacing = Pt(14)

    output_path = os.path.join(output_dir(), f"{name}-个人精准配餐报告.docx")
    doc.save(output_path)
    return output_path


def run_body(params):
    """仅做体型/内脏脂肪/性别化营养评估，不出 docx。"""
    ctx = build_ctx(params)
    if ctx["bmi"] is None:
        return {"error": "缺少 weight 与 height，无法计算 BMI"}
    va = visceral_assess(ctx)
    return {
        "mode": "body",
        "sex": ctx["sex"],
        "age": ctx["age"],
        "bmi": ctx["bmi"],
        "bmi_assessment": bmi_assess(ctx["bmi"], ctx["sex"]),
        "waist": waist_assess(ctx["waist"], ctx["sex"], ctx["height"]),
        "body_fat": body_fat_assess(ctx["body_fat"], ctx["sex"]),
        "visceral": va,
        "energy": energy_estimate(ctx),
        "gender_targets": gender_targets(ctx),
        "advice": VISCERAL_ADVICE if va["overall"] in ("偏高", "高") else [],
    }


BODY_PARAM_RANGES = {
    "weight": (20, 300), "height": (80, 250), "waist": (30, 200), "hip": (30, 200),
    "body_fat": (2, 70), "visceral_fat_level": (1, 30), "visceral_fat_area": (1, 500),
    "tg": (0.1, 30), "hdl": (0.1, 10), "age": (1, 120), "steps": (0, 60000),
}


def validate_body_params(params):
    for key, (lo, hi) in BODY_PARAM_RANGES.items():
        if key in params and params[key] is not None:
            v = _as_float(params[key])
            if v is None:
                return f"{key} 必须为数值"
            if not (lo <= v <= hi):
                return f"{key} 超出合理范围（{lo}–{hi}）"
    sex = params.get("sex", params.get("gender"))
    if sex is not None and norm_sex(sex) is None:
        return f"无法识别性别: {sex}（可用 男/女/male/female）"
    return None


def dispatch(params):
    mode = params.get("mode")
    if mode is None or str(mode).strip() == "":
        return {"error": f"缺少 mode 参数，请选择: {', '.join(MODES)}", "modes": list(MODES)}
    mode = str(mode).strip().lower()
    if mode not in MODES:
        return {"error": f"未知 mode: {mode}，请选择: {', '.join(MODES)}", "modes": list(MODES)}

    bad = validate_body_params(params)
    if bad:
        return {"error": bad}

    if mode == "met":
        if "exercises" not in params and "weekly_activities" not in params:
            return {"error": "缺少 exercises 或 weekly_activities 参数"}
        return run_met(params)

    if mode == "body":
        return run_body(params)

    if mode == "macro":
        for r in ["weight", "steps", "target_protein", "foods"]:
            if r not in params:
                return {"error": f"缺少必填参数: {r}"}
        if not isinstance(params["foods"], list) or len(params["foods"]) == 0:
            return {"error": "foods 必须为非空列表"}
        for f in params["foods"]:
            if "name" not in f or "amount" not in f:
                return {"error": "每个食材需包含 name 和 amount"}
            if f["name"] not in FOOD_NUTRITION:
                return {"error": f"不支持食材: {f['name']}", "supported": list(FOOD_NUTRITION.keys())}
        path = run_macro(params)
        return {"success": True, "output": path}

    for r in ["weight", "target_protein"]:
        if r not in params:
            return {"error": f"缺少必填参数: {r}"}
    for key in ["allowed_meats", "allowed_eggs", "allowed_dairy", "allowed_soy"]:
        if key in params:
            for f in params[key]:
                if f not in FOOD_NUTRITION:
                    return {"error": f"不支持食材: {f}", "supported": list(FOOD_NUTRITION.keys())}
    for sk in ["lunch_staple", "dinner_staple"]:
        if sk in params and params[sk] not in STAPLES:
            return {"error": f"不支持主食: {params[sk]}", "supported": STAPLES}
    path = run_meal(params)
    return {"success": True, "output": path}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": f"需要输入 JSON 参数，请选择 mode: {', '.join(MODES)}"}, ensure_ascii=False))
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"JSON 解析失败: {e}"}, ensure_ascii=False))
        sys.exit(1)

    result = dispatch(params)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
