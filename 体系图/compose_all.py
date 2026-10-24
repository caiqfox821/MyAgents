#!/usr/bin/env python3
# 把 5 张体系图拼成一张纵向全集 PNG。
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = [
    ("01-总览.png", "① 体系总览", "入口层 → 12 领域专家 → 支撑层 → 交付物 + 进化闭环"),
    ("02-分层.png", "② 分层与边界", "私有事实来源 / 公共只读层 / 全局内置 / 边界纪律"),
    ("03-协作流.png", "③ 业务协作流", "生产端 → 加工端 → 评价端 → 交付端的真实依赖链"),
    ("04-进化闭环.png", "④ 进化闭环", "评估 → 复盘 → 固化 → 登记 → 版本化 → 回归"),
    ("05-部署机制.png", "⑤ 部署与加载机制", "install.sh 三种模式与启动加载"),
]
W = 1680            # 内容区宽度
PAD = 48            # 页面外边距
GAP = 40            # 图间距
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
f_title = ImageFont.truetype(FONT_B, 84)
f_sub   = ImageFont.truetype(FONT_R, 40)
f_h     = ImageFont.truetype(FONT_B, 56)
f_desc  = ImageFont.truetype(FONT_R, 36)
f_foot  = ImageFont.truetype(FONT_R, 32)

# 先量算总高度
head_h = 84 + 60 + 46 + 60
scaled, heights, blocks = [], [], 0
for png, title, desc in PANELS:
    im = Image.open(os.path.join(HERE, png)).convert("RGB")
    h = round(im.height * W / im.width)
    scaled.append(im.resize((W, h), Image.LANCZOS))
    heights.append(h)
    blocks += 70 + h + 46 + GAP   # 小标题 + 图 + 说明 + 间距
foot_h = 70
H = PAD * 2 + head_h + blocks + foot_h

canvas = Image.new("RGB", (W + PAD * 2, H), "white")
d = ImageDraw.Draw(canvas)

def center(text, y, font, fill):
    w = d.textlength(text, font=font)
    d.text(((canvas.width - w) / 2, y), text, font=font, fill=fill)

# 页头
y = PAD
center("MyAgents 专家 Agent 体系图", y, f_title, "#0D47A1"); y += 84 + 24
center("健康食品与现代农业 · opencode 领域专家库", y, f_sub, "#37474F"); y += 60
center("13 agent（1 primary + 12 all）· 19 技能（公共 2 + 私有 17）· 公共知识只读 · 进化闭环人工裁定", y, f_desc, "#546E7A")
y += 46 + 24
d.line([(PAD, y), (canvas.width - PAD, y)], fill="#B0BEC5", width=3)
y += 60

for (png, title, desc), im, h in zip(PANELS, scaled, heights):
    d.text((PAD, y), title, font=f_h, fill="#1565C0"); y += 70
    canvas.paste(im, (PAD, y)); y += h + 12
    d.text((PAD, y), desc, font=f_desc, fill="#607D8B"); y += 46 + 34
    d.line([(PAD, y - 16), (canvas.width - PAD, y - 16)], fill="#E0E0E0", width=2)
    y += GAP

center("基线 baseline-2026-10-23 · 模型 paratera/DeepSeek-V4-Flash · 由 mmd/*.mmd 渲染合成",
       y, f_foot, "#90A4AE")

out = os.path.join(HERE, "MyAgents-体系图-全集.png")
canvas.save(out, optimize=True)
print(f"{out}  {canvas.width}x{canvas.height}px  {os.path.getsize(out)//1024} KB")
