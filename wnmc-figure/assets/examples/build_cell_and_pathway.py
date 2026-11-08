# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.expanduser("~/.workbuddy/skills/medical-illustration/scripts"))
from bio_graphics import Canvas, C, leader_label

OUT = r"C:\Users\Administrator\WorkBuddy\2026-09-11-14-26-41\_mi_test"
os.makedirs(OUT, exist_ok=True)

# ---------- 图1: 动物细胞超微结构 ----------
c = Canvas(1400, 1000)
c.title("动物细胞超微结构示意图", size=32)
c.add("membrane_boundary", 700, 540, w=1100, h=800, label=None, fill="#F4FAFE")
c.add("nucleus", 430, 470, r=125, label="细胞核")
c.raw(leader_label(430+60, 470-80, 640, 250, "核仁", bold=True))
c.add("nucleolus", 400, 430, r=38)
c.add("mitochondrion", 800, 340, w=170, h=95, label="线粒体", angle=-12)
c.add("golgi", 1010, 480, w=170, h=110, label="高尔基体")
c.add("rough_er", 350, 760, w=200, h=110, label="粗面内质网")
c.add("smooth_er", 640, 800, w=170, h=80, label="滑面内质网")
c.add("lysosome", 900, 720, r=40, label="溶酶体")
c.add("peroxisome", 1020, 700, r=28, label="过氧化物酶体")
c.add("centriole", 1130, 380, label="中心体")
c.add("vesicle", 720, 600, r=22)
c.add("cytoskeleton", 520, 620, length=180, kind="microtubule", angle=25, label="微管")
c.add("cytoskeleton", 950, 860, length=180, kind="actin", angle=-15, label="微丝")
c.add("membrane_patch", 700, 928, w=520, h=34)
c.text(700, 975, "磷脂双分子层(细胞膜)", size=15)
c.save(OUT + "/cell_anatomy.svg")
f1 = c.export(OUT + "/cell_anatomy", formats=("png", "pdf"), dpi=300)

# ---------- 图2: 细胞凋亡信号通路 ----------
p = Canvas(1400, 900)
p.title("细胞凋亡的内源与外源信号通路", size=30)
# 外源通路
p.add("receptor_tmembrane", 260, 200, label="Fas 受体", ligand=True)
p.add("protein_blob", 260, 360, r=26, label="FADD", shape="circle")
p.add("protein_blob", 260, 470, r=30, label="Caspase-8", shape="square", fill=C["orange_l"])
p.arrow(260, 232, 260, 330, kind="activation")
p.arrow(260, 392, 260, 438, kind="activation")
# 内源通路
p.add("mitochondrion", 780, 260, w=190, h=105, label=None)
p.text(780, 190, "线粒体", size=15, bold=True)
p.add("protein_blob", 780, 260, r=20, label=None, fill=C["purple_l"])
p.text(780, 266, "Cyt c", size=13, bold=True, fill="#FFFFFF")
p.add("protein_blob", 780, 470, r=30, label="Apaf-1", shape="hexagon")
p.arrow(780, 318, 780, 438, kind="translocation", label="细胞色素c 释放")
# 汇合 -> 执行
p.add("protein_blob", 520, 620, r=34, label="Caspase-9", shape="square")
p.arrow(292, 495, 480, 595, kind="activation")
p.arrow(748, 495, 560, 595, kind="activation")
p.add("protein_blob", 900, 620, r=36, label="Caspase-3/7", shape="square", fill=C["red_l"])
p.arrow(558, 620, 858, 620, kind="activation", label="级联激活")
# 效应
p.add("group_box", 1130, 620, w=320, h=230, label="凋亡效应", color=C["red"])
p.add("dna_helix", 1050, 570, length=70, width=30, label=None)
p.text(1050, 620, "DNA 断裂", size=13)
p.add("proteasome", 1200, 570)
p.text(1200, 645, "蛋白降解", size=13)
p.add("autophagosome", 1120, 720, r=28)
p.text(1120, 775, "膜起泡", size=13)
p.arrow(940, 620, 966, 620, kind="activation")
# 调控
p.add("protein_blob", 1060, 260, r=26, label="Bcl-2", shape="circle", fill=C["green_l"])
p.arrow(1030, 280, 880, 300, kind="inhibition", label="抑制")
p.add("protein_blob", 560, 260, r=26, label="Bax", shape="circle", fill=C["red_l"])
p.arrow(592, 280, 680, 290, kind="activation", label="促释放")
p.add("legend_row", 160, 850, items=[(C["red_l"], "促凋亡"), (C["green_l"], "抗凋亡"),
                                     (C["orange_l"], "起始 Caspase"), (C["red"], "执行 Caspase")], size=15)
f2 = p.export(OUT + "/apoptosis_pathway", formats=("png", "pdf"), dpi=300)

print("\n".join(f1 + f2))
