# -*- coding: utf-8 -*-
"""WGCNA：加权基因共表达网络分析与模块-性状关联"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1500, 1000)
c.title("WGCNA：模块识别与模块-性状关联", size=30)

# ---------- 左：基因层次聚类树 + 模块色带 ----------
c.text(360, 140, "① 基因层次聚类树（Topological Overlap）", size=15, bold=True)

# 手绘简化聚类树：8 个叶，两两聚枝，再聚成 2 大枝
leaves = [(150, 560), (215, 560), (280, 560), (345, 560),
          (410, 560), (475, 560), (540, 560), (605, 560)]
# 第一层 merge（高度 y=480）
m1 = [(182, 480), (312, 480), (442, 480), (572, 480)]
# 第二层（y=380）
m2 = [(247, 380), (507, 380)]
# 根（y=300）
root = (377, 300)
for (x, y), (mx, my) in zip(leaves, [m1[0], m1[0], m1[1], m1[1], m1[2], m1[2], m1[3], m1[3]]):
    c.line(x, y, x, my, color=C["ink"], width=1.8)
    c.line(x, my, mx, my, color=C["ink"], width=1.8)
for (mx, my), (nx, ny) in zip(m1, [m2[0], m2[0], m2[1], m2[1]]):
    c.line(mx, my, mx, ny, color=C["ink"], width=1.8)
    c.line(mx, ny, nx, ny, color=C["ink"], width=1.8)
for (nx, ny) in m2:
    c.line(nx, ny, nx, root[1], color=C["ink"], width=1.8)
    c.line(nx, root[1], root[0], root[1], color=C["ink"], width=1.8)

# 动态剪切：模块色带
bands = [("turquoise", "#40B5AD", 150, 130), ("brown", "#A5673E", 280, 130),
         ("blue", "#3A89C8", 410, 130), ("green", "#84B545", 540, 130)]
for name, col, bx, bw in bands:
    c.rect(bx, 600, bw, 26, fill=col)
    c.text(bx + bw/2, 645, name, size=12, bold=True)
c.text(360, 675, "④ 动态剪切 → 基因共表达模块", size=13, fill=C["gray"])

# 流程注解
flow = ["② 软阈值 β 选择（无尺度拓扑）", "③ 构建邻接矩阵 → TOM", "⑤ 计算模块特征基因 ME"]
for i, t in enumerate(flow):
    c.text(150, 745 + i * 36, "· " + t, size=13.5, anchor="start")

# ---------- 右：模块-性状关联热图 ----------
c.text(1120, 140, "⑥ 模块-性状关联热图（相关系数 r）", size=15, bold=True)
traits = ["体重", "血糖", "炎症 IL-6", "预后"]
mods = [("turquoise", "#40B5AD"), ("brown", "#A5673E"), ("blue", "#3A89C8"), ("green", "#84B545")]
rmat = [
    [ 0.62, -0.48,  0.35, -0.55],
    [-0.31,  0.58,  0.44, -0.28],
    [ 0.45,  0.71, -0.36,  0.64],
    [-0.22, -0.35,  0.29,  0.31],
]
HX0, HY0, CS = 980, 220, 118
def rcolor(r):
    t = min(1.0, max(0.0, (r + 1) / 2))
    a = [int("#3A89C8"[i:i+2], 16) for i in (1, 3, 5)]
    b = [int("#D64550"[i:i+2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a[i]+(b[i]-a[i])*t):02x}" for i in range(3))

for j, tr in enumerate(traits):
    c.text(HX0 + CS/2 + j * CS, HY0 - 16, tr, size=13, bold=True)
for i, (mname, mcol) in enumerate(mods):
    c.rect(HX0 - 170, HY0 + i * CS + CS/2 - 11, 22, 22, fill=mcol)
    c.text(HX0 - 138, HY0 + i * CS + CS/2 + 5, mname, size=12, anchor="start")
    for j, r in enumerate(rmat[i]):
        c.rect(HX0 + j * CS, HY0 + i * CS, CS - 4, CS - 4, fill=rcolor(r))
        c.text(HX0 + j * CS + (CS - 4)/2, HY0 + i * CS + CS/2 - 2, f"{r:.2f}",
               size=13, bold=True, fill="#FFFFFF" if abs(r) > 0.55 else "#1F2937")

# 色标条
for k in range(20):
    t = k / 19
    c.rect(980 + k * 14, 750, 14, 18, fill=rcolor(t * 2 - 1))
c.text(980, 792, "-1（负相关）", size=12, anchor="start", fill=C["gray"])
c.text(1260, 792, "+1（正相关）", size=12, anchor="end", fill=C["gray"])

# ---------- 底：hub 基因 ----------
c.add("group_box", 150, 900, w=620, h=0, label=None, color=C["gray"]) if False else None
c.text(150, 880, "⑦ Hub 基因筛选：kME/模块内连接度 Top 基因 → 后续验证", size=14, bold=True, anchor="start")
c.text(150, 920, "常用图：模块特征基因-性状散点图（带拟合线与相关系数）", size=13, fill=C["gray"], anchor="start")
c.text(980, 880, "解读：brown 模块与血糖（r=0.71）、预后（r=0.64）", size=13.5, anchor="start")
c.text(980, 912, "高度相关 → 优先深入该模块", size=13.5, anchor="start")

c.add("legend_row", 980, 955, items=[("#40B5AD", "turquoise"), ("#A5673E", "brown"),
                                     ("#3A89C8", "blue"), ("#84B545", "green")], size=13)

c.save(os.path.join(OUT, "wgcna_modules.svg"))
c.export(os.path.join(OUT, "wgcna_modules"), formats=("png",), dpi=300)
print("wgcna done")
