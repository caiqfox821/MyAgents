# -*- coding: utf-8 -*-
import csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.sans-serif"] = ["Source Han Sans SC","Noto Sans CJK SC","WenQuanYi Micro Hei"]
plt.rcParams["axes.unicode_minus"] = False

g=defaultdict(list)
for r in csv.DictReader(open("peaks_all.csv",encoding="utf-8")):
    g[r["record"]].append((float(r["mz"]), int(r["relative_intensity"])))

def ann(ax,x,y,txt,dx,dy,ha="left"):
    ax.annotate(txt, xy=(x,y), xytext=(x+dx,y+dy), fontsize=8.5, ha=ha,
                arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9, shrinkA=0, shrinkB=1))

fig,axes=plt.subplots(2,1,figsize=(10,8))
panels=[
 (axes[0],"MSBNK-Univ_Toyama-TY000193","人参皂苷 Rg1  ·  母离子 [M−H]- 799.49（负离子）",
  [(799.49,90,"母离子 [M−H]- = 799.49\n（整个分子少一个 H 原子）",-40,-5,"left"),
   (637.43,95,"丢 1 个葡萄糖（−162 u）\n→ 637.43",-30,15,"left"),
   (475.38,75,"苷元离子 = 475.38\n（再丢 1 个糖；只剩\n原人参三醇 PPT 骨架）",-75,25,"left"),
   (161.04,60,"糖残基小碎片\n(161 / 179 等)", 15,30,"left")]),
 (axes[1],"MSBNK-RIKEN-PR308649","人参皂苷 Rg3  ·  母离子 [M−H]- 783.49（负离子）",
  [(783.49,90,"母离子 [M−H]- = 783.49\n（整个分子少一个 H 原子）",-35,-5,"left"),
   (621.44,60,"丢 1 个葡萄糖（−162 u）\n→ 621.44",-5,45,"left"),
   (459.38,45,"苷元离子 = 459.38\n（原人参二醇 PPD 骨架）",-60,55,"left"),
   (161.04,70,"糖残基小碎片\n(161 / 101 / 113)", 20,25,"left")]),
]
for ax,rid,title,marks in panels:
    pk=sorted(g[rid]); mz=[p[0] for p in pk]; rel=[p[1]/999*100 for p in pk]
    ax.vlines(mz,0,rel,linewidth=1.0,color="#1f5fa8")
    ax.set_ylim(0,135); ax.set_xlim(min(mz)-20, max(mz)+30)
    ax.set_yticks([0,25,50,75,100]); ax.set_ylabel("相对强度 (%)",fontsize=10)
    ax.set_title(title,fontsize=11,loc="left")
    ax.grid(axis="x",ls=":",lw=0.4,alpha=0.5)
    ax.tick_params(labelsize=9)
    for x,y,t,dx,dy,ha in marks:
        ann(ax,x,y,t,dx,dy,ha)
axes[1].set_xlabel("m/z（质荷比）",fontsize=10)
fig.suptitle("怎么看质谱图：横轴 m/z = 离子质量；纵轴 = 相对强度（最强峰 = 100%）",fontsize=11.5,y=0.99)
fig.tight_layout(rect=[0,0,1,0.965])
fig.savefig("讲解_如何看质谱图.png",dpi=150); plt.close(fig); print("wrote 讲解_如何看质谱图.png")

# fragmentation ladder
fig,ax=plt.subplots(figsize=(10,4.2)); ax.axis("off")
def box(x,y,w,h,txt,fc):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02,rounding_size=0.03",
                 fc=fc,ec="#333",lw=1.0))
    ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=9)
def arrow(x1,x2,y,label):
    ax.add_patch(FancyArrowPatch((x1,y),(x2,y),arrowstyle="-|>",mutation_scale=14,color="#555",lw=1.2))
    ax.text((x1+x2)/2,y+0.035,label,ha="center",va="bottom",fontsize=8.5,color="#c0392b")
ax.set_xlim(0,1); ax.set_ylim(0,1)
ax.text(0.02,0.90,"Rg1（PPT 型，C42H72O14）",fontsize=10,fontweight="bold")
box(0.02,0.60,0.22,0.18,"母离子 [M−H]-\n799.49", "#dce9f7")
arrow(0.24,0.40,0.69,"−葡萄糖 162")
box(0.40,0.60,0.20,0.18,"637.43", "#dce9f7")
arrow(0.60,0.74,0.69,"−葡萄糖 162")
box(0.74,0.60,0.24,0.18,"苷元离子 475.38\n（原人参三醇 PPT）", "#f7e3dc")
ax.text(0.02,0.38,"Rg3（PPD 型，C42H72O13）",fontsize=10,fontweight="bold")
box(0.02,0.08,0.22,0.18,"母离子 [M−H]-\n783.49", "#dce9f7")
arrow(0.24,0.40,0.17,"−葡萄糖 162")
box(0.40,0.08,0.20,0.18,"621.44", "#dce9f7")
arrow(0.60,0.74,0.17,"−葡萄糖 162")
box(0.74,0.08,0.24,0.18,"苷元离子 459.38\n（原人参二醇 PPD）", "#f7e3dc")
ax.text(0.5,0.0,"负离子下一层层丢掉糖（每个葡萄糖 162 u），最后剩下苷元骨架——这是皂苷类最典型的碎裂路径。",
        ha="center",fontsize=8.5,color="#444")
ax.set_title("碎裂路径示意：母离子 → 丢糖 → 苷元离子",fontsize=11)
fig.tight_layout()
fig.savefig("讲解_碎片路径.png",dpi=150); plt.close(fig); print("wrote 讲解_碎片路径.png")
