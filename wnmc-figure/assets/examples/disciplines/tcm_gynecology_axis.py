# -*- coding: utf-8 -*-
"""中医妇科：肾-天癸-冲任-胞宫轴与常见病机（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("中医妇科核心病机：肾-天癸-冲任-胞宫轴", size=30)

def organ(cx, cy, w, h, name, sub, color, fillc):
    c.add("group_box", cx, cy, w=w, h=h, label=None, color=color, fill=fillc)
    c.text(cx, cy - 10, name, size=18, bold=True)
    c.text(cx, cy + 24, sub, size=12.5, fill=C["gray"])

# 主轴
organ(700, 240, 260, 100, "肾", "先天之本，主生殖", C["blue"], "#F4F9FE")
c.arrow(700, 296, 700, 344, kind="activation", label="化生")
c.add("group_box", 700, 400, w=260, h=90, label=None, color=C["purple"], fill="#F9F7FC")
c.text(700, 392, "天癸", size=18, bold=True)
c.text(700, 426, "促进生殖机能成熟", size=12.5, fill=C["gray"])
c.arrow(700, 450, 700, 500, kind="activation")
c.add("group_box", 700, 555, w=260, h=90, label=None, color=C["teal"], fill="#F3FAF9")
c.text(700, 547, "冲任二脉", size=18, bold=True)
c.text(700, 581, "血海 · 阴脉之海", size=12.5, fill=C["gray"])
c.arrow(700, 606, 700, 650, kind="activation", label="下注")

# 胞宫
c.add("group_box", 700, 725, w=260, h=130, label=None, color=C["red"], fill="#FDF5F6")
c.text(700, 715, "胞宫（子宫）", size=17, bold=True)
c.circle(630, 765, 17, fill=C["orange_l"], stroke=C["orange"], width=1.6)
c.circle(770, 765, 17, fill=C["orange_l"], stroke=C["orange"], width=1.6)
c.text(630, 800, "卵巢", size=11.5)
c.text(770, 800, "卵巢", size=11.5)
c.text(700, 745, "藏泻有时", size=12, fill=C["gray"])

# 旁路脏腑
organ(240, 470, 220, 100, "肝", "疏泄，调畅气血", C["green"], "#F7FBF5")
c.arrow(360, 500, 560, 545, kind="activation", label="疏泄于冲任")
organ(240, 630, 220, 100, "脾", "统血，生化之源", C["yellow"], "#FDFAF2")
c.arrow(355, 625, 565, 580, kind="activation", label="充养血海")

# 心
organ(1160, 470, 220, 100, "心", "心神下通胞宫", C["purple"], "#F9F7FC")
c.arrow(1040, 500, 840, 545, kind="activation", label="心肾相交")

# 病机
x0, y0 = 0, 0
c.add("group_box", 1160, 760, w=290, h=240, label=None, color=C["red"], fill="#FDF5F6")
c.text(1160, 662, "常见病机", size=14, bold=True)
for i, t in enumerate(["肾虚 → 月经后期、闭经", "肝郁 → 痛经、经前诸证",
                       "痰湿 → 多囊、闭经", "血瘀 → 子宫内膜异位"]):
    c.text(1040, 700 + i * 40, t, size=12.3, anchor="start")

# 治则
c.add("group_box", 240, 860, w=310, h=150, label=None, color=C["teal"], fill="#F3FAF9")
c.text(240, 808, "治疗大法", size=14, bold=True)
for i, t in enumerate(["补肾填精为根本", "疏肝健脾以助源", "调理冲任以治标"]):
    c.text(115, 868 + i * 28, "· " + t, size=12.5, anchor="start")

c.add("legend_row", 540, 975, items=[(C["blue"], "主轴"), (C["green"], "旁路脏腑"),
                                     (C["red"], "病机/胞宫")], size=13)

c.save(os.path.join(OUT, "tcm_gynecology_axis.svg"))
c.export(os.path.join(OUT, "tcm_gynecology_axis"), formats=("png",), dpi=300)
print("tcm done")
