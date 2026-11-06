# -*- coding: utf-8 -*-
"""空间转录组：组织切片上的基因表达空间图谱（中心锚点版）"""
import os, sys, math
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

def mix(c1, c2, t):
    a = [int(c1[i:i+2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i+2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a[i]+(b[i]-a[i])*t):02x}" for i in range(3))

c = Canvas(1500, 1000)
c.title("空间转录组学：保留位置信息的基因表达图谱", size=29)

# ---------- 左：组织切片 + 捕获点阵 ----------
SX, SY, SW, SH = 80, 170, 500, 610
c.rect(SX, SY, SW, SH, fill="#FBEFEA", stroke=C["ink"], width=2.0)
c.text(SX + SW / 2, SY - 16, "组织切片 + 空间捕获芯片（Visium）", size=15, bold=True)
for (dx, dy, r) in [(140, 250, 55), (360, 320, 78), (230, 480, 92), (420, 550, 50)]:
    c.circle(SX + dx, SY + dy, r, fill="#F5D9C8")
for ix in range(10):
    for iy in range(12):
        px = SX + 45 + ix * 45
        py = SY + 42 + iy * 45
        t = min(1.0, max(0.0, ((px - SX) / SW + (py - SY) / SH) / 2 + 0.15))
        c.circle(px, py, 12, fill=mix("#2A9D8F", "#D64550", t))

# ---------- 中：两基因表达图 ----------
for k, (gene, tint) in enumerate([("基因 A（基质标记）", "#2A9D8F"),
                                   ("基因 B（肿瘤标记）", "#D64550")]):
    bx = 640 + k * 320
    c.rect(bx, 170, 250, 300, fill="#FDFDFD", stroke=C["gray"], width=1.5)
    c.text(bx + 125, 156, gene, size=13, bold=True)
    for ix in range(5):
        for iy in range(6):
            px = bx + 35 + ix * 45
            py = 210 + iy * 45
            v = 0.5 + 0.45 * math.sin(px / 40 + (0 if k else 1.2)) * math.cos(py / 45)
            v = min(1.0, max(0.0, v))
            c.circle(px, py, 11, fill=mix("#F2F2F2", tint, v))
# 色标
c.rect(640, 505, 125, 20, fill=mix("#F2F2F2", "#2A9D8F", 0.5))
c.rect(765, 505, 125, 20, fill=mix("#F2F2F2", "#2A9D8F", 1.0))
c.text(640, 548, "低", size=11.5, fill=C["gray"], anchor="start")
c.text(890, 548, "高", size=11.5, fill=C["gray"], anchor="end")

# ---------- 右：分析流程 ----------
steps = ["逆转录 + 二代测序", "比对与计数（Space Ranger）",
         "与 H&E 图像配准", "空间聚类 / 去卷积", "配体-受体空间互作"]
for i, s in enumerate(steps):
    cy = 220 + i * 100
    c.add("group_box", 1330, cy, w=300, h=64, label=None, color=C["purple"], fill="#FAF8FD")
    c.text(1330, cy - 4, "②③④⑤⑥"[i] + " " + s, size=12.8, bold=True)
    if i < 4:
        c.arrow(1330, cy + 33, 1330, cy + 67, kind="activation")

# ---------- 下中：空间生态位 ----------
c.add("group_box", 940, 690, w=440, h=240, label=None, color=C["teal"], fill="#F6FBFA")
c.text(940, 598, "空间生态位解读（示例）", size=14, bold=True)
c.circle(800, 665, 22, fill=mix("#F2F2F2", "#D64550", 0.85))
c.text(800, 715, "肿瘤巢", size=12.5, bold=True)
c.circle(940, 665, 22, fill=mix("#F2F2F2", "#2A9D8F", 0.5))
c.text(940, 715, "癌旁基质", size=12.5, bold=True)
c.circle(1080, 665, 22, fill="#FDFDFD", stroke=C["gray"], width=1.5)
c.text(1080, 715, "正常组织", size=12.5, bold=True)
c.arrow(824, 665, 916, 665, kind="bidirectional", label="通讯")
c.arrow(964, 665, 1056, 665, kind="bidirectional")

c.add("legend_row", 620, 880, items=[
    ("#2A9D8F", "基因 A 高表达区"), ("#D64550", "基因 B 高表达区"),
    (C["gray"], "每个点 = 一个捕获 spot")], size=13.5)
c.text(940, 940, "一个 spot = 若干细胞的表达均值；分辨率由芯片点径决定",
       size=12, fill=C["gray"])

c.save(os.path.join(OUT, "spatial_transcriptomics.svg"))
c.export(os.path.join(OUT, "spatial_transcriptomics"), formats=("png",), dpi=300)
print("spatial done")
