# -*- coding: utf-8 -*-
"""药物制剂：脂质体纳米给药系统与 EPR 效应（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("脂质体纳米制剂：结构、递送与 EPR 效应", size=29)

# ---------- 左：脂质体结构 ----------
c.add("group_box", 330, 330, w=440, h=420, label=None, color=C["blue"], fill="#F4F9FE")
c.text(330, 158, "脂质体结构（放大）", size=15.5, bold=True)
LX, LY = 340, 400
c.circle(LX, LY, 105, fill="#F4FAFE", stroke=C["blue"], width=3.0)
c.circle(LX, LY, 80, fill="#FFFFFF", stroke=C["blue"], width=2.4)
c.circle(LX, LY, 36, fill=C["purple_l"], stroke=C["purple"], width=2.0)
c.text(LX, LY, "水相药", size=12, bold=True)
for i in range(5):
    x = LX - 88 + i * 26
    c.path(f"M {x} {LY-103} q 5 -10 10 0 q 5 10 10 0", stroke=C["teal"], width=2.2)
c.raw(leader_label(LX - 40, LY - 108, 170, 230, "PEG 修饰（长循环）", size=13, bold=True, color=C["teal"]))
c.circle(LX - 140, LY + 95, 42, fill="#F4FAFE", stroke=C["blue"], width=2.0)
for i in range(4):
    c.line(LX - 164 + i * 12, LY + 68, LX - 164 + i * 12, LY + 82, color=C["orange"], width=2.4)
    c.line(LX - 158 + i * 12, LY + 110, LX - 158 + i * 12, LY + 124, color=C["orange"], width=2.4)
c.raw(leader_label(LX - 140, LY + 50, 165, 320, "磷脂双分子层\n(卵磷脂+胆固醇)", size=13, bold=True))
c.add("protein_blob", LX + 82, LY - 55, r=10, shape="circle", fill=C["orange_l"], label=None)
c.raw(leader_label(LX + 82, LY - 68, 520, 260, "膜载疏水药", size=12.5, bold=True))

# ---------- 中：体内命运 ----------
c.add("group_box", 810, 330, w=380, h=420, label=None, color=C["teal"], fill="#F3FAF9")
c.text(810, 158, "体内命运", size=15.5, bold=True)
journey = [("静脉注射", "避免聚集，粒径 80~150 nm"),
           ("PEG 长循环", "逃避 RES / 单核吞噬系统"),
           ("EPR 富集", "肿瘤血管间隙渗出"),
           ("细胞摄取", "内吞 → 溶酶体释放药")]
for i, (t, s) in enumerate(journey):
    c.add("step_badge", 665, 235 + i * 88, n=i + 1, r=13)
    c.text(700, 231 + i * 88, "①②③④"[i] + " " + t, size=13.5, bold=True, anchor="start")
    c.text(700, 259 + i * 88, s, size=11.3, fill=C["gray"], anchor="start")
    if i < 3:
        c.arrow(665, 252 + i * 88, 665, 285 + i * 88, kind="activation")

# ---------- 右：EPR 与粒径窗口 ----------
c.add("group_box", 1200, 330, w=340, h=420, label=None, color=C["red"], fill="#FDF5F6")
c.text(1200, 158, "EPR 效应", size=15.5, bold=True)
c.path("M 1080 260 Q 1200 225 1320 260", stroke=C["red"], width=3.0)
c.path("M 1080 330 Q 1200 365 1320 330", stroke=C["red"], width=3.0)
c.text(1200, 240, "肿瘤血管内皮间隙 100~600 nm", size=11, fill=C["gray"])
for gx in (1150, 1250):
    c.add("vesicle", gx, 295, r=12, fill=C["blue_l"])
    c.arrow(gx, 280, gx, 312, kind="translocation")
c.text(1200, 385, "纳米粒外渗 → 选择性蓄积", size=12, bold=True)
c.text(1070, 425, "粒径窗口", size=12.5, bold=True, anchor="start")
for i, (rng, lab, hot) in enumerate([("<10 nm", "肾清除", False),
                                      ("10~80 nm", "入瘤但易清除", False),
                                      ("80~150 nm", "最佳治疗窗口", True),
                                      (">200 nm", "肝脾 RES 摄取", False)]):
    yy = 455 + i * 26
    c.rect(1085, yy - 10, 22, 14, fill=C["red"] if hot else C["gray_l"])
    c.text(1115, yy, f"{rng}  {lab}", size=11.3, anchor="start",
           fill=C["red"] if hot else C["gray"])

# ---------- 底：处方与质控 ----------
c.add("group_box", 700, 780, w=1240, h=220, label=None, color=C["orange"], fill="#FEF8F4")
c.text(700, 705, "处方工艺与质量控制", size=15.5, bold=True)
c.text(120, 745, "关键质量属性 (CQA)", size=13, bold=True, anchor="start")
for i, t in enumerate(["粒径 / PDI（DLS）", "Zeta 电位", "包封率 EE% / 载药量 DL%", "体外释放（透析法）"]):
    c.text(140, 775 + i * 28, "· " + t, size=12, anchor="start")
c.text(520, 745, "制备工艺", size=13, bold=True, anchor="start")
for i, t in enumerate(["薄膜水化法", "乙醇注入法", "pH 梯度主动载药（阿霉素）", "冻干保护（海藻糖）"]):
    c.text(540, 775 + i * 28, "· " + t, size=12, anchor="start")
c.text(920, 745, "代表上市品种", size=13, bold=True, anchor="start")
for i, t in enumerate(["多柔比星脂质体（Doxil）", "紫杉醇白蛋白纳米粒", "mRNA-LNP（脂质纳米粒）", "两性霉素B脂质体"]):
    c.text(940, 775 + i * 28, "· " + t, size=12, anchor="start")

c.add("legend_row", 200, 940, items=[(C["blue_l"], "脂质体"), (C["purple_l"], "水相药物"),
                                     (C["teal"], "PEG 链"), (C["red"], "肿瘤血管")], size=14)

c.save(os.path.join(OUT, "liposome_nanomedicine.svg"))
c.export(os.path.join(OUT, "liposome_nanomedicine"), formats=("png",), dpi=300)
print("liposome done")
