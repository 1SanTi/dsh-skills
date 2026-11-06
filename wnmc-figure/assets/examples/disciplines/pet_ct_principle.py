# -*- coding: utf-8 -*-
"""核医学：PET/CT 显像原理（18F-FDG）——中心锚点版"""
import os, sys, math
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("PET/CT 显像原理（以 18F-FDG 为例）", size=30)

# ① 注射
c.add("syringe", 170, 215, length=130, angle=-20, label=None)
c.text(170, 120, "① 静脉注射显像剂", size=14, bold=True)
c.text(170, 295, "18F-FDG（葡萄糖类似物）", size=12.5, fill=C["gray"])
c.add("human_silhouette", 170, 430, h=150, label=None)
c.text(170, 530, "肿瘤 / 脑 / 心 高摄取", size=12, fill=C["gray"])
c.arrow(280, 250, 380, 300, kind="activation")

# ② 湮没
c.add("group_box", 560, 300, w=340, h=280, label=None, color=C["purple"], fill="#F9F7FC")
c.text(560, 185, "② 正电子湮没", size=14, bold=True)
c.add("protein_blob", 480, 360, r=16, shape="circle", fill=C["orange_l"], label=None)
c.text(480, 360, "β+", size=12, bold=True)
c.add("protein_blob", 640, 360, r=13, shape="circle", fill=C["gray_l"], label=None)
c.text(640, 360, "e-", size=12, bold=True)
c.arrow(505, 360, 615, 360, kind="activation")
c.arrow(560, 338, 560, 250, kind="activation", color=C["red"], width=2.4)
c.arrow(560, 382, 560, 462, kind="activation", color=C["red"], width=2.4)
c.text(590, 268, "γ 511 keV", size=12.5, fill=C["red"], anchor="start")
c.text(590, 430, "γ 511 keV（180°）", size=12.5, fill=C["red"], anchor="start")
c.arrow(740, 360, 830, 360, kind="activation")

# ③ 符合探测
c.add("group_box", 1060, 300, w=390, h=280, label=None, color=C["blue"], fill="#F4F9FE")
c.text(1060, 185, "③ 符合探测", size=14, bold=True)
for i in range(14):
    ang = i / 14 * 6.283
    c.rect(1060 + 120 * math.cos(ang) - 8, 340 + 95 * math.sin(ang) - 8,
           16, 16, fill=C["blue_l"], stroke=C["blue"], width=1.4)
c.circle(1060, 340, 42, fill="#FBEFEA", stroke=C["gray"], width=2.0)
c.circle(1050, 330, 13, fill=C["red_l"], stroke=C["red"], width=2.0)
c.text(1060, 462, "探测器环：符合线（LOR）", size=12)

# ④ 重建
c.add("group_box", 250, 700, w=380, h=280, label=None, color=C["teal"], fill="#F3FAF9")
c.text(250, 585, "④ 重建与融合", size=14, bold=True)
c.circle(250, 715, 80, fill="#2A1E3F")
c.circle(250, 715, 56, fill="#3A2A55")
for (dx, dy, r, col) in [(-38, -18, 15, "#5A3A6E"), (42, 10, 12, "#5A3A6E"),
                          (5, 42, 17, "#5A3A6E"), (24, -33, 11, "#C4453C")]:
    c.circle(250 + dx, 715 + dy, r, fill=col)
c.text(250, 820, "PET 代谢信息", size=12.5, bold=True)
c.arrow(450, 715, 520, 715, kind="activation")

# ⑤ 融合
c.add("group_box", 730, 700, w=380, h=280, label=None, color=C["orange"], fill="#FEF8F4")
c.text(730, 585, "⑤ PET/CT 融合图像", size=14, bold=True)
c.circle(730, 715, 80, fill="#F3E4D2", stroke=C["gray"], width=2.0)
c.circle(730, 715, 56, fill="#EAD5BC")
c.circle(752, 685, 12, fill="#C4453C", stroke="#7a1f1f", width=1.6)
c.raw(leader_label(752, 672, 850, 630, "高代谢灶", size=12.5, bold=True, color=C["red"]))
c.text(730, 820, "解剖定位 + 代谢功能", size=12.5, bold=True)
c.arrow(930, 715, 990, 715, kind="activation")

# ⑥ SUV
c.add("group_box", 1180, 700, w=340, h=280, label=None, color=C["red"], fill="#FDF5F6")
c.text(1180, 585, "⑥ 半定量：SUV", size=14, bold=True)
c.add("group_box", 1180, 660, w=260, h=70, label=None, color=C["gray"], fill="#FFFFFF")
c.text(1180, 655, "SUV = 组织活度", size=13.5, bold=True)
c.text(1180, 685, "（注射活度 / 体重）", size=12, fill=C["gray"])
for i, t in enumerate(["SUVmax > 2.5 提示恶性可能", "用于诊断、分期、疗效评估",
                       "SUV 下降 = 治疗有效"]):
    c.text(1040, 740 + i * 36, "· " + t, size=12.3, anchor="start")

c.add("legend_row", 200, 940, items=[(C["red"], "γ 光子"), (C["orange_l"], "正电子"),
                                     ("#C4453C", "高代谢病灶")], size=14)

c.save(os.path.join(OUT, "pet_ct_principle.svg"))
c.export(os.path.join(OUT, "pet_ct_principle"), formats=("png",), dpi=300)
print("pet done")
