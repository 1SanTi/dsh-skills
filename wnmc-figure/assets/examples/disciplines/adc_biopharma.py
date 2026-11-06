# -*- coding: utf-8 -*-
"""生物医药：抗体偶联药物（ADC）结构与作用机制（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("抗体偶联药物（ADC）：结构设计与 bystander 效应", size=29)

# ---------- 左：ADC 三要素 ----------
c.add("group_box", 330, 330, w=480, h=420, label=None, color=C["blue"], fill="#F4F9FE")
c.text(330, 158, "ADC 三要素", size=15.5, bold=True)
AX, AY = 330, 390
c.path(f"M {AX-65} {AY+55} L {AX-18} {AY-38} L {AX} {AY-20} L {AX+18} {AY-38} L {AX+65} {AY+55}",
       stroke=C["blue"], width=7)
c.line(AX, AY - 20, AX, AY + 68, color=C["blue"], width=7)
for dx, dy in [(-18, -38), (18, -38)]:
    c.circle(AX + dx - 28, AY + dy - 28, 8, fill=C["yellow"], stroke=C["orange"], width=1.6)
    c.circle(AX + dx - 54, AY + dy - 45, 12, fill=C["red_l"], stroke=C["red"], width=2.0)
c.raw(leader_label(AX - 82, AY - 83, 175, 235, "细胞毒弹头\n(MMAE/DM1)", size=13, bold=True, color=C["red"]))
c.raw(leader_label(AX - 46, AY - 66, 475, 265, "可裂解连接子\n(mc-VC-PAB)", size=13, bold=True, color=C["orange"]))
c.text(AX + 85, AY + 38, "IgG 抗体", size=13.5, bold=True, fill=C["blue"], anchor="start")
c.text(AX + 85, AY + 64, "(HER2/TROP2/CD30…)", size=11, fill=C["gray"], anchor="start")
c.text(330, 515, "关键参数：DAR（药物抗体比）2~4 最佳", size=12.5, fill=C["gray"])

# ---------- 中：内吞机制 ----------
c.add("group_box", 810, 330, w=380, h=420, label=None, color=C["teal"], fill="#F3FAF9")
c.text(810, 158, "作用机制", size=15.5, bold=True)
c.add("group_box", 810, 340, w=300, h=300, label=None, color=C["gray"], fill="#FAFAFA")
c.add("receptor_tmembrane", 745, 320, label="HER2", ligand=False)
c.add("receptor_tmembrane", 875, 320, label=None, ligand=False)
c.add("antibody_igg", 745, 258, size=0.65, fill=C["blue_l"])
c.add("antibody_igg", 875, 258, size=0.65, fill=C["blue_l"])
c.text(810, 448, "① 抗体结合靶抗原", size=12.3, anchor="start")
c.arrow(810, 465, 810, 500, kind="translocation", label="② 内吞")
c.add("lysosome", 810, 535, r=26, label="溶酶体")
c.text(770, 600, "③ 连接子裂解释放弹头", size=12.3, anchor="start")
c.add("protein_blob", 940, 520, r=13, shape="circle", fill=C["red_l"], label=None)
c.text(940, 520, "药", size=10.5, bold=True)
c.raw(leader_label(940, 505, 1010, 565, "微管破坏 → 凋亡", size=12, bold=True))

# ---------- 右：旁观者效应 ----------
c.add("group_box", 1200, 330, w=280, h=420, label=None, color=C["red"], fill="#FDF5F6")
c.text(1200, 158, "旁观者效应", size=15.5, bold=True)
c.add("cancer_cell", 1150, 300, r=34, label=None)
c.add("cancer_cell", 1260, 390, r=28, label=None)
c.add("protein_blob", 1205, 345, r=9, shape="circle", fill=C["red_l"], label=None)
c.arrow(1190, 355, 1245, 378, kind="translocation", color=C["red"], width=2.0)
c.text(1200, 460, "膜通透性弹头扩散至", size=12, anchor="start")
c.text(1200, 488, "邻近抗原低表达肿瘤", size=12, anchor="start")
c.text(1200, 530, "→ 克服抗原异质性", size=12.5, bold=True, anchor="start", fill=C["red"])

# ---------- 底：代表药物 ----------
c.add("group_box", 700, 780, w=1240, h=210, label=None, color=C["purple"], fill="#F9F7FC")
c.text(700, 705, "代表性药物与靶点", size=15.5, bold=True)
drugs = [("T-DM1 / T-DXd", "HER2", "乳腺癌 / 胃癌"),
         ("SG (Trodelvy)", "TROP-2", "三阴乳腺癌 / 尿路上皮癌"),
         ("EV (Padcev)", "Nectin-4", "尿路上皮癌"),
         ("维布妥昔单抗", "CD30", "霍奇金淋巴瘤")]
for i, (n, t, ind) in enumerate(drugs):
    bx = 130 + i * 305
    c.text(bx, 755, n, size=13.5, bold=True, anchor="start")
    c.rect(bx, 772, 90, 24, fill=C["purple_l"], stroke=C["purple"], width=1.2, rx=12)
    c.text(bx + 45, 789, t, size=12, bold=True)
    c.text(bx, 825, ind, size=12, fill=C["gray"], anchor="start")
c.text(700, 860, "研发要点：弹头效力 · 连接子血浆稳定性 · 脱靶毒性（肺/眼/血液）· 生物分析（LC-MS/MS）",
       size=12.5, fill=C["gray"])

c.add("legend_row", 200, 935, items=[(C["blue_l"], "抗体"), (C["yellow"], "连接子"),
                                     (C["red_l"], "细胞毒弹头")], size=14)

c.save(os.path.join(OUT, "adc_biopharma.svg"))
c.export(os.path.join(OUT, "adc_biopharma"), formats=("png",), dpi=300)
print("adc done")
