# -*- coding: utf-8 -*-
"""神经科学 / 蛋白组：阿尔茨海默病 Aβ 与 Tau 双机制（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1020)
c.title("阿尔茨海默病核心机制：Aβ 级联与 Tau 磷酸化", size=29)

# ---------- 左上：Aβ 级联 ----------
c.add("group_box", 300, 285, w=440, h=340, label=None, color=C["blue"], fill="#F4F9FE")
c.text(300, 152, "① 淀粉样蛋白级联（胞外）", size=14.5, bold=True)
c.rect(130, 300, 280, 20, fill="#DDE7F2", stroke=C["ink"], width=1.6)
c.rect(255, 290, 16, 40, fill=C["orange"], stroke=C["ink"], width=1.0)
c.text(245, 268, "APP", size=13, bold=True)
c.add("enzyme_lock_key", 210, 385, label=None)
c.text(210, 435, "β/γ 分泌酶异常切割", size=11.5, fill=C["gray"])
c.arrow(255, 400, 320, 400, kind="activation")
c.add("protein_blob", 350, 400, r=14, shape="circle", fill=C["gray_l"], label=None)
c.text(350, 438, "Aβ 寡聚体", size=11, bold=True)
c.arrow(372, 395, 415, 390, kind="activation")
c.circle(445, 388, 24, fill="#B8B8C8", stroke=C["gray"], width=2.2)
c.circle(433, 380, 7, fill="#8888A0")
c.circle(455, 396, 7, fill="#8888A0")
c.text(445, 438, "老年斑（Aβ 沉积）", size=11.5, bold=True)

# ---------- 左下：突触 ----------
c.add("group_box", 300, 700, w=440, h=200, label=None, color=C["orange"], fill="#FEF8F4")
c.text(300, 638, "② 突触功能障碍", size=14.5, bold=True)
c.add("neuron", 300, 720, length=240, label=None)
c.text(300, 780, "Aβ 寡聚体损伤突触 → LTP 受损 → 记忆减退", size=11.5, fill=C["gray"])

# ---------- 中：神经元胞体 ----------
c.add("group_box", 700, 270, w=280, h=300, label=None, color=C["purple"], fill="#F9F7FC")
c.text(700, 158, "神经元胞体（放大）", size=14, bold=True)
c.add("nucleus", 640, 330, r=44, label="细胞核")
c.path("M 735 240 q 18 25 0 50 q -18 25 0 50", stroke=C["red"], width=4.5)
c.path("M 758 235 q 20 28 0 56 q -20 28 0 56", stroke=C["red_l"], width=4.5)
c.text(746, 375, "NFT 缠结", size=12, bold=True, fill=C["red"])
c.add("neuron", 700, 600, length=460, label=None)
c.text(700, 680, "胆碱能神经元", size=13, bold=True)

# ---------- 右上：Tau ----------
c.add("group_box", 1090, 285, w=320, h=330, label=None, color=C["red"], fill="#FDF5F6")
c.text(1090, 158, "③ Tau 病理级联", size=14.5, bold=True)
c.add("protein_blob", 1000, 320, r=19, shape="circle", fill=C["yellow_l"], label=None)
c.text(1000, 320, "Tau", size=11.5, bold=True)
c.add("phosphate", 1042, 295, label=None)
c.add("phosphate", 1038, 345, label=None)
c.arrow(1032, 320, 1120, 320, kind="activation", label="磷酸化↑")
c.text(1090, 390, "微管解聚 → 轴转运障碍", size=11.5, fill=C["gray"])
c.arrow(1090, 412, 1090, 448, kind="activation")
c.text(1090, 478, "缠结形成 → 神经元凋亡", size=12, bold=True, fill=C["red"])

# ---------- 右下：神经炎症 ----------
c.add("group_box", 1090, 700, w=320, h=240, label=None, color=C["teal"], fill="#F3FAF9")
c.text(1090, 618, "④ 神经炎症", size=14.5, bold=True)
c.add("macrophage", 1000, 720, r=28, label=None)
c.text(1000, 772, "小胶质细胞", size=11.5, bold=True)
c.add("protein_blob", 1110, 690, r=14, shape="hexagon", fill=C["orange_l"], label=None)
c.text(1110, 690, "IL-1β", size=9.5, bold=True)
c.add("protein_blob", 1110, 740, r=14, shape="circle", fill=C["orange_l"], label=None)
c.text(1110, 740, "TNF-α", size=9.5, bold=True)
c.text(1090, 795, "慢性炎症加速神经元丢失", size=11.5, fill=C["gray"])

# ---------- 底部：转化 ----------
c.add("group_box", 700, 900, w=1240, h=110, label=None, color=C["gray"], fill="#FAFAFA")
c.text(700, 885, "生物标志物：脑脊液 Aβ42↓ / p-Tau↑ · PET（Aβ/Tau） · 血浆 p-Tau217", size=13.5, bold=True)
c.text(700, 922, "药物：胆碱酯酶抑制剂 · 美金刚 · 抗 Aβ 单抗（阿杜卡奴/仑卡奈/多纳单抗）",
       size=12.5, fill=C["gray"])

c.add("legend_row", 200, 990, items=[(C["blue_l"], "Aβ 级联"), (C["red"], "Tau 病理"),
                                     (C["purple_l"], "神经元"), (C["orange_l"], "炎症因子")], size=13.5)

c.save(os.path.join(OUT, "alzheimers_mechanism.svg"))
c.export(os.path.join(OUT, "alzheimers_mechanism"), formats=("png",), dpi=300)
print("ad done")
