# -*- coding: utf-8 -*-
"""内科：2 型糖尿病发病机制与靶器官损害（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("2 型糖尿病：发病机制与靶器官损害", size=30)

# 危险因素
c.add("group_box", 700, 150, w=1040, h=90, label=None, color=C["gray"], fill="#F7F7F7")
c.text(700, 152, "危险因素：遗传易感 · 肥胖 · 高脂饮食 · 缺乏运动 · 增龄", size=15, bold=True)
c.arrow(700, 200, 700, 244, kind="activation")

# 左：胰岛 β 细胞
c.add("group_box", 350, 400, w=430, h=300, label=None, color=C["blue"], fill="#F4F9FE")
c.text(350, 278, "胰岛 β 细胞功能进行性衰退", size=15, bold=True, fill=C["blue"])
c.add("membrane_boundary", 350, 430, w=330, h=200, fill="#EFF6FD")
c.text(350, 350, "胰岛", size=13, bold=True)
c.add("protein_blob", 275, 430, r=20, shape="circle", fill=C["blue_l"], label="β")
c.add("protein_blob", 425, 430, r=16, shape="circle", fill=C["green_l"], label="α")
c.add("protein_blob", 350, 495, r=16, shape="circle", fill=C["yellow_l"], label="δ")
c.text(350, 570, "β 细胞凋亡 + 胰岛素分泌不足", size=12.5, fill=C["gray"])

# 右：胰岛素抵抗
c.add("group_box", 1050, 400, w=430, h=300, label=None, color=C["orange"], fill="#FEF8F4")
c.text(1050, 278, "胰岛素抵抗（肝 / 肌 / 脂）", size=15, bold=True, fill=C["orange"])
c.add("membrane_patch", 960, 380, w=200, h=26)
c.add("receptor_tmembrane", 930, 380, label=None, ligand=False)
c.add("protein_blob", 990, 330, r=15, shape="circle", fill=C["orange_l"], label=None)
c.text(990, 330, "Ins", size=12, bold=True)
c.raw(leader_label(930, 355, 1105, 350, "胰岛素受体", size=12.5, bold=True))
c.text(1050, 420, "受体后信号转导缺陷", size=12.5, fill=C["gray"])
c.add("muscle_fiber", 1000, 480, w=170, h=34, kind="skeletal", label=None)
c.text(1050, 545, "肌肉葡萄糖摄取↓ · 肝糖输出↑", size=12.5, fill=C["gray"])

# 汇聚
c.arrow(350, 590, 560, 680, kind="activation")
c.arrow(1050, 590, 840, 680, kind="activation")
c.add("group_box", 700, 715, w=460, h=80, label=None, color=C["red"], fill="#FDF5F6")
c.text(700, 717, "慢性高血糖 → 糖毒性 / 脂毒性", size=16, bold=True, fill=C["red"])

# 并发症
c.line(210, 815, 1050, 815, color=C["gray"], width=1.4)
c.arrow(700, 758, 700, 815, kind="activation", head_size=7)
complic = [("糖尿病肾病", C["blue"]), ("糖尿病视网膜病变", C["teal"]),
           ("糖尿病神经病变", C["purple"]), ("大血管病变", C["red"])]
for i, (name, col) in enumerate(complic):
    bx = 210 + i * 280
    c.add("group_box", bx, 895, w=250, h=90, label=None, color=col, fill="#FAFAFA")
    c.text(bx, 897, name, size=14.5, bold=True)
    c.arrow(bx, 818, bx, 848, kind="activation", head_size=7)

c.add("legend_row", 220, 975, items=[(C["blue"], "胰岛因素"), (C["orange"], "胰岛素抵抗"),
                                     (C["red"], "高血糖/并发症")], size=14)

c.save(os.path.join(OUT, "t2d_mechanism.svg"))
c.export(os.path.join(OUT, "t2d_mechanism"), formats=("png",), dpi=300)
print("t2d done")
