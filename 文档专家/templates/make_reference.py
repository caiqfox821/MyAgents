#!/usr/bin/env python3
# 生成「中文宋体 + 英文 Times New Roman + 全黑」的 pandoc reference.docx
# 用法: python3 make_reference.py <pandoc默认reference.docx> <输出.docx>
import re
import shutil
import sys
import zipfile

SRC = sys.argv[1] if len(sys.argv) > 1 else "ref_base.docx"
DST = sys.argv[2] if len(sys.argv) > 2 else "reference-tnr-simsun.docx"

CN = "宋体"
EN = "Times New Roman"

zin = zipfile.ZipFile(SRC)
zout = zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED)

for name in zin.namelist():
    data = zin.read(name)

    # ---------- 1. 主题：字体与配色 ----------
    if name == "word/theme/theme1.xml":
        t = data.decode("utf-8")
        # 配色方案整体黑白化（所有 themeColor 引用都会落到黑/白）
        t = re.sub(r'<a:dk2><a:srgbClr val="[0-9A-Fa-f]{6}" /></a:dk2>',
                   '<a:dk2><a:srgbClr val="000000" /></a:dk2>', t)
        t = re.sub(r'<a:lt2><a:srgbClr val="[0-9A-Fa-f]{6}" /></a:lt2>',
                   '<a:lt2><a:srgbClr val="FFFFFF" /></a:lt2>', t)
        for acc in ("accent1", "accent2", "accent3", "accent4", "accent5",
                    "accent6", "hlink", "folHlink"):
            t = re.sub(r'<a:%s><a:srgbClr val="[0-9A-Fa-f]{6}" /></a:%s>' % (acc, acc),
                       '<a:%s><a:srgbClr val="000000" /></a:%s>' % (acc, acc), t)
        t = re.sub(r'<a:dk1><a:sysClr val="windowText" lastClr="[0-9A-Fa-f]{6}" /></a:dk1>',
                   '<a:dk1><a:sysClr val="windowText" lastClr="000000" /></a:dk1>', t)
        # 字体方案：正文与标题统一
        t = t.replace('<a:majorFont><a:latin typeface="Calibri" /><a:ea typeface="" /><a:cs typeface="" />',
                      '<a:majorFont><a:latin typeface="%s" /><a:ea typeface="%s" /><a:cs typeface="%s" />' % (EN, CN, EN))
        t = t.replace('<a:minorFont><a:latin typeface="Cambria" /><a:ea typeface="" /><a:cs typeface="" />',
                      '<a:minorFont><a:latin typeface="%s" /><a:ea typeface="%s" /><a:cs typeface="%s" />' % (EN, CN, EN))
        t = re.sub(r'<a:majorFont><a:latin typeface="[^"]*" /><a:ea typeface="[^"]*" /><a:cs typeface="[^"]*" />',
                   '<a:majorFont><a:latin typeface="%s" /><a:ea typeface="%s" /><a:cs typeface="%s" />' % (EN, CN, EN), t)
        t = re.sub(r'<a:minorFont><a:latin typeface="[^"]*" /><a:ea typeface="[^"]*" /><a:cs typeface="[^"]*" />',
                   '<a:minorFont><a:latin typeface="%s" /><a:ea typeface="%s" /><a:cs typeface="%s" />' % (EN, CN, EN), t)
        data = t.encode("utf-8")

    # ---------- 2. 样式：字体、颜色、表格线 ----------
    if name == "word/styles.xml":
        s = data.decode("utf-8")

        # 2.1 所有显式文字颜色 → 纯黑
        s = re.sub(r'<w:color\b[^/>]*/>', '<w:color w:val="000000" />', s)
        s = re.sub(r'<w:color\b[^>]*>.*?</w:color>', '<w:color w:val="000000" />', s, flags=re.S)

        # 2.2 默认字体：中文宋体 / 西文 Times New Roman
        s = re.sub(
            r'<w:rFonts\b[^>]*w:asciiTheme="minorHAnsi"[^>]*/>',
            '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:eastAsia="%s" w:cs="%s" />' % (EN, EN, CN, EN),
            s)

        # 2.3 表格：黑色细边框（0.5pt）+ 表头加粗、无底纹
        tbl_old = re.search(r'<w:style w:type="table" w:default="1" w:styleId="Table">.*?</w:style>', s, flags=re.S)
        if tbl_old:
            tbl_new = '''<w:style w:type="table" w:default="1" w:styleId="Table">
    <w:name w:val="Table" />
    <w:basedOn w:val="TableNormal" />
    <w:semiHidden />
    <w:unhideWhenUsed />
    <w:qFormat />
    <w:tblPr>
      <w:tblInd w:w="0" w:type="dxa" />
      <w:tblBorders>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="000000" />
        <w:left w:val="single" w:sz="4" w:space="0" w:color="000000" />
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000" />
        <w:right w:val="single" w:sz="4" w:space="0" w:color="000000" />
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000" />
        <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000" />
      </w:tblBorders>
      <w:tblCellMar>
        <w:top w:w="28" w:type="dxa" />
        <w:left w:w="108" w:type="dxa" />
        <w:bottom w:w="28" w:type="dxa" />
        <w:right w:w="108" w:type="dxa" />
      </w:tblCellMar>
    </w:tblPr>
    <w:tblStylePr w:type="firstRow">
      <w:rPr>
        <w:b />
        <w:bCs />
      </w:rPr>
    </w:tblStylePr>
  </w:style>'''
            s = s.replace(tbl_old.group(0), tbl_new)

        # 2.4 兜底：把残留的彩色底纹（若有）改为无填充
        s = re.sub(r'<w:shd\b[^>]*w:fill="(?!auto|FFFFFF)[0-9A-Fa-f]{6}"[^>]*/>',
                   '<w:shd w:val="clear" w:color="auto" w:fill="auto" />', s)

        data = s.encode("utf-8")

    # ---------- 3. 文档级默认字体（部分模板写在 document defaults） ----------
    if name.startswith("word/") and name.endswith(".xml") and name not in ("word/styles.xml",):
        try:
            t = data.decode("utf-8")
        except UnicodeDecodeError:
            zout.writestr(name, data)
            continue
        if "Calibri" in t or "Cambria" in t:
            t = t.replace('typeface="Calibri"', 'typeface="%s"' % EN)
            t = t.replace('typeface="Cambria"', 'typeface="%s"' % EN)
            data = t.encode("utf-8")

    zout.writestr(name, data)

zout.close()
zin.close()
print("written:", DST)
