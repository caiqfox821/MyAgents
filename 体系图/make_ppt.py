#!/usr/bin/env python3
# 由体系图 PNG + 体系数据生成 16:9 PPT。
import os, copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "MyAgents-体系图.pptx")

NAVY   = RGBColor(0x0D, 0x47, 0xA1)
BLUE   = RGBColor(0x15, 0x65, 0xC0)
LBLUE  = RGBColor(0xE3, 0xF2, 0xFD)
INK    = RGBColor(0x26, 0x32, 0x38)
GREY   = RGBColor(0x60, 0x7D, 0x8B)
LINE   = RGBColor(0xCF, 0xD8, 0xDC)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
GREEN  = RGBColor(0x2E, 0x7D, 0x32)
TEAL   = RGBColor(0x00, 0x83, 0x8F)
RED    = RGBColor(0xC6, 0x28, 0x28)
PURPLE = RGBColor(0x6A, 0x1B, 0x9A)
ORANGE = RGBColor(0xEF, 0x6C, 0x00)
FONT   = "微软雅黑"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = 13.333, 7.5

def txbox(slide, x, y, w, h, text, size=18, bold=False, color=INK,
          align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=FONT, spacing=1.15):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run(); r.text = ln
        r.font.size = Pt(size); r.font.bold = bold
        r.font.color.rgb = color; r.font.name = font
    return tb

def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06):
    sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(1)
    sh.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try: sh.adjustments[0] = radius
        except Exception: pass
    return sh

def header(slide, no, title, sub=None):
    rect(slide, 0.55, 0.42, 0.09, 0.62, BLUE, shape=MSO_SHAPE.RECTANGLE)
    txbox(slide, 0.78, 0.34, 11.0, 0.5, title, size=27, bold=True, color=NAVY)
    if no:
        txbox(slide, 0.78, 0.44, 11.0, 0.3, "", size=12)
    if sub:
        txbox(slide, 0.78, 0.92, 11.9, 0.34, sub, size=13, color=GREY)
    ln = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(1.30), Inches(12.23), Emu(9525))
    ln.fill.solid(); ln.fill.fore_color.rgb = LINE; ln.line.fill.background(); ln.shadow.inherit = False

def picture_fit(slide, png, x, y, w, h):
    """在 (x,y,w,h) 框内等比放入图片，居中，返回实际尺寸。"""
    im = Image.open(png); ar = im.width / im.height
    if w / h > ar:
        ph = h; pw = h * ar
    else:
        pw = w; ph = w / ar
    px = x + (w - pw) / 2; py = y + (h - ph) / 2
    slide.shapes.add_picture(png, Inches(px), Inches(py), Inches(pw), Inches(ph))
    return pw, ph

def _text_w(text, size):
    """估算文本宽度（英寸）：中文按 1.0em，西文按 0.55em。"""
    cjk = sum(1 for ch in text if ord(ch) > 0x2000)
    other = len(text) - cjk
    return (cjk * 1.0 + other * 0.55) * size / 72.0

def bullets(slide, x, y, w, items, size=14, gap=0.06, dot=BLUE, dotsize=0.11, lead=1.35):
    cy = y
    for it in items:
        head, body = it if isinstance(it, tuple) else (None, it)
        d = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(cy + 0.075), Inches(dotsize), Inches(dotsize))
        d.fill.solid(); d.fill.fore_color.rgb = dot; d.line.fill.background(); d.shadow.inherit = False
        tb = txbox(slide, x + 0.24, cy, w - 0.24, 0.4, "", size=size)
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.line_spacing = lead
        if head:
            r = p.add_run(); r.text = head
            r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = NAVY; r.font.name = FONT
        r = p.add_run(); r.text = body
        r.font.size = Pt(size); r.font.color.rgb = INK; r.font.name = FONT
        total_w = _text_w((head or "") + body, size)
        lines = max(1, int(total_w / (w - 0.28)) + (1 if total_w % (w - 0.28) else 0))
        cy += lines * size * lead / 72.0 + gap
    return cy

def table(slide, x, y, w, rows, col_w, header_row=True, fs=11.5, rh=0.34):
    nrow, ncol = len(rows), len(rows[0])
    shp = slide.shapes.add_table(nrow, ncol, Inches(x), Inches(y), Inches(w), Inches(rh * nrow))
    tbl = shp.table
    tbl.first_row = header_row
    total = sum(col_w)
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(w * cw / total)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(rh)
        for j, val in enumerate(row):
            c = tbl.cell(i, j)
            c.margin_left = Inches(0.07); c.margin_right = Inches(0.05)
            c.margin_top = Inches(0.02); c.margin_bottom = Inches(0.02)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]; p.line_spacing = 1.0
            r = p.add_run(); r.text = str(val); r.font.name = FONT
            if i == 0 and header_row:
                c.fill.solid(); c.fill.fore_color.rgb = NAVY
                r.font.size = Pt(fs); r.font.bold = True; r.font.color.rgb = WHITE
            else:
                c.fill.solid()
                c.fill.fore_color.rgb = RGBColor(0xF5, 0xF8, 0xFA) if i % 2 else WHITE
                r.font.size = Pt(fs); r.font.color.rgb = INK
    return tbl

