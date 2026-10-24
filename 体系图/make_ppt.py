#!/usr/bin/env python3
# MyAgents 体系图 PPT —— 长三院简洁模板样式
# 样式依据：文档专家/templates/ppt-长三院简洁模板-template.md + generate_pptx.py
#   深蓝 #1A3C6E 标题带 · 强调 #2E75B6 · 正文 #333333 · 底纹 #F2F5FA
#   封面/分隔页深蓝满版 · 内容页顶部标题带 + 页脚「浙江清华长三角研究院」+ 页码
#   字体 中文 微软雅黑 / 西文 Arial
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "MyAgents-体系图.pptx")

NAVY   = RGBColor(0x1A, 0x3C, 0x6E)   # 主色 深蓝
ACCENT = RGBColor(0x2E, 0x75, 0xB6)   # 强调 蓝
BODY   = RGBColor(0x33, 0x33, 0x33)   # 正文
LIGHT  = RGBColor(0xF2, 0xF5, 0xFA)   # 浅底
GREY   = RGBColor(0x99, 0x99, 0x99)   # 次要
SUB    = RGBColor(0xCC, 0xDD, 0xEE)   # 封面副标题
AUTHOR = RGBColor(0xAA, 0xBB, 0xDD)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
TINT   = RGBColor(0xE6, 0xEE, 0xF7)   # 深蓝上的浅字
CN, EN = "微软雅黑", "Arial"
INST = "浙江清华长三角研究院"

prs = Presentation()
prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)   # 16:9
SW, SH = 13.333, 7.5
BLANK = prs.slide_layouts[6]

# ───────────────────────── 基础元件
def set_font(run, size=14, bold=False, color=BODY, cn=CN, en=EN):
    run.font.name = en; run.font.size = Pt(size); run.font.bold = bold
    run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", cn if tag == "a:ea" else en)

def rect(slide, x, y, w, h, fill, shape=MSO_SHAPE.RECTANGLE):
    sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.fill.background(); sh.shadow.inherit = False
    return sh

def text(slide, x, y, w, h, s, size=14, bold=False, color=BODY,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.25):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, ln in enumerate(s.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = spacing
        set_font(p.add_run(), size, bold, color)
        p.runs[0].text = ln
    return tb

def _text_w(s, size):
    cjk = sum(1 for ch in s if ord(ch) > 0x2000)
    return (cjk + (len(s) - cjk) * 0.55) * size / 72.0

def bullets(slide, x, y, w, items, size=13, gap=0.10, color=BODY):
    cy = y
    for it in items:
        head, body = it if isinstance(it, tuple) else (None, it)
        d = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(cy + 0.085),
                                   Inches(0.075), Inches(0.075))
        d.fill.solid(); d.fill.fore_color.rgb = ACCENT
        d.line.fill.background(); d.shadow.inherit = False
        tb = slide.shapes.add_textbox(Inches(x + 0.22), Inches(cy), Inches(w - 0.22), Inches(0.4))
        tf = tb.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]; p.line_spacing = 1.28
        if head:
            r = p.add_run(); r.text = head; set_font(r, size, True, NAVY)
        r = p.add_run(); r.text = body; set_font(r, size, False, color)
        tw = _text_w((head or "") + body, size)
        lines = int(tw / (w - 0.26)) + 1
        cy += lines * size * 1.28 / 72.0 + gap
    return cy

def picture_fit(slide, name, x, y, w, h):
    im = Image.open(os.path.join(HERE, name)); ar = im.width / im.height
    if w / h > ar:
        ph, pw = h, h * ar
    else:
        pw, ph = w, w / ar
    slide.shapes.add_picture(os.path.join(HERE, name),
                             Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2),
                             Inches(pw), Inches(ph))
    return pw, ph

def card(slide, x, y, w, h):
    return rect(slide, x, y, w, h, LIGHT)

# ───────────────────────── 版式
def title_bar(slide, title, num=None):
    rect(slide, 0, 0, SW, 0.9, NAVY)
    rect(slide, 0, 0.9, SW, 0.06, ACCENT)
    label = title if num is None else f"{num}   {title}"
    text(slide, 0.5, 0.14, 11.4, 0.62, label, 28, True, WHITE, anchor=MSO_ANCHOR.MIDDLE)
    rect(slide, 0, 0, 0.14, 0.9, ACCENT)

def footer(slide, page=None, total=None):
    text(slide, 0.5, 7.03, 6.0, 0.3, INST, 10, False, GREY)
    if page is not None:
        text(slide, 11.3, 7.03, 1.53, 0.3, f"{page}/{total}", 10, False, GREY, PP_ALIGN.RIGHT)

def section(num, title, sub):
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, SH, NAVY)
    rect(s, 0.5, 2.62, 0.09, 1.5, ACCENT)
    text(s, 0.82, 2.42, 6.0, 0.9, f"{num:02d}", 48, True, ACCENT)
    text(s, 0.82, 3.22, 11.4, 0.8, title, 36, True, WHITE)
    text(s, 0.82, 4.02, 11.4, 0.4, sub, 14, False, TINT)
    return s

def content(title, num=None):
    s = prs.slides.add_slide(BLANK)
    title_bar(s, title, num)
    return s

def table(slide, x, y, w, rows, colw, fs=11, rh=0.6):
    gf = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(rh * len(rows)))
    tbl = gf.table
    tblPr = tbl._tbl.tblPr
    tblPr.set("firstRow", "0"); tblPr.set("bandRow", "0")
    for el in tblPr.findall(qn("a:tableStyleId")):
        tblPr.remove(el)
    style = etree.SubElement(tblPr, qn("a:tableStyleId"))
    style.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"     # No Style, No Grid
    tot = sum(colw)
    for j, cw in enumerate(colw):
        tbl.columns[j].width = Inches(w * cw / tot)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(rh)
        for j, val in enumerate(row):
            c = tbl.cell(i, j)
            c.margin_left = Inches(0.09); c.margin_right = Inches(0.07)
            c.margin_top = Inches(0.03); c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]; p.line_spacing = 1.12
            r = p.add_run(); r.text = str(val)
            if i == 0:
                c.fill.solid(); c.fill.fore_color.rgb = NAVY
                set_font(r, fs, True, WHITE)
            else:
                c.fill.solid()
                c.fill.fore_color.rgb = WHITE if i % 2 else LIGHT
                set_font(r, fs, False, BODY)
    return tbl

# 需要页码的内容页
numbered = []
def mark(slide):
    numbered.append(slide); return slide

# ═══════════════════════ 1 封面
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, NAVY)
rect(s, 0, 2.80, SW, 0.04, ACCENT)
text(s, 0.8, 1.50, 11.5, 1.2, "MyAgents 专家 Agent 体系图", 40, True, WHITE)
text(s, 0.8, 3.20, 11.5, 0.5, "—— 健康食品与现代农业 · opencode 领域专家库", 22, False, SUB)
text(s, 0.8, 3.95, 11.5, 0.4, "13 个 Agent　·　19 个技能　·　双层知识库（公共只读 + 私有）　·　进化闭环可回滚",
     14, False, TINT)
text(s, 0.8, 5.50, 11.5, 0.4, "蔡强", 18, False, AUTHOR)
text(s, 0.8, 5.92, 11.5, 0.4, INST, 14, False, RGBColor(0x88, 0x99, 0xBB))

# ═══════════════════════ 2 目录
s = prs.slides.add_slide(BLANK)
title_bar(s, "目　录")
mark(s)
toc = ["01　体系总览", "02　分层与边界", "03　业务协作流",
       "04　进化闭环", "05　部署与加载机制", "06　专家与支撑：清单 · 公共层 · 关键统计"]
for i, item in enumerate(toc):
    y = 1.35 + i * 0.82
    rect(s, 0.8, y + 0.06, 0.06, 0.42, ACCENT)
    text(s, 1.05, y, 11.5, 0.5, item, 18, False, NAVY)

# ═══════════════════════ 3 体系速览
s = content("体系速览", "00")
mark(s)
text(s, 0.5, 1.12, 12.3, 0.34,
     "三层结构：入口编排 → 领域专家 → 支撑（技能 / 知识 / 工具），外挂可回滚的进化闭环",
     13, False, GREY)
kpi = [("13", "个 Agent", "1 个 primary（orchestrator）\n12 个 mode = all（可主用亦可被调用）"),
       ("19", "个技能", "公共 2 · 私有 17\n其中 5 个可执行（带脚本）"),
       ("2", "层知识库", "公共知识（只读）+ 私有 references/\n公共书库 815 MB"),
       ("258", "条 L3 证据条目", "公共 80 · 毒理 104 · 质谱 74\n逐条带页码 / PMCID，可回原文")]
for i, (num, unit, desc) in enumerate(kpi):
    x = 0.5 + i * 3.13
    card(s, x, 1.60, 2.95, 2.15)
    rect(s, x, 1.60, 2.95, 0.075, ACCENT)
    text(s, x + 0.25, 1.86, 2.45, 0.65, num, 34, True, NAVY)
    text(s, x + 0.25, 2.52, 2.45, 0.3, unit, 14, True, ACCENT)
    text(s, x + 0.25, 2.88, 2.45, 0.75, desc, 10.5, False, BODY, spacing=1.3)
card(s, 0.5, 4.00, 12.333, 2.85)
text(s, 0.85, 4.22, 11.6, 0.35, "一句话读法", 15, True, NAVY)
bullets(s, 0.90, 4.72, 11.6, [
    ("入口唯一　", "orchestrator 是 13 个 agent 中唯一的 primary，负责澄清 / 拆解 / 路由 / 交接 / 汇总 / 验收；"),
    ("专家平权　", "其余 12 位 mode = all，既可被手动选为主 agent 单干，也可被 orchestrator 当子 agent 调用；"),
    ("知识与技能分层　", "专家之间不互读私有库，跨界资料上移到公共层（公共知识只读 + 公共技能）；"),
    ("可演化　", "评估 → 复盘 → 固化 → 登记 EVOLUTION.md → git 版本化 → 回归；评分人工启动、演化人工裁定。"),
], size=13.5)

# ═══════════════════════ 图页
def fig_page(num, title, sub, png, items):
    section(num, title, sub)
    s = content(title, f"{num:02d}")
    mark(s)
    picture_fit(s, png, 0.5, 1.28, 7.42, 5.4)
    card(s, 8.17, 1.28, 4.66, 5.4)
    bullets(s, 8.44, 1.62, 4.16, items, size=12.5)
    return s

fig_page(1, "体系总览", "入口层 → 领域专家层 → 支撑层 → 交付物 + 进化闭环", "01-总览.png", [
    ("13 个 agent　", "1 个 primary + 12 个 mode: all。"),
    ("4 类支撑　", "技能 19（公共 2 / 私有 17）、公共知识（只读）、私有 references/ 与 templates/、内置技能与脚本。"),
    ("进化闭环　", "evals/ → retrospectives/ → 固化 agent.md / SKILL.md / references/ → EVOLUTION.md → git。"),
    ("治理原则　", "评分人工启动、演化人工裁定；系统只记录与可回滚。"),
])

fig_page(2, "分层与边界", "私有事实来源 / 公共只读层 / 全局内置 / 边界纪律", "02-分层.png", [
    ("唯一事实来源　", "改 agent.md 或 SKILL.md 即改行为，项目与全局软链自动生效。"),
    ("公共只读　", "公共知识目录不得写入，变更须登记 EVOLUTION.md。"),
    ("私有隔离　", "agent.md 只索引本目录 references/，不引用他专家私有库。"),
    ("跨界上移　", "同时服务多领域的资料统一放 公共知识/案例库/，以软链共享。"),
])

# ── ③ 业务协作流（横幅图 + 底部要点）
section(3, "业务协作流", "生产端 → 加工端 → 评价端 → 交付端的真实依赖链")
s = content("业务协作流", "03"); mark(s)
picture_fit(s, "03-协作流.png", 0.5, 1.30, 12.333, 3.90)
card(s, 0.5, 5.35, 12.333, 1.5)
bullets(s, 0.85, 5.55, 11.7, [
    ("主链　", "育种 → 育苗 → 种植 → 发酵 / 食品加工 → 安全 / 营养 → 文档 → 投稿。"),
    ("质谱 → 检测　", "检测管全局标准、前处理与质量体系；质谱管深度环节（选型、碎裂、MRM/HRMS、未知物鉴定）。"),
    ("毒理 → 食品安全　", "毒理产出“毒性凭什么”（POD / HBGV / 证据权重）；食品安全做“是否超标”。风险评估只回答“风险多大”。"),
], size=12.5)

fig_page(4, "进化闭环", "评估 → 复盘 → 固化 → 登记 → 版本化 → 回归", "04-进化闭环.png", [
    ("规则　", "失败一个用例，就应产出一条固化动作。"),
    ("现状　", "15 个 P0 用例（13 专家 + 公共技能）首轮全量评分 15 / 15 通过。"),
    ("治理　", "评分由人工启动、演化决策由人工最终裁定；系统仅记录与可回滚。"),
    ("基线　", "git tag baseline-2026-10-23 作为演化祖先与回滚点。"),
])

fig_page(5, "部署与加载机制", "install.sh 三种模式与启动加载", "05-部署机制.png", [
    ("默认 link　", "软链到 ~/.config/opencode/，任何目录启动 opencode 均可用（推荐）。"),
    ("--project　", "软链到 MyAgents/.opencode/，项目模式自动加载。"),
    ("--copy　", "复制快照，源更新后需重跑。"),
    ("配置　", "opencode.json：default_agent = orchestrator、skills.paths、references = 公共知识。"),
    ("注意　", "配置与 agent 启动时加载、不热更新；改动后需重启 opencode。"),
])

# ═══════════════════════ 06 专家与支撑
section(6, "专家与支撑", "13 位专家 / 19 个技能 / 公共层与关键统计")
COLW = [1.4, 1.9, 1.15, 2.55, 5.33]
ROWS_A = [
    ["专家", "agent id", "mode · temp", "私有技能（★=可执行）", "私有知识库要点"],
    ["协调专家", "orchestrator", "primary · 0.2", "orchestration", "编排模式与路由 · 跨专家工作流（6 个端到端）· 汇总质检"],
    ["种植专家", "planting-expert", "all · 0.3", "planting-knowledge、plant-lstm ★", "栽培·土肥水·植保·生长模型 ＋ 证据条目 108 条 ＋ 书库 48 册"],
    ["育种专家", "breeding-expert", "all · 0.25", "breeding-knowledge", "种质·分子育种·品种审定·制种 ＋ 证据条目 64 条 ＋ 书库 16 册"],
    ["育苗专家", "nursery-expert", "all · 0.3", "nursery-knowledge", "催芽·基质·嫁接扦插·组培·工厂化 ＋ 证据条目 60 条 ＋ 书库 14 册"],
    ["发酵专家", "fermentation-expert", "all · 0.3", "fermentation-knowledge、microbial-growth ★", "菌种·工艺·动力学·下游膜分离 ＋ 证据条目 46 条 ＋ 书库 34 册"],
    ["食品加工专家", "food-processing-expert", "all · 0.3", "food-processing", "配方·单元操作·中试放大·货架期 ＋ 证据条目 51 条 ＋ 书库 118 册/篇"],
]
ROWS_B = [
    ["专家", "agent id", "mode · temp", "私有技能（★=可执行）", "私有知识库要点"],
    ["食品安全专家", "food-safety-expert", "all · 0.2", "food-safety", "限量法规·化学/生物危害·检测监测与 HACCP ＋ 风险排序案例"],
    ["营养专家", "nutrition-expert", "all · 0.3", "nutrition、nutritionist ★", "DRIs·配餐·营养标签 ＋ 证据条目 47 条 ＋ 书库 221 册"],
    ["检测专家", "detection-expert", "all · 0.2", "detection-analysis", "方法学·前处理·方法验证与质控·CNAS/CMA ＋ 能力评价案例"],
    ["质谱专家", "mass-spec-expert", "all · 0.2", "mass-spectrometry、spectral-matching ★", "选型·MRM/HRMS·未知物鉴定 ＋ 证据条目 74 条 ＋ 本地谱库 3 套"],
    ["毒理专家", "toxicology-expert", "all · 0.2", "toxicology", "POD / HBGV·毒性终点·计算毒理与 NAMs ＋ 证据条目 104 条"],
    ["文档专家", "document-expert", "all · 0.4", "document-format", "7 份文档 ＋ 6 份 PPT 模板 ＋ generate_pptx.py；复用内置 pptx/docx 等"],
    ["投稿专家", "submission-expert", "all · 0.3", "journal-submission", "期刊规则 Schema·合规诊断·投稿材料 ＋ 规则缓存（ISSN 为唯一键）"],
]
s = content("专家清单（一）农业生产与食品制造", "06"); mark(s)
table(s, 0.5, 1.20, 12.333, ROWS_A, COLW, fs=10.5, rh=0.62)
text(s, 0.5, 6.65, 12.3, 0.3, "★ = 可执行技能（带脚本）；temp = agent.md 中 request.body.temperature", 10, False, GREY)

s = content("专家清单（二）评价、检测与交付", "06"); mark(s)
table(s, 0.5, 1.20, 12.333, ROWS_B, COLW, fs=10.5, rh=0.56)
text(s, 0.5, 6.65, 12.3, 0.3, "除 orchestrator 为 primary（默认入口）外，其余 12 位 mode 均为 all。", 10, False, GREY)

