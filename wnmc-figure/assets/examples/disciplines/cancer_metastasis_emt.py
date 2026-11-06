# -*- coding: utf-8 -*-
"""肿瘤学：上皮-间质转化（EMT）与血行转移（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1500, 1000)
c.title("肿瘤转移：EMT — 内渗 — 循环 — 外渗 — 定植", size=29)

# ---------- 原发灶 ----------
c.add("group_box", 280, 300, w=380, h=400, label=None, color=C["gray"], fill="#FAFAFA")
c.text(280, 135, "原发肿瘤灶", size=15, bold=True)
for dx, dy, r in [(-60, -20, 28), (0, -45, 24), (55, -10, 26), (-10, 30, 30), (50, 55, 22), (-60, 50, 20)]:
    c.add("cancer_cell", 280 + dx, 320 + dy, r=r, label=None)
c.text(280, 465, "E-cadherin +（上皮标志）", size=12, fill=C["blue"])

# EMT
c.arrow(478, 300, 552, 300, kind="activation", width=3.0, label="EMT")
c.text(515, 258, "TGF-β / Snail / ZEB", size=11.5, fill=C["gray"])

# 间质表型
c.add("group_box", 700, 300, w=260, h=400, label=None, color=C["orange"], fill="#FEF8F4")
c.text(700, 135, "间质表型", size=15, bold=True)
c.add("fibroblast", 700, 320, w=130, h=70, label=None)
c.text(700, 440, "N-cadherin + / Vimentin +", size=11.5, fill=C["orange"])
c.text(700, 470, "运动性 ↑ 侵袭性 ↑", size=12.5, bold=True, fill=C["orange"])

# 内渗
c.arrow(838, 300, 912, 300, kind="activation", width=3.0, label="内渗")

# 血管
c.path("M 950 180 Q 1200 140 1440 180 L 1440 460 Q 1200 500 950 460 Z",
       fill="#FBEFEA", stroke=C["red"], width=2.6)
c.text(1200, 172, "循环肿瘤细胞（CTC）", size=14, bold=True, fill=C["red"])
c.add("cancer_cell", 1090, 300, r=25, label=None)
c.add("cancer_cell", 1210, 380, r=23, label=None)
c.add("cancer_cell", 1330, 300, r=25, label=None)
c.add("rbc", 1150, 250, r=17)
c.add("rbc", 1290, 430, r=17)
c.add("platelet", 1250, 240, r=10)
c.text(1030, 440, "血流剪切 + 免疫攻击", size=12, fill=C["gray"], anchor="start")

# 外渗
c.arrow(1400, 505, 1400, 590, kind="activation", width=3.0, label="外渗")
c.text(1408, 560, "穿过内皮", size=11.5, fill=C["gray"], anchor="start")

# 转移灶
c.add("group_box", 1300, 760, w=280, h=290, label=None, color=C["red"], fill="#FDF5F6")
c.text(1300, 640, "远处转移灶", size=15, bold=True, fill=C["red"])
c.circle(1260, 740, 38, fill="#E8A0A8", stroke=C["red"], width=2.0)
c.add("cancer_cell", 1260, 740, r=20, label=None)
c.add("cancer_cell", 1330, 810, r=15, label=None)
c.text(1300, 862, "肺 / 肝 / 骨 / 脑", size=12.5, bold=True)
c.text(1300, 890, "血管生成 · 克隆扩增", size=11.5, fill=C["gray"])

# 机制步骤
c.add("group_box", 490, 760, w=830, h=290, label=None, color=C["purple"], fill="#F9F7FC")
c.text(490, 640, "转移关键步骤与干预靶点", size=15, bold=True)
for i, t in enumerate([
        "① 细胞连接破坏：E-cadherin 下调",
        "② 基质降解：MMP-2/9 分泌",
        "③ 侵袭运动：Rho GTPase 重排细胞骨架",
        "④ 内渗 / 外渗：内皮黏附（ICAM/VCAM）",
        "⑤ 预转移 niche：外泌体营造土壤（seed & soil）"]):
    c.text(120, 700 + i * 46, t, size=13.5, anchor="start")

c.add("legend_row", 120, 950, items=[(C["blue_l"], "上皮表型"), (C["orange_l"], "间质表型"),
                                     (C["red"], "血管/转移")], size=14)

c.save(os.path.join(OUT, "cancer_metastasis_emt.svg"))
c.export(os.path.join(OUT, "cancer_metastasis_emt"), formats=("png",), dpi=300)
print("metastasis done")
