# -*- coding: utf-8 -*-
"""把人参皂苷 Rg1/Rg3 质谱讲解生成为 Word (.docx)，图片内嵌。"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BODY_EA, HEAD_EA, MONO = "宋体", "黑体", "Consolas"

def set_cjk(run, ea=BODY_EA, ascii_font="Times New Roman"):
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), ea)

def style_base(doc):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"; st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_EA)
    pf = st.paragraph_format; pf.space_after = Pt(4); pf.line_spacing = 1.25
    for name, sz in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11.5)):
        s = doc.styles[name]
        s.font.name = "Times New Roman"; s.font.size = Pt(sz); s.font.bold = True
        s.font.color.rgb = RGBColor(0x1F, 0x3B, 0x63)
        s.element.rPr.rFonts.set(qn("w:eastAsia"), HEAD_EA)

def para(doc, text="", bold=False, italic=False, size=10.5, align=None, color=None, ae=None):
    p = doc.add_paragraph()
    if align is not None: p.alignment = align
    r = p.add_run(text); r.bold = bold; r.italic = italic; r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    set_cjk(r, ea=ae or BODY_EA)
    return p

def h(doc, level, text):
    p = doc.add_heading(text, level=level); return p

def bullet(doc, text, bold_head=None):
    p = doc.add_paragraph(style="List Bullet")
    if bold_head:
        r0 = p.add_run(bold_head); r0.bold = True; set_cjk(r0)
    r = p.add_run(text); set_cjk(r)
    return p

def code_block(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(6)
    for i, line in enumerate(text.split("\n")):
        r = p.add_run(line)
        r.font.name = MONO; r.font.size = Pt(8.5)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), MONO)
        if i < len(text.split("\n")) - 1: r.add_break()
    # 底纹
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "F4F6F8")
    p._p.get_or_add_pPr().append(shd)

def add_table(doc, headers, rows):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, txt in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(txt); r.bold = True; set_cjk(r, ea=HEAD_EA)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row in rows:
        cells = t.add_row().cells
        for i, txt in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(txt)); set_cjk(r)
    doc.add_paragraph()
    return t

def add_image(doc, path, caption, width_cm=15.5):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Cm(width_cm))
    cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption); r.font.size = Pt(9); r.italic = True
    r.font.color.rgb = RGBColor(0x55, 0x55, 0x55); set_cjk(r)

# ---------------- 生成 ----------------
doc = Document()
style_base(doc)
sec = doc.sections[0]
sec.top_margin = sec.bottom_margin = Cm(2.2); sec.left_margin = sec.right_margin = Cm(2.4)

title = doc.add_paragraph(); title.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title.add_run("人参皂苷 Rg1 / Rg3 质谱图怎么看（入门讲解）")
tr.bold = True; tr.font.size = Pt(18); tr.font.color.rgb = RGBColor(0x1F,0x3B,0x63)
set_cjk(tr, ea=HEAD_EA)

note = doc.add_paragraph(); note.alignment = WD_ALIGN_PARAGRAPH.CENTER
nr = note.add_run("数据来源：MassBank 参考谱库 ｜ 检索日期：2026-10-23 ｜ 化合物：人参皂苷 Rg1、Rg3")
nr.font.size = Pt(9); nr.italic = True; nr.font.color.rgb = RGBColor(0x66,0x66,0x66); set_cjk(nr)

h(doc, 1, "一、质谱图像什么？")
para(doc, "把它想成给分子“称重 + 排队”：分子先带上电，再按“体重”从轻到重排好，哪种离子多、哪根线就高。")
code_block(doc, "相对强度(%)\n"
                " 100 |                     █         ← 最高的峰叫\"基峰\"，定为 100%\n"
                "     |                  █  █\n"
                "  50 |          █    █  █  █\n"
                "     |      █   █    █  █  █\n"
                "   0 +------█---█----█--█--█---------\n"
                "          100 161  475 637 799   →  m/z（质量）\n"
                "      （小碎片）（苷元）  （母离子：靠右、最大）")

h(doc, 1, "二、两个坐标轴")
add_table(doc, ["轴", "含义", "怎么理解"], [
    ["横轴 m/z", "质荷比 = 离子的质量", "这根离子有多重（单位 Da）。离子一般带 1 个电荷，所以 m/z ≈ 质量"],
    ["纵轴 相对强度 (%)", "该离子有多少", "把最强的那根定为 100%，其余按比例画。不用管绝对值，只看“哪些质量的离子多”"],
    ["一根竖线", "一种离子", "每根线对应一个确定的 m/z"],
])

h(doc, 1, "三、一张谱图分三块看")
add_table(doc, ["位置", "是什么", "说明"], [
    ["最右边的大峰", "母离子", "整个分子带个电、还没碎（如 Rg1 的 799.49）"],
    ["中间", "碎片离子", "掉了 1~2 个糖（如 637.43、475.38）"],
    ["左下角小峰", "糖残基", "糖本身碎成的小片（161、179、101、113 等）"],
])
para(doc, "核心机理：ESI 是“温柔”的电离——不把分子打碎，只让它带上电，得到右边的母离子；再给它一点能量，它就像掰积木一样一个个把糖掰下来（每掰掉一个葡萄糖 = 少 162 u），最后剩下光秃秃的骨架，叫苷元。")
add_image(doc, "讲解_碎片路径.png", "图 1  碎裂路径示意：母离子 → 丢糖 → 苷元离子")

h(doc, 1, "四、带标注的谱图")
add_image(doc, "讲解_如何看质谱图.png", "图 2  Rg1（上）与 Rg3（下）谱图讲解，红色箭头标出每个关键峰的含义")

h(doc, 1, "五、Rg1 逐峰解读（母离子 799.49）")
add_table(doc, ["峰 m/z", "含义", "怎么算出来的"], [
    ["799.49", "完整分子（少一个氢带负电）", "Rg1 分子重 800.49，丢 1 个 H"],
    ["637.43", "掉 1 个葡萄糖", "799.49 − 162（葡萄糖）"],
    ["475.38", "掉光 2 个糖，剩骨架（原人参三醇 PPT）", "637.43 − 162"],
    ["161 / 179", "糖残基碎片", "葡萄糖自身碎裂"],
])

h(doc, 1, "六、Rg3 逐峰解读（母离子 783.49）")
add_table(doc, ["峰 m/z", "含义", "怎么算出来的"], [
    ["783.49", "完整分子（比 Rg1 少一个氧，所以轻 16）", "Rg3 分子重 784.49，丢 1 个 H"],
    ["621.44", "掉 1 个葡萄糖", "783.49 − 162"],
    ["459.38", "掉光 2 个糖，剩骨架（原人参二醇 PPD）", "621.44 − 162"],
    ["101 / 113 / 161", "糖残基碎片", "糖自身碎裂"],
])

h(doc, 1, "七、Rg1 和 Rg3 差在哪里？")
para(doc, "看两张图能直接发现：每一步都刚好差 16。")
add_table(doc, ["步骤", "Rg1", "Rg3", "差值"], [
    ["母离子", "799.49", "783.49", "16"],
    ["掉 1 个糖", "637.43", "621.44", "16"],
    ["苷元", "475.38", "459.38", "16"],
])
para(doc, "差的这 16 就是一个氧原子——Rg1 的骨架（原人参三醇 PPT）比 Rg3 的骨架（原人参二醇 PPD）多一个氧。分子式也对应：Rg1 = C42H72O14，Rg3 = C42H72O13。")
add_image(doc, "Rg1_mass_spectra.png", "图 3  Rg1 四张参考谱（叠放）")
add_image(doc, "Rg3_mass_spectra.png", "图 4  Rg3 四张参考谱（叠放）")

h(doc, 1, "八、几个常见疑惑")
bullet(doc, "那是同位素峰。自然界的碳约 1% 是碳-13，分子里碳很多（Rg1 有 42 个碳），就有一部分分子重 1 个单位。正常现象，不是杂质。", bold_head="为什么 799.49 旁边还有一根 800.49？")
bullet(doc, "因为可以做不同实验：加合物不同（有的让分子“丢 H”，有的让它“抓一个甲酸根”）；层级不同（MS1 只测完整分子，MS2 把分子打碎后看碎片）。同一化合物的不同实验，碎片规律是一致的。", bold_head="为什么一共给了 8 张谱？")
bullet(doc, "能量高时母离子被“打光”，碎片峰反而更高（例如 Rg1 的第一张谱里，637 比 799 还高）。", bold_head="为什么有时最右边的大峰不是最高的？")

h(doc, 1, "九、这张图有什么用？")
bullet(doc, "每种分子的碎片组合像指纹，拿去和谱库比对就能确认是不是 Rg1。", bold_head="认人（定性）：")
bullet(doc, "选“母离子 799.49 → 碎片 475.38”这样一对离子来测——这就是《MRM 通道建议》里推荐通道的由来。", bold_head="定量（做 MRM）：")

end = doc.add_paragraph(); end.alignment = WD_ALIGN_PARAGRAPH.CENTER
er = end.add_run("—— 本讲解由质谱专家整理；谱图为 MassBank 实测参考谱，检索日 2026-10-23 ——")
er.font.size = Pt(8.5); er.italic = True; er.font.color.rgb = RGBColor(0x88,0x88,0x88); set_cjk(er)

cp = doc.core_properties
cp.title = "人参皂苷 Rg1/Rg3 质谱图怎么看（入门讲解）"
cp.subject = "MassBank 参考谱解读"
cp.author = "质谱专家"

out = "讲解_怎么看质谱图.docx"
doc.save(out)
print("saved", out)
