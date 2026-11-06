# -*- coding: utf-8 -*-
"""基础医学：急性炎症反应（血管通透性与白细胞渗出）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("急性炎症反应：血管变化与白细胞渗出", size=30)

# 血管（横贯）
VY = 430
c.path("M 120 330 Q 700 260 1280 330 L 1280 530 Q 700 600 120 530 Z",
       fill="#FBEFEA", stroke=C["red"], width=2.6)
c.text(700, 235, "小静脉（扩张、血流淤滞）", size=14, bold=True, fill=C["red"])
# 血管内细胞
c.add("rbc", 300, 470, r=24)
c.add("rbc", 480, 430, r=22)
c.add("rbc", 1080, 450, r=24)
c.add("neutrophil", 250, 360, r=32, label=None)
c.add("neutrophil", 350, 350, r=32, label=None)
c.add("neutrophil", 900, 360, r=32, label=None)
c.text(700, 640, "管腔内：红细胞 + 边集的中性粒细胞", size=13, fill=C["gray"])

# 内皮间隙与渗出
c.line(545, 292, 525, 580, color=C["orange"], width=3.0)
c.text(470, 620, "内皮间隙增宽", size=12.5, fill=C["orange"])
# 液体渗出
c.arrow(640, 560, 640, 700, kind="translocation", color=C["teal"], width=2.2, label="血浆渗出（水肿液）")

# 趋化因子梯度
for i in range(4):
    c.circle(690 + i * 55, 680, 9, fill="#FADCD3")
c.text(745, 726, "趋化因子梯度（IL-8 / C5a）", size=12.5, fill=C["gray"])

# 白细胞渗出三步（左下）
c.add("neutrophil", 300, 700, r=30, label=None)
c.text(300, 758, "① 边集滚动", size=13, bold=True)
c.arrow(340, 705, 420, 745, kind="activation")
c.add("neutrophil", 460, 755, r=30, label=None)
c.text(460, 813, "② 黏附", size=13, bold=True)
c.arrow(500, 760, 570, 790, kind="activation")
c.add("neutrophil", 600, 800, r=30, label=None)
c.text(600, 858, "③ 游出（穿过内皮）", size=13, bold=True)
c.arrow(640, 800, 700, 840, kind="activation")

# 组织侧：巨噬细胞与肥大细胞
c.add("macrophage", 850, 780, r=40, label="巨噬细胞")
c.add("group_box", 1000, 720, w=250, h=120, label=None, color=C["purple"], fill="#F9F7FC")
c.text(1125, 745, "肥大细胞", size=14, bold=True)
for i in range(5):
    c.circle(1060 + (i % 3) * 55, 790 + (i // 3) * 30, 8, fill=C["purple_l"], stroke=C["purple"], width=1.2)
c.arrow(1030, 780, 900, 690, kind="activation", label="释放组胺")

# 炎症介质
c.add("group_box", 150, 880, w=1100, h=0, label=None, color=C["gray"]) if False else None
c.add("legend_row", 200, 930, items=[
    (C["red"], "血管扩张充血"), (C["teal"], "通透性↑渗出"),
    (C["orange"], "内皮间隙"), (C["purple_l"], "组胺颗粒")], size=14)
c.text(200, 970, "典型表现：红、肿、热、痛、功能障碍", size=14, bold=True, anchor="start")

c.save(os.path.join(OUT, "acute_inflammation.svg"))
c.export(os.path.join(OUT, "acute_inflammation"), formats=("png",), dpi=300)
print("inflammation done")
