from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Emu(12192000)
prs.slide_height = Emu(6858000)

TITLE_COLOR = RGBColor(0x1A, 0x3C, 0x6E)
BODY_COLOR = RGBColor(0x33, 0x33, 0x33)
ACCENT_COLOR = RGBColor(0x2E, 0x75, 0xB6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG = RGBColor(0xF2, 0xF5, 0xFA)
DARK_BG = RGBColor(0x1A, 0x3C, 0x6E)


def add_rect(slide, left, top, width, height, fill_color, line_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
    else:
        shape.line.fill.background()
    return shape


def set_font(run, name_cn='微软雅黑', name_en='Arial', size=Pt(14), bold=False, color=BODY_COLOR):
    run.font.name = name_en
    run.font.size = size
    run.font.bold = bold
    run.font.color.rgb = color


def add_textbox(slide, left, top, width, height, text, font_size=Pt(14), bold=False, color=BODY_COLOR, align=PP_ALIGN.LEFT, name_cn='微软雅黑', name_en='Arial'):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_font(run, name_cn, name_en, font_size, bold, color)
    return txBox


def add_bullet_slide(slide, items, left, top, width, height, font_size=Pt(14), color=BODY_COLOR, line_spacing=1.5):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.space_after = Pt(4)
        p.line_spacing = line_spacing
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = item
        set_font(run, size=font_size, color=color)
    return txBox


def add_slide_number(slide, num, total):
    add_textbox(slide, Inches(12.0), Inches(7.0), Inches(1.0), Inches(0.3),
                f"{num}/{total}", Pt(10), color=RGBColor(0x99, 0x99, 0x99), align=PP_ALIGN.RIGHT)


def make_title_bar(slide, title_text):
    add_rect(slide, Inches(0), Inches(0), Inches(13.333), Inches(0.9), DARK_BG)
    add_textbox(slide, Inches(0.5), Inches(0.15), Inches(12), Inches(0.6),
                title_text, Pt(28), True, WHITE, PP_ALIGN.LEFT)
    add_rect(slide, Inches(0), Inches(0.9), Inches(13.333), Inches(0.06), ACCENT_COLOR)
    add_textbox(slide, Inches(0.5), Inches(7.0), Inches(5), Inches(0.3),
                "浙江清华长三角研究院", Pt(10), color=RGBColor(0x99, 0x99, 0x99))


def make_section_slide(slide, section_num, section_title):
    add_rect(slide, Inches(0), Inches(0), Inches(13.333), Inches(7.5), DARK_BG)
    add_rect(slide, Inches(0.5), Inches(2.5), Inches(0.08), Inches(1.5), ACCENT_COLOR)
    add_textbox(slide, Inches(0.8), Inches(2.3), Inches(11), Inches(0.6),
                f"0{section_num}" if section_num < 10 else str(section_num), Pt(48), True, ACCENT_COLOR)
    add_textbox(slide, Inches(0.8), Inches(3.0), Inches(11), Inches(0.8),
                section_title, Pt(36), True, WHITE)
    add_textbox(slide, Inches(0.8), Inches(3.7), Inches(11), Inches(0.4),
                "食药用菌产业技术与发展趋势", Pt(14), color=RGBColor(0xAA, 0xBB, 0xDD))


TOTAL_SLIDES = 12

# ===== Slide 1: 封面 =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_rect(slide, Inches(0), Inches(0), Inches(13.333), Inches(7.5), DARK_BG)
add_rect(slide, Inches(0), Inches(2.8), Inches(13.333), Inches(0.04), ACCENT_COLOR)
add_textbox(slide, Inches(0.8), Inches(1.5), Inches(11.5), Inches(1.2),
            "食药用菌产业技术与发展趋势", Pt(40), True, WHITE, PP_ALIGN.LEFT)
add_textbox(slide, Inches(0.8), Inches(3.2), Inches(11.5), Inches(0.6),
            "——产业现状、技术前沿与未来展望", Pt(22), False, RGBColor(0xCC, 0xDD, 0xEE))
add_textbox(slide, Inches(0.8), Inches(5.5), Inches(11.5), Inches(0.4),
            "蔡强", Pt(18), False, RGBColor(0xAA, 0xBB, 0xDD))
add_textbox(slide, Inches(0.8), Inches(5.9), Inches(11.5), Inches(0.4),
            "浙江清华长三角研究院", Pt(14), False, RGBColor(0x88, 0x99, 0xBB))

# ===== Slide 2: 目录 =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
make_title_bar(slide, "目  录")
toc_items = [
    "01  食药用菌的范畴",
    "02  全球食药用菌的分布",
    "03  全球食药用菌的产业格局",
    "04  我国食药用菌的分布",
    "05  我国食药用菌的产业格局",
    "06  我国食药用菌的产业困境分析",
]
for i, item in enumerate(toc_items):
    y = 1.3 + i * 0.75
    add_rect(slide, Inches(0.8), Inches(y), Inches(0.06), Inches(0.45), ACCENT_COLOR)
    add_textbox(slide, Inches(1.1), Inches(y), Inches(10), Inches(0.5),
                item, Pt(18), False, BODY_COLOR)
add_slide_number(slide, 2, TOTAL_SLIDES)

# ===== Slide 3: 食药用菌的范畴 =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
make_title_bar(slide, "01  食药用菌的范畴")
add_textbox(slide, Inches(0.5), Inches(1.2), Inches(12), Inches(0.4),
            "食药用菌是指可食用或具有药用价值的大型真菌（蘑菇），属于真菌界，主要包括担子菌门和子囊菌门。",
            Pt(14), False, BODY_COLOR)

items_left = [
    "◆ 食用菌（主要品种）",
    "    香菇（Lentinula edodes）— 全球第二大品种",
    "    平菇（Pleurotus ostreatus）— 产量最大",
    "    双孢蘑菇（Agaricus bisporus）— 欧美主流",
    "    金针菇（Flammulina velutipes）",
    "    杏鲍菇（Pleurotus eryngii）",
    "    木耳 / 银耳 / 茶树菇 / 滑菇",
]
items_right = [
    "◆ 药用菌（主要品种）",
    "    灵芝（Ganoderma lucidum）— 免疫调节",
    "    冬虫夏草（Cordyceps sinensis）— 补肾益肺",
    "    猴头菇（Hericium erinaceus）— 养胃",
    "    蛹虫草（Cordyceps militaris）— 虫草素",
    "    桑黄（Sanghuangporus）— 抗肿瘤",
    "    茯苓 / 猪苓 / 云芝",
]
add_bullet_slide(slide, items_left, Inches(0.3), Inches(1.7), Inches(6), Inches(5.0), Pt(13))
add_bullet_slide(slide, items_right, Inches(6.5), Inches(1.7), Inches(6), Inches(5.0), Pt(13))
add_slide_number(slide, 3, TOTAL_SLIDES)

# ===== Slide 4: 全球食药用菌的分布 =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
make_title_bar(slide, "02  全球食药用菌的分布")
add_textbox(slide, Inches(0.5), Inches(1.2), Inches(12), Inches(0.4),
            "全球总产量约4,800万吨（2022年），中国占85-90%", Pt(16), True, ACCENT_COLOR)

items = [
    "◆ 主要生产国排名",
    "  1. 中国 — 约4,000+万吨，占全球85-90%",
    "  2. 欧盟（荷兰/波兰/西班牙）— 约150-200万吨",
    "  3. 美国 — 约40-45万吨",
    "  4. 日本 — 约8-10万吨",
    "  5. 韩国 — 约6-8万吨",
    "◆ 区域主要品种分布",
    "  中国：香菇、平菇、金针菇、木耳、灵芝、冬虫夏草",
    "  欧洲：双孢蘑菇（占80%以上）",
    "  美国：双孢蘑菇（占90%）、香菇、平菇",
    "  日本：香菇、金针菇、舞茸、灵芝",
    "  东南亚：草菇、平菇",
]
add_bullet_slide(slide, items, Inches(0.3), Inches(1.7), Inches(12), Inches(5.0), Pt(13))
add_slide_number(slide, 4, TOTAL_SLIDES)

# ===== Slide 5: 全球产业格局（栽培与市场） =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
make_title_bar(slide, "03  全球食药用菌的产业格局")
add_textbox(slide, Inches(0.5), Inches(1.2), Inches(12), Inches(0.4),
            "栽培与市场", Pt(18), True, ACCENT_COLOR)

items = [
    "◆ 全球产量趋势",
    "  2010年约2,500万吨 → 2022年约4,800万吨，CAGR 5-7%",
    "  1978年仅约106万吨，40余年增长45倍",
    "◆ 市场价值",
    "  2022年全球蘑菇市场规模约600-700亿美元",
    "  预计2030年将达800-1,000亿美元，CAGR 7-9%",
    "◆ 主要加工产品",
    "  鲜品40-45% | 干品20-25% | 罐头10-15%",
    "  冷冻5-8% | 保健品提取物8-12% | 调味品3-5%",
    "◆ 人均年消费量（鲜品等价）",
    "  中国15-20kg | 欧盟3-4kg | 美国2-3kg | 日本4-5kg",
    "  全球平均约5-6kg",
]
add_bullet_slide(slide, items, Inches(0.3), Inches(1.7), Inches(12), Inches(5.0), Pt(13))
add_slide_number(slide, 5, TOTAL_SLIDES)

# ===== Slide 6: 我国食药用菌的分布 =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
make_title_bar(slide, "04  我国食药用菌的分布")
add_textbox(slide, Inches(0.5), Inches(1.2), Inches(12), Inches(0.4),
            "2022年中国食用菌总产量约4,220万吨，从业人数约3,000万人", Pt(16), True, ACCENT_COLOR)

items_left = [
    "◆ 主要生产省份（前十）",
    "  1. 河南 ~600万吨（香菇/平菇）",
    "  2. 福建 ~500万吨（香菇/银耳）",
    "  3. 山东 ~450万吨（平菇/金针菇）",
    "  4. 河北 ~400万吨（平菇/杏鲍菇）",
    "  5. 黑龙江 ~350万吨（黑木耳/滑菇）",
    "  6. 四川 ~300万吨（香菇/羊肚菌）",
    "  7. 江苏 ~250万吨（金针菇/杏鲍菇）",
    "  8. 湖北 ~200万吨（香菇/平菇）",
    "  9. 浙江 ~180万吨（香菇/金针菇）",
    " 10. 湖南 ~150万吨（平菇/香菇）",
]
items_right = [
    "◆ 品种产量结构",
    "  香菇 ~1,200万吨（28%）",
    "  平菇 ~800万吨（19%）",
    "  黑木耳 ~700万吨（17%）",
    "  金针菇 ~350万吨（8%）",
    "  双孢蘑菇 ~300万吨（7%）",
    "  杏鲍菇 ~250万吨（6%）",
    "  银耳 ~100万吨（2.5%）",
    "  其他 ~400万吨（9.5%）",
]
add_bullet_slide(slide, items_left, Inches(0.3), Inches(1.7), Inches(6.2), Inches(5.0), Pt(12))
add_bullet_slide(slide, items_right, Inches(6.8), Inches(1.7), Inches(5.5), Inches(5.0), Pt(12))
add_slide_number(slide, 6, TOTAL_SLIDES)

# ===== Slide 7: 我国产业格局（栽培与加工） =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
make_title_bar(slide, "05  我国食药用菌的产业格局（栽培与加工）")
add_textbox(slide, Inches(0.5), Inches(1.2), Inches(12), Inches(0.4),
            "总产值约3,800-4,200亿元（2022年）", Pt(16), True, ACCENT_COLOR)

items = [
    "◆ 栽培现状",
    "  工厂化率约15-20%（金针菇、杏鲍菇达80%以上）",
    "  工厂化生产企业约500-600家",
    "  从业人数约3,000万人（含种植、加工、流通）",
    "◆ 加工现状",
    "  加工率仅15-20%，远低于发达国家40-50%",
    "  干制40% | 罐头20% | 速冻10% | 保健品15% | 即食品10% | 其他5%",
    "  产业链短，初级产品销售比例高",
    "◆ 出口概况",
    "  出口量约60-70万吨/年，出口额约35-45亿美元",
    "  主要出口市场：日本、韩国、美国、欧盟、东南亚",
    "  主要品种：香菇干、蘑菇罐头、木耳干、灵芝提取物",
]
add_bullet_slide(slide, items, Inches(0.3), Inches(1.7), Inches(12), Inches(5.0), Pt(13))
add_slide_number(slide, 7, TOTAL_SLIDES)

# ===== Slide 8: 我国产业困境（上） =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
make_title_bar(slide, "06  我国食药用菌的产业困境分析（一）")
add_textbox(slide, Inches(0.5), Inches(1.2), Inches(12), Inches(0.4),
            "深加工不足、产能过剩、质量安全、品种同质化四大挑战", Pt(16), True, ACCENT_COLOR)

items = [
    "◆ 问题一：深加工率偏低",
    "  加工率仅15-20%（发达国家40-50%，荷兰60%+），附加值低",
    "◆ 问题二：产能过剩与价格波动",
    "  大宗品种供过于求，价格波动幅度达50-100%以上",
    "  毛木耳从40元/kg（2019）跌至15-20元/kg（2023）",
    "◆ 问题三：质量安全与标准化不足",
    "  农药残留、重金属超标问题时有发生",
    "  标准化覆盖率低，溯源体系建设滞后",
    "◆ 问题四：品种结构单一、同质化严重",
    "  香菇/平菇/木耳/金针菇/杏鲍菇占总产量70%+",
    "  珍稀品种占比小，缺乏差异化竞争",
]
add_bullet_slide(slide, items, Inches(0.3), Inches(1.7), Inches(12), Inches(5.0), Pt(13))
add_slide_number(slide, 8, TOTAL_SLIDES)

# ===== Slide 9: 我国产业困境（下） =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
make_title_bar(slide, "06  我国食药用菌的产业困境分析（二）")
add_textbox(slide, Inches(0.5), Inches(1.2), Inches(12), Inches(0.4),
            "菌种知识产权、工厂化水平、贸易壁垒、科技创新等深层问题", Pt(16), True, ACCENT_COLOR)

items = [
    "◆ 问题五：菌种知识产权保护薄弱",
    "  受专利保护的品种不足10%，日本/韩国掌握核心种源",
    "◆ 问题六：工厂化水平滞后",
    "  工厂化率15-20%（日本60%+，韩国50%+），自动化程度不高",
    "◆ 问题七：国际贸易壁垒",
    "  日本肯定列表制度、欧盟农残标准持续收紧",
    "◆ 问题八：科技创新能力不足",
    "  研发投入占产业总产值不到0.5%，精深加工技术落后",
    "◆ 问题九：环境与资源问题",
    "  菌渣年产生量超5,000万吨，综合利用率低",
    "◆ 问题十：产业链协同不足",
    "  小散农户为主，品牌化程度低，冷链物流损耗率15-20%",
]
add_bullet_slide(slide, items, Inches(0.3), Inches(1.7), Inches(12), Inches(5.0), Pt(13))
add_slide_number(slide, 9, TOTAL_SLIDES)

# ===== Slide 10: 产业困境 - 总结图表 =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
make_title_bar(slide, "06  产业困境总结")
items = [
    "1. 加工率低 → 附加值低，产业链短",
    "2. 产能过剩 → 价格战，菇贱伤农",
    "3. 质量安全 → 农残超标，出口受阻",
    "4. 品种同质 → 缺乏差异化，竞争激烈",
    "5. 种源受制 → 知识产权薄弱，依赖进口",
    "6. 工厂化低 → 自动化不足，能耗偏高",
    "7. 贸易壁垒 → 绿色壁垒，标准趋严",
    "8. 创新不足 → 研发投入少，装备落后",
    "9. 环境压力 → 菌渣污染，资源消耗",
    "10. 协同不足 → 品牌弱，损耗高",
]
add_bullet_slide(slide, items, Inches(0.5), Inches(1.3), Inches(9), Inches(5.5), Pt(14))
add_slide_number(slide, 10, TOTAL_SLIDES)

# ===== Slide 11: 发展趋势展望 =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
make_title_bar(slide, "发展趋势与展望")
add_textbox(slide, Inches(0.5), Inches(1.2), Inches(9), Inches(0.4),
            "食药用菌产业高质量发展方向", Pt(18), True, ACCENT_COLOR)

items = [
    "◆ 精深加工升级",
    "  提高加工率至30-40%，发展功能性食品、保健品、药品",
    "◆ 工厂化智能化",
    "  提升工厂化率至30%+，引入物联网、AI环境控制",
    "◆ 品种多元化",
    "  培育珍稀品种（羊肚菌、松茸、牛肝菌），优化品种结构",
    "◆ 品牌化与标准化",
    "  建立全程质量追溯体系，打造区域公用品牌",
    "◆ 绿色循环经济",
    "  菌渣资源化利用（有机肥、生物质燃料），减少环境污染",
    "◆ 国际合作与出口",
    '  拓展"一带一路"市场，应对绿色贸易壁垒',
    "◆ 科技创新驱动",
    "  加大研发投入，突破液体菌种、活性成分提取等关键技术",
]
add_bullet_slide(slide, items, Inches(0.3), Inches(1.7), Inches(9), Inches(5.0), Pt(13))
add_slide_number(slide, 11, TOTAL_SLIDES)

# ===== Slide 12: 结尾页 =====
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_rect(slide, Inches(0), Inches(0), Inches(10), Inches(7.5), DARK_BG)
add_rect(slide, Inches(0), Inches(3.2), Inches(10), Inches(0.04), ACCENT_COLOR)
add_textbox(slide, Inches(0.8), Inches(2.0), Inches(8.4), Inches(1.0),
            "感谢各位专家", Pt(40), True, WHITE, PP_ALIGN.CENTER)
add_textbox(slide, Inches(0.8), Inches(3.6), Inches(8.4), Inches(0.6),
            "敬请批评指正", Pt(24), False, RGBColor(0xCC, 0xDD, 0xEE), PP_ALIGN.CENTER)
add_textbox(slide, Inches(0.8), Inches(5.5), Inches(8.4), Inches(0.4),
            "蔡强 | 浙江清华长三角研究院", Pt(16), False, RGBColor(0xAA, 0xBB, 0xDD), PP_ALIGN.CENTER)

output_path = "/home/caiq/opencode/plant/mushroom/食药用菌产业技术与发展趋势.pptx"
prs.save(output_path)
print(f"PPTX saved to: {output_path}")
print(f"Total slides: {len(prs.slides)}")