def footnote(slide, text):
    txbox(slide, 0.55, 7.06, 12.23, 0.3, text, size=10, color=GREY)

# ─────────────────────────────────── S1 封面
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, NAVY, shape=MSO_SHAPE.RECTANGLE)
rect(s, 0, 0, SW, 0.22, RGBColor(0x6A, 0x1B, 0x9A), shape=MSO_SHAPE.RECTANGLE)
txbox(s, 1.1, 2.20, 11.2, 1.2, "MyAgents 专家 Agent 体系图", size=48, bold=True, color=WHITE)
txbox(s, 1.1, 3.52, 11.2, 0.5, "健康食品与现代农业 · opencode 领域专家库", size=22, color=RGBColor(0xBB, 0xDE, 0xFB))
rect(s, 1.12, 4.30, 2.4, 0.045, RGBColor(0x90, 0xCA, 0xF9), shape=MSO_SHAPE.RECTANGLE)
txbox(s, 1.1, 4.62, 11.2, 1.2,
      "13 个 Agent　·　19 个技能　·　双层知识库（公共只读 + 私有）\n"
      "入口 orchestrator（primary）→ 12 领域专家（mode = all）→ 汇总校验交付",
      size=17, color=WHITE, spacing=1.5)
txbox(s, 1.1, 6.35, 11.2, 0.4,
      "基线 baseline-2026-10-23　|　模型 paratera/DeepSeek-V4-Flash　|　图由 mmd/*.mmd 渲染",
      size=12, color=RGBColor(0x90, 0xCA, 0xF9))

# ─────────────────────────────────── S2 体系速览（KPI 卡片）
s = prs.slides.add_slide(BLANK)
header(s, None, "体系速览", "三层结构：入口编排 → 领域专家 → 支撑（技能 / 知识 / 工具），外挂进化闭环")
cards = [
    ("13", "个 Agent", "1 个 primary（orchestrator）\n12 个 mode = all（可主用亦可被调用）", BLUE),
    ("19", "个技能", "公共 2：risk-assessment · togomcp-sparql\n私有 17（5 个可执行，带脚本）", TEAL),
    ("2", "层知识库", "公共知识（只读）+ 各专家 references/\n公共书库 815 MB · 私有书库 48/16/14/34/118/221", GREEN),
    ("258", "条 L3 证据条目", "公共 80 · 毒理 104 · 质谱 74\n逐条带页码 / PMCID，可回原文取据", PURPLE),
]
x0, y0, cw, ch, gx = 0.55, 1.60, 2.95, 2.05, 0.16
for i, (num, unit, desc, col) in enumerate(cards):
    x = x0 + i * (cw + gx)
    rect(s, x, y0, cw, ch, WHITE, line=LINE)
    rect(s, x, y0, cw, 0.075, col, shape=MSO_SHAPE.RECTANGLE)
    txbox(s, x + 0.22, y0 + 0.24, cw - 0.44, 0.6, num, size=34, bold=True, color=col)
    txbox(s, x + 0.22, y0 + 0.86, cw - 0.44, 0.3, unit, size=14, bold=True, color=INK)
    txbox(s, x + 0.22, y0 + 1.20, cw - 0.44, 0.75, desc, size=10.5, color=GREY, spacing=1.3)

rect(s, 0.55, 3.95, 12.23, 2.55, RGBColor(0xF5, 0xF8, 0xFA), line=LINE)
txbox(s, 0.85, 4.15, 11.6, 0.4, "一句话读法", size=15, bold=True, color=NAVY)
bullets(s, 0.90, 4.62, 11.5, [
    ("入口唯一　", "orchestrator 是 13 个 agent 中唯一的 primary，负责澄清 / 拆解 / 路由 / 交接 / 汇总 / 验收；"),
    ("专家平权　", "其余 12 位 mode = all，既可被手动选为主 agent 单干，也可被 orchestrator 当子 agent 调用；"),
    ("知识与技能分层　", "专家之间不互读私有库，跨界资料上移到公共层（公共知识只读 + 公共技能）；"),
    ("可演化　", "评估 → 复盘 → 固化 → 登记 EVOLUTION.md → git 版本化 → 回归，评分由人工启动、演化由人工裁定。"),
], size=13.5, dot=BLUE)

# ─────────────────────────────────── 图页
def fig_slide(no, title, sub, png, bullets_items=None, img_h=None):
    s = prs.slides.add_slide(BLANK)
    header(s, no, title, sub)
    if bullets_items:
        picture_fit(s, os.path.join(HERE, png), 0.55, 1.52, 7.75, 5.35)
        bb = rect(s, 8.55, 1.52, 4.23, 5.35, RGBColor(0xF5, 0xF8, 0xFA), line=LINE)
        bullets(s, 8.80, 1.80, 3.80, bullets_items, size=12.5)
    else:
        picture_fit(s, os.path.join(HERE, png), 0.60, 1.50, 12.13, img_h or 5.40)
    footnote(s, f"图 {no}　{title}")
    return s

fig_slide("①", "体系总览", "入口层 → 领域专家层 → 支撑层 → 交付物 + 进化闭环", "01-总览.png", [
    ("13 个 agent　", "1 个 primary + 12 个 mode: all。"),
    ("4 类支撑　", "技能 19（公共 2 / 私有 17）、公共知识（只读）、私有 references/ 与 templates/、内置技能与脚本。"),
    ("进化闭环　", "evals/ → retrospectives/ → 固化 agent.md / SKILL.md / references/ → EVOLUTION.md → git。"),
    ("治理原则　", "评分人工启动、演化人工裁定；系统只记录与可回滚。"),
])

fig_slide("②", "分层与边界", "私有事实来源 / 公共只读层 / 全局内置 / 边界纪律", "02-分层.png", [
    ("唯一事实来源　", "改 agent.md 或 SKILL.md 即改行为，项目与全局软链自动生效。"),
    ("公共只读　", "公共知识目录不得写入，变更须登记 EVOLUTION.md。"),
    ("私有隔离　", "agent.md 只索引本目录 references/，不引用他专家私有库。"),
    ("跨界上移　", "同时服务多领域的资料统一放 公共知识/案例库/，以软链共享。"),
])

fig_slide("③", "业务协作流", "生产端 → 加工端 → 评价端 → 交付端的真实依赖链", "03-协作流.png", [
    ("主链　", "育种 → 育苗 → 种植 → 发酵 / 食品加工 → 安全 / 营养 → 文档 → 投稿。"),
    ("质谱 → 检测　", "检测管全局标准、前处理与质量体系；质谱管深度环节（选型、碎裂、MRM/HRMS、未知物鉴定）。"),
    ("毒理 → 食品安全　", "毒理产出“毒性凭什么”（POD / HBGV / 证据权重）；食品安全做“是否超标”。"),
    ("风险评估　", "公共技能只回答“风险多大”，三者互不替代。"),
])
s = prs.slides.add_slide(BLANK)
header(s, "④", "进化闭环", "评估 → 复盘 → 固化 → 登记 → 版本化 → 回归")
picture_fit(s, os.path.join(HERE, "04-进化闭环.png"), 0.60, 1.58, 12.13, 1.55)
rect(s, 0.60, 3.45, 12.13, 2.75, RGBColor(0xF5, 0xF8, 0xFA), line=LINE)
bullets(s, 0.90, 3.72, 11.6, [
    ("规则　", "失败一个用例，就应产出一条固化动作。"),
    ("现状　", "15 个 P0 用例（13 专家 + 公共技能）首轮全量评分 15 / 15 通过（自动预评，最终裁定留人工）。"),
    ("治理　", "评分由人工启动、演化决策由人工最终裁定；系统仅记录与可回滚，不自行改文件。"),
    ("基线　", "git tag baseline-2026-10-23 作为演化祖先与回滚点。"),
], size=13.5)

fig_slide("⑤", "部署与加载机制", "install.sh 三种模式与启动加载", "05-部署机制.png", [
    ("默认 link（推荐）　", "软链到 ~/.config/opencode/，任何目录启动 opencode 均可用。"),
    ("--project　", "软链到 MyAgents/.opencode/，项目模式自动加载。"),
    ("--copy　", "复制快照，源更新后需重跑。"),
    ("配置　", "opencode.json：default_agent = orchestrator、skills.paths、references = 公共知识。"),
    ("注意　", "配置与 agent 在启动时加载，不热更新；改动后需重启 opencode。"),
])

# ─────────────────────────────────── 专家清单
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
COLW = [1.45, 1.95, 1.15, 2.55, 5.13]
for tag, rows, sub in (("专家清单（一）农业生产与食品制造", ROWS_A, "6 / 13"),
                       ("专家清单（二）评价、检测与交付", ROWS_B, "7 / 13")):
    s = prs.slides.add_slide(BLANK)
    header(s, None, tag, f"共 13 位：1 个 primary（默认入口）+ 12 个 mode = all（{sub}）")
    table(s, 0.55, 1.55, 12.23, rows, COLW, fs=10.5, rh=0.55)
    footnote(s, "★ = 可执行技能（带脚本，可直接运行）；temp = agent.md 中的 request.body.temperature")

