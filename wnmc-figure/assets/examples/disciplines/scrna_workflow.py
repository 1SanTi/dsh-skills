# -*- coding: utf-8 -*-
"""单细胞转录组：scRNA-seq 工作流与细胞类型聚类"""
import os, sys, random, math
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

random.seed(7)
c = Canvas(1500, 1000)
c.title("单细胞 RNA 测序（scRNA-seq）工作流", size=30)

# ---------- 上排：湿实验 4 步 ----------
Y1 = 330

# ① 组织
c.add("group_box", 190, Y1, w=200, h=190, label=None, color=C["gray"], fill="#FDF7F4")
c.text(190, 225, "① 组织", size=14, bold=True, anchor="start")
c.add("cell_epithelial", 145, Y1 + 70, w=44, h=72, label=None)
c.add("fibroblast", 230, Y1 + 65, w=62, h=44, label=None)
c.add("lymphocyte", 160, Y1 + 140, r=18, label=None)
c.add("macrophage", 245, Y1 + 135, r=22, label=None)

c.arrow(305, Y1, 360, Y1, kind="activation", label="酶解")

# ② 单细胞悬液
c.text(455, 225, "② 单细胞悬液", size=14, bold=True, anchor="start")
for i, (dx, dy, r) in enumerate([(-30, -20, 15), (18, -34, 12), (30, 12, 14), (-22, 26, 12), (8, 36, 13)]):
    c.circle(465 + dx, Y1 + dy, r, fill=C["blue_l"], stroke=C["blue"], width=1.6)
    c.circle(465 + dx + 4, Y1 + dy - 4, r * 0.34, fill=C["purple_l"], stroke=C["purple"], width=1.0)

c.arrow(560, Y1, 620, Y1, kind="activation", label="10x 平台")

# ③ 液滴捕获 GEM
c.text(700, 225, "③ 液滴捕获（GEM）", size=14, bold=True, anchor="start")
for i in range(3):
    gx, gy = 700 + (i % 2) * 78, Y1 + (i // 2) * 95
    c.circle(gx, gy, 34, fill="#FFF6E8", stroke=C["orange"], width=2.0)
    c.circle(gx - 12, gy + 8, 15, fill=C["blue_l"], stroke=C["blue"], width=1.4)
    c.circle(gx + 13, gy - 10, 11, fill=C["yellow"], stroke=C["orange"], width=1.4)
c.text(872, Y1 + 85, "凝胶珠(条形码)", size=11, fill=C["gray"])

c.arrow(875, Y1, 935, Y1, kind="activation", label="建库")

# ④ 测序
c.text(1010, 225, "④ 文库测序", size=14, bold=True, anchor="start")
c.add("group_box", 1010, Y1, w=170, h=190, label=None, color=C["gray"], fill="#F7FAFD")
c.rect(1030, Y1 - 40, 130, 26, fill=C["blue_l"], stroke=C["blue"], width=1.5)
c.text(1095, Y1 - 24, "Flow Cell", size=12, bold=True)
for i in range(4):
    c.rect(1030, Y1 - 45 + i * 30, 130, 22, fill=C["gray_l"], stroke=C["gray"], width=1.0)
    c.text(1095, Y1 - 31 + i * 30, f"Read {i+1}", size=11)

# ---------- 下排：生信分析 + UMAP ----------
c.arrow(1095, Y1 + 105, 1095, 460, kind="activation", label="Cell Ranger")

c.add("group_box", 1120, 660, w=560, h=290, label=None, color=C["teal"], fill="#F6FBFA")
c.text(870, 545, "⑤ 数据分析", size=15, bold=True, anchor="start")

# UMAP 散点
umap_cx, umap_cy = 1130, 650
clusters = [
    ("T 细胞",   C["orange"], -90, -70),
    ("B 细胞",   C["purple"],  60, -95),
    ("巨噬细胞", C["teal"],   -35,  70),
    ("上皮细胞", C["blue"],   130,  30),
    ("成纤维细胞", C["green"], 40, 95),
]
for name, col, dx, dy in clusters:
    cx, cy = umap_cx + dx, umap_cy + dy
    c.circle(cx, cy, 52, fill="none", stroke=col, width=1.6, )
    for k in range(8):
        ang = random.random() * 6.283
        rr = random.random() * 40
        c.circle(cx + rr * math.cos(ang), cy + rr * math.sin(ang), 6, fill=col)
    c.text(cx, cy - 62, name, size=12.5, bold=True)

c.text(1450, 780, "UMAP 降维", size=13, bold=True, anchor="end")
c.text(1450, 806, "每个点 = 1 个细胞", size=11.5, fill=C["gray"], anchor="end")

# 分析产出
for i, t in enumerate(["差异表达基因 (DEG)", "通路富集 (GSVA/GSEA)", "细胞通讯 (CellChat)", "拟时序 (Monocle)"]):
    c.add("group_box", 610, 540 + i * 92, w=330, h=64, label=None, color=C["gray"], fill="#FAFAFA")
    c.text(610, 545 + i * 92, t, size=13.5, bold=True)

c.add("legend_row", 620, 950, items=[
    (C["orange"], "T 细胞"), (C["purple"], "B 细胞"), (C["teal"], "巨噬细胞"),
    (C["blue"], "上皮细胞"), (C["green"], "成纤维细胞")], size=14)
c.text(300, 950, "常用平台：10x Genomics Chromium、Smart-seq2", size=13, fill=C["gray"], anchor="start")

c.save(os.path.join(OUT, "scrna_workflow.svg"))
c.export(os.path.join(OUT, "scrna_workflow"), formats=("png",), dpi=300)
print("scrna done")
