# 长三院简洁模板PPT生成技能

使用"长三院简洁模板"生成指定内容的PowerPoint演示文稿。

## 模板信息

- **模板文件**: `data/长三院简洁模板.pot` (PowerPoint 97-2003 模板格式)
- **创建工具**: WPS
- **作者**: 浙江清华长三角研究院
- **页面尺寸**: 标准 4:3 (25.4cm x 19.05cm / 10in x 7.5in)
- **主题名称**: Office 主题

### 颜色方案

从模板中提取的主题色（通过分析模板二进制数据）:

- 主色: 深蓝色系 (标题/装饰)
- 辅色: 灰色/白色 (背景/正文)
- 强调色: 模板内置 Office 主题色

### 字体方案

| 用途 | 西文 | 中文 |
|------|------|------|
| 标题 | Arial / Calibri | 微软雅黑 |
| 正文 | Times New Roman | 思源黑体 / 等线 |

### 布局结构

模板包含以下页面类型:

1. **封面页** (Layout: `1_Office 主题`)
   - 标题占位符
   - 副标题/作者占位符 ("浙江清华长三角研究院")
   - 装饰性矩形 + 图片

2. **目录/分隔页**
   - 居中标题
   - 装饰元素

3. **正文内容页** (Layout: `2_Office 主题`)
   - 顶部标题占位符
   - 正文文本占位符
   - 页脚/页码

4. **内容页变体** (Layout: `4_Office 主题`, `7_Office 主题`)
   - 标题 + 多级文本
   - 可用于表格/图表

5. **结尾页**
   - "感谢各位专家"
   - "敬请批评指正"
   - 研究院标识

## 生成PPT的工作流

### 第一步：准备内容

从HTML/Markdown源文件中提取结构化内容:

- 标题（一级标题）
- 章节标题（二级标题）
- 小节标题（三级标题）
- 正文段落
- 列表项
- 表格
- 公式（可选，用文本描述替代）

### 第二步：安装依赖

```bash
pip install python-pptx
```

### 第三步：代码生成模板

使用 `python-pptx` 库，基于模板样式生成PPT。关键代码结构:

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import re

# 打开模板 (需要先另存为 .potx 或用 Presentation 打开)
# 注意: .pot 是旧格式, python-pptx 无法直接打开。
# 解决方案: 用WPS/Office将 .pot 另存为 .potx 或 .pptx,
# 或创建一个匹配模板风格的 .pptx 文件
prs = Presentation("data/长三院简洁模板.pptx")

# 页面尺寸: 4:3
# prs.slide_width = Emu(9144000)   # 10 inches
# prs.slide_height = Emu(6858000)  # 7.5 inches

# ===== 辅助函数 =====

def add_title_slide(prs, title, subtitle="", author="蔡强", institute="浙江清华长三角研究院"):
    """创建封面页"""
    slide = prs.slides.add_slide(prs.slide_layouts[0])  # 使用封面布局
    # 设置标题
    if slide.shapes.title:
        slide.shapes.title.text = title
    # 设置副标题/其他占位符
    for shape in slide.placeholders:
        if "Title" in shape.name:
            shape.text = title
        elif "Text" in shape.name:
            shape.text = f"{author}\n{institute}"
    return slide

def add_content_slide(prs, title, content_items):
    """创建正文内容页"""
    slide = prs.slides.add_slide(prs.slide_layouts[1])  # 使用正文布局
    if slide.shapes.title:
        slide.shapes.title.text = title
    # 填充正文内容
    for shape in slide.placeholders:
        if "Text" in shape.name:
            tf = shape.text_frame
            tf.clear()
            for i, item in enumerate(content_items):
                if i == 0:
                    tf.paragraphs[0].text = item
                else:
                    p = tf.add_paragraph()
                    p.text = item
    return slide

def set_font(run, name_cn='微软雅黑', name_en='Arial', size=Pt(14), bold=False, color=None):
    """设置字体"""
    run.font.name = name_en
    run.font.size = size
    run.font.bold = bold
    if color:
        run.font.color.rgb = color

# ===== 内容渲染规则 =====

# 一级标题 -> 封面页
# 二级标题 -> 分隔页 或 内容页标题
# 三级标题 -> 内容页小标题
# 正文 + 列表 + 表格 -> 内容页正文

# ===== 样式参数 =====

TITLE_COLOR = RGBColor(0x1A, 0x3C, 0x6E)      # 深蓝 (标题色)
BODY_COLOR = RGBColor(0x33, 0x33, 0x33)       # 深灰 (正文字色)
ACCENT_COLOR = RGBColor(0x2E, 0x75, 0xB6)     # 蓝色 (强调色)
BG_COLOR = RGBColor(0xFF, 0xFF, 0xFF)         # 白色 (背景)
```

### 第四步：内容映射规则

从HTML到PPT的映射逻辑:

| HTML元素 | PPT元素 |
|----------|---------|
| `<h1>` (文章标题) | **封面页** - 大标题居中 |
| `<h2>` (章节标题: 绪论/结论等) | **分隔页** 或 **内容页标题** |
| `<h3>` (小节标题: 2.1 Logistic等) | **内容页标题** |
| `<p>` (正文) | 正文文本框（缩进/分段） |
| `<table>` | 表格（每行对应PPT表格行） |
| `<ul>/<ol>` 列表 | 项目符号列表 |
| `<strong>` 加粗 | 加粗文本 |
| 关键引用 `(作者, 年份)` | 保持原文格式 |

### 第五步：生成PPT

```python
def build_presentation(html_content):
    prs = Presentation("data/长三院简洁模板.pptx")

    # 1. 封面
    add_title_slide(prs, "植物生长模型研究进展\n——模型溯源、田间实验与应用评述",
                    subtitle="", author="蔡强", institute="浙江清华长三角研究院")

    # 2. 目录页
    toc_items = ["1 绪论", "2 经验统计模型", "3 过程机理模型",
                  "4 机器学习模型", "5 混合模型",
                  "6 功能-结构植物模型", "7 模型校准方法", "8 结论"]
    add_content_slide(prs, "目 录", toc_items)

    # 3. 逐章节渲染
    # 每个 <h2> 作为一个章节
    # 每个 <h3> 作为一页内容
    # 正文、表格、列表作为该页的内容

    # 4. 结尾页
    add_content_slide(prs, "感谢各位专家\n敬请批评指正",
                     ["蔡强", "浙江清华长三角研究院"])

    prs.save("output.pptx")
    return "output.pptx"
```

### 第六步：样式微调

- 标题字号: 封面 36-44pt, 内容页标题 28-32pt, 小标题 20-24pt
- 正文字号: 14-18pt
- 表格字号: 12-14pt
- 行距: 1.2-1.5倍
- 页面间距: 上下左右留白约1英寸
- 表格样式: 简洁线框, 表头加粗/底色

## 注意事项

1. **模板兼容性**: `python-pptx` 不支持直接打开 `.pot` (97-2003格式)。先用 WPS/Office 将 `.pot` 另存为 `.potx` 或 `.pptx`。
2. **公式处理**: HTML中的LaTeX公式用文本描述或截图替代。
3. **图片处理**: 模板中的装饰图片（如 `Untitled-3.jpg`）在生成时需保留或替换。
4. **字体回退**: 中文推荐"微软雅黑"，西文推荐"Arial"或"Calibri"。
5. **表格渲染**: 复杂表格需逐行逐单元格填充，注意合并单元格处理。