s = content("公共层与边界纪律", "06"); mark(s)
text(s, 0.5, 1.14, 6.2, 0.32, "公共知识（opencode.json 注册为全局 references）", 14, True, NAVY)
table(s, 0.5, 1.52, 6.3, [
    ["分区", "内容"],
    ["政策法规与规划/", "官方政策、规划、批复文件（含盖章件）"],
    ["标准规范/", "标准要点与查询入口（不整篇下载）"],
    ["技术指南/", "通用指南 ＋ L3 原著证据条目 80 条"],
    ["案例库/", "跨领域共享案例（多专家软链共享）"],
    ["知识图谱/", "togomcp-sparql 可查 47 个 RDF 数据库"],
    ["书库/", "815 MB：EHC 240、ICH M7(R2)、SANTE v2026、MDPI 24 册、OECD 指南 17 份、OA 176 篇"],
], [1.45, 4.85], fs=10.5, rh=0.62)
text(s, 7.15, 1.14, 5.7, 0.32, "边界纪律（防越界 / 防臆造）", 14, True, NAVY)
bullets(s, 7.15, 1.58, 5.68, [
    ("三问分界　", "风险多大 → 公共技能 risk-assessment；毒性凭什么 → 毒理专家；是否超标 → 食品安全专家。"),
    ("公共库只读　", "各私有库不得写入 公共知识/，变更须登记 EVOLUTION.md。"),
    ("私有库隔离　", "各专家 agent.md 只索引本目录 references/，不引用他人私有库。"),
    ("跨界资料上移　", "多领域共用资料上移 公共知识/案例库/，软链共享，避免重复。"),
    ("引用纪律　", "法规 / 标准 / 限量 / 指导值以官方现行文本为准；条目只作方法学锚点。"),
], size=11.5)

s = content("关键统计与维护方式", "06"); mark(s)
table(s, 0.5, 1.20, 6.9, [
    ["指标", "数值"],
    ["Agent 总数", "13（1 primary + 12 mode: all）"],
    ["技能总数", "19（公共 2 + 私有 17，其中可执行 5）"],
    ["公共 L3 证据条目", "80 条"],
    ["三份核心 L3 合计", "258 条（公共 80 + 毒理 104 + 质谱 74）"],
    ["私有 L3 条目", "种植 108 · 育种 64 · 育苗 60 · 食品加工 51 · 营养 47 · 发酵 46"],
    ["私有书库（册·篇）", "种植 48 · 育种 16 · 育苗 14 · 发酵 34 · 食品加工 118 · 营养 221"],
    ["公共书库", "815 MB（EHC 240 / ICH M7(R2) / SANTE v2026 / MDPI 24 / OECD 17 / OA 176）"],
    ["本地质谱谱库", "人参 1778 · 金线莲 2387 · 合并检索 2954 条"],
    ["评估用例 / 基线", "15 个 P0，首轮 15 / 15 通过　|　git tag baseline-2026-10-23"],
], [1.95, 4.95], fs=10.5, rh=0.53)
card(s, 7.65, 1.20, 5.18, 3.85)
text(s, 7.92, 1.44, 4.7, 0.32, "重新生成", 14, True, NAVY)
text(s, 7.92, 1.88, 4.7, 2.9,
     "cd MyAgents/体系图\n"
     "python3 compose_all.py     # 拼全集 PNG\n"
     "python3 make_ppt.py        # 本 PPT（长三院简洁）\n"
     "\n"
     "# 单张重渲染（改 mmd/*.mmd 后）\n"
     "mmdc -p puppeteer-config.json \\\n"
     "     -i mmd/01-总览.mmd \\\n"
     "     -o 01-总览.png -b white -w 1634 -s 2",
     10.5, False, BODY, spacing=1.35)
text(s, 7.92, 5.20, 4.7, 0.8, "事实来源仍是各专家 agent.md 与 SKILL.md，\n本目录只是它们的投影。", 10.5, False, GREY, spacing=1.3)

# ═══════════════════════ 结尾
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, NAVY)
rect(s, 0.8, 3.35, 2.2, 0.045, ACCENT)
text(s, 0.8, 2.35, 11.5, 0.9, "感谢各位专家", 40, True, WHITE)
text(s, 0.8, 3.62, 11.5, 0.5, "敬请批评指正", 22, False, SUB)
text(s, 0.8, 5.70, 11.5, 0.4, "蔡强　·　" + INST, 14, False, RGBColor(0x88, 0x99, 0xBB))

# ═══════════════════════ 页码
TOTAL = len(prs.slides._sldIdLst)
for i, sl in enumerate(numbered, 1):
    footer(sl, i, TOTAL)

prs.save(OUT)
print(f"{OUT}  {TOTAL} slides  {os.path.getsize(OUT)//1024} KB  (长三院简洁模板样式)")

