# -*- coding: utf-8 -*-
"""分子生物学 / 基础医学：中心法则（遗传信息流动）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 900)
c.title("中心法则：遗传信息的流动方向", size=30)

# ---- 细胞核区室（中心锚点）----
c.add("membrane_boundary", 300, 450, w=440, h=620, fill="#F4FAFE")
c.text(300, 175, "细胞核", size=16, bold=True, fill=C["blue"])

# 父代 DNA
c.add("dna_helix", 260, 300, length=200, width=44, label=None)
c.text(260, 365, "DNA（双螺旋）", size=14, bold=True)

# 复制：竖直箭头 + 子代 DNA
c.add("dna_helix", 260, 600, length=200, width=44, label=None)
c.text(260, 665, "子代 DNA", size=14, bold=True)
c.arrow(340, 390, 340, 510, kind="activation", label="复制")
c.text(445, 452, "DNA 聚合酶", size=13, fill=C["gray"], anchor="start")

# 转录
c.add("mrna", 800, 300, length=240)
c.text(800, 240, "mRNA（转录本）", size=14, bold=True)
c.arrow(430, 305, 665, 300, kind="activation", label="转录")
c.text(548, 262, "RNA 聚合酶 II", size=13, fill=C["gray"])

# 逆转录（虚线，部分病毒）
c.arrow(700, 345, 445, 545, kind="translocation", label="逆转录")

# 翻译
c.add("ribosome", 800, 345, r=15)
c.arrow(800, 390, 800, 470, kind="activation", label="翻译")
c.add("protein_blob", 800, 535, r=34, shape="circle", fill=C["orange_l"], label=None)
c.text(800, 615, "多肽链 → 功能蛋白", size=14, bold=True)

# 氨基酸序列示意
seq_colors = [C["teal"], C["purple_l"], C["yellow"], C["green_l"], C["red_l"]]
for i, col in enumerate(seq_colors):
    c.circle(645 + i * 42, 535, 15, fill=col, stroke=C["ink"], width=1.2)
c.text(729, 582, "氨基酸以肽键连接", size=12, fill=C["gray"])

# RNA 复制（RNA 病毒）
c.arrow(945, 285, 1035, 285, kind="translocation")
c.text(990, 235, "RNA 复制（RNA 病毒）", size=12, fill=C["gray"])

c.add("legend_row", 220, 800, items=[
    (C["blue"], "DNA → DNA：复制"),
    (C["teal"], "DNA → RNA：转录"),
    (C["orange"], "RNA → 蛋白：翻译"),
    (C["gray"], "虚线：仅部分病毒具有")], size=14)

c.save(os.path.join(OUT, "central_dogma.svg"))
c.export(os.path.join(OUT, "central_dogma"), formats=("png",), dpi=300)
print("central_dogma done")