# ─────────────────────────────────── 公共层与边界
s = prs.slides.add_slide(BLANK)
header(s, None, "公共层与边界纪律", "所有专家共用、只读；专家之间不互读私有库")
txbox(s, 0.55, 1.52, 6.0, 0.35, "公共知识（opencode.json 注册为全局 references）", size=14, bold=True, color=NAVY)
table(s, 0.55, 1.95, 6.0, [
    ["分区", "内容"],
    ["政策法规与规划/", "官方政策、规划、批复文件（含盖章件）"],
    ["标准规范/", "标准要点与查询入口（不整篇下载）"],
    ["技术指南/", "通用指南 ＋ L3 原著证据条目 80 条（risk-assessment 底座）"],
    ["案例库/", "跨领域共享案例（多专家软链共享）"],
    ["知识图谱/", "togomcp-sparql 可查 47 个 RDF 数据库"],
    ["书库/", "815 MB 开放获取全文：EHC 240、ICH M7(R2)、SANTE v2026、MDPI 24 册、OECD 指南 17 份、OA 176 篇"],
], [1.5, 4.5], fs=10.5, rh=0.58)
txbox(s, 6.85, 1.52, 5.93, 0.35, "边界纪律（防越界 / 防臆造）", size=14, bold=True, color=NAVY)
bullets(s, 6.85, 2.00, 5.93, [
    ("三问分界　", "风险多大 → 公共技能 risk-assessment；毒性凭什么 → 毒理专家；是否超标 → 食品安全专家。"),
    ("公共库只读　", "各私有库不得写入 公共知识/，内容变更须在 EVOLUTION.md 登记。"),
    ("私有库隔离　", "各专家 agent.md 只索引本目录 references/，不直接引用他人私有库。"),
    ("跨界资料上移　", "多领域共用资料统一上移 公共知识/案例库/，以软链共享，避免重复。"),
    ("引用纪律　", "法规 / 标准 / 限量 / 指导值一律以官方现行文本为准；条目只作方法学锚点。"),
], size=11.5, lead=1.30)

# ─────────────────────────────────── 关键统计与维护
s = prs.slides.add_slide(BLANK)
header(s, None, "关键统计与维护方式", "数值随仓库演进，重跑脚本即可刷新")
table(s, 0.55, 1.55, 6.6, [
    ["指标", "数值"],
    ["Agent 总数", "13（1 primary + 12 mode: all）"],
    ["技能总数", "19（公共 2 + 私有 17，其中可执行 5）"],
    ["公共 L3 证据条目", "80 条"],
    ["三份核心 L3 合计", "258 条（公共 80 + 毒理 104 + 质谱 74）"],
    ["公共书库", "815 MB（EHC 240 / ICH M7(R2) / SANTE v2026 / MDPI 24 / OECD 17 / OA 176）"],
    ["私有书库（册·篇）", "种植 48 · 育种 16 · 育苗 14 · 发酵 34 · 食品加工 118 · 营养 221"],
    ["本地质谱谱库", "人参 1778 · 金线莲 2387 · 合并检索 2954 条"],
    ["评估用例", "15 个 P0，首轮 15 / 15 通过"],
    ["版本基线", "git tag baseline-2026-10-23"],
], [1.9, 4.7], fs=10.5, rh=0.50)
rect(s, 7.45, 1.55, 5.33, 3.55, RGBColor(0xF5, 0xF8, 0xFA), line=LINE)
txbox(s, 7.70, 1.78, 4.9, 0.35, "重新生成", size=14, bold=True, color=NAVY)
txbox(s, 7.70, 2.25, 4.9, 2.6,
      "cd MyAgents/体系图\n"
      "python3 compose_all.py      # 合并全集 PNG\n"
      "python3 make_ppt.py         # 本 PPT\n"
      "\n"
      "# 单张重渲染（改 mmd/*.mmd 后）\n"
      "mmdc -p puppeteer-config.json \\\n"
      "     -i mmd/01-总览.mmd \\\n"
      "     -o 01-总览.png -b white -w 1634 -s 2",
      size=10.5, color=INK, spacing=1.35)
txbox(s, 7.70, 5.30, 4.9, 0.8,
      "改图只改 mmd/*.mmd，再重跑；事实来源仍是各专家\nagent.md 与 SKILL.md。",
      size=10.5, color=GREY, spacing=1.3)

prs.save(OUT)
print(f"{OUT}  {len(prs.slides.__iter__.__self__._sldIdLst)} slides  {os.path.getsize(OUT)//1024} KB")

