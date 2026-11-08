# -*- coding: utf-8 -*-
"""头颈部肿瘤 / 肿瘤免疫治疗：PD-1/PD-L1 检查点机制（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("免疫检查点治疗：PD-1/PD-L1 抗体的作用机制", size=28)

# ============ 面板 A：治疗前 ============
c.add("group_box", 390, 490, w=560, h=640, label=None, color=C["gray"], fill="#FAFAFA")
c.text(390, 205, "A. 治疗前：肿瘤免疫逃逸", size=17, bold=True)

c.add("cancer_cell", 470, 340, r=58, label=None)
c.text(470, 428, "头颈鳞癌细胞", size=13, bold=True)
for dx, dy in [(-46, -30), (30, -44), (48, 18)]:
    c.rect(470 + dx - 7, 340 + dy - 20, 14, 34, fill=C["red_l"], stroke=C["red"], width=1.6)
c.raw(leader_label(522, 300, 600, 245, "PD-L1", size=14, bold=True))

c.add("lymphocyte", 330, 650, r=50, label=None, receptor=True)
c.text(330, 730, "T 细胞（耗竭）", size=13, bold=True, fill=C["gray"])
c.rect(330 + 40 - 6, 650 - 50, 12, 26, fill=C["purple_l"], stroke=C["purple"], width=1.6)
c.raw(leader_label(376, 612, 452, 560, "PD-1", size=14, bold=True))

c.arrow(372, 610, 445, 400, kind="inhibition", color=C["red"], width=3.0, label="抑制信号")
c.text(390, 775, "结果：T 细胞活性被抑制，肿瘤逃脱免疫监视", size=13.5, fill=C["red"])

# ============ 面板 B：治疗后 ============
c.add("group_box", 1010, 490, w=560, h=640, label=None, color=C["teal"], fill="#F6FBFA")
c.text(1010, 205, "B. 治疗后：免疫激活杀伤肿瘤", size=17, bold=True, fill=C["teal"])

c.add("cancer_cell", 1090, 340, r=58, label=None)
c.text(1090, 428, "肿瘤细胞", size=13, bold=True)
for dx, dy in [(-46, -30), (30, -44), (48, 18)]:
    c.rect(1090 + dx - 7, 340 + dy - 20, 14, 34, fill=C["red_l"], stroke=C["red"], width=1.6)
c.raw(leader_label(1142, 300, 1220, 245, "PD-L1", size=14, bold=True))

c.add("lymphocyte", 930, 650, r=50, label=None, receptor=True)
c.text(930, 730, "T 细胞（激活）", size=13, bold=True, fill=C["teal"])
c.rect(930 + 40 - 6, 650 - 50, 12, 26, fill=C["purple_l"], stroke=C["purple"], width=1.6)

# 抗体阻断 PD-1
c.add("antibody_igg", 975, 555, size=1.25, fill=C["teal_l"])
c.arrow(960, 600, 985, 420, kind="inhibition", color=C["teal"], width=3.0, label="阻断结合")
c.raw(leader_label(1000, 545, 1210, 650, "PD-1 抑制剂\n(纳武/帕博利珠单抗)", size=13, bold=True))
# 杀伤
c.arrow(950, 615, 1055, 400, kind="activation", width=2.4)
c.text(1040, 460, "穿孔素 / 颗粒酶", size=12, bold=True, anchor="start")
c.text(1010, 775, "结果：T 细胞重新激活并杀伤肿瘤细胞", size=13.5, bold=True, fill=C["teal"])

# 底部临床应用
c.add("group_box", 700, 905, w=1180, h=80, label=None, color=C["blue"], fill="#F4F9FE")
c.text(700, 893, "临床应用：复发/转移性头颈部鳞癌（SCCHN）一线免疫治疗；", size=13.5, bold=True)
c.text(700, 925, "常与化疗或 CTLA-4 抑制剂联合；PD-L1 CPS ≥ 1 人群获益更明显", size=13.5, bold=True)

c.add("legend_row", 200, 845, items=[(C["purple_l"], "PD-1"), (C["red_l"], "PD-L1"),
                                     (C["teal"], "治疗性抗体"), (C["red"], "抑制信号")], size=13.5)

c.save(os.path.join(OUT, "immune_checkpoint.svg"))
c.export(os.path.join(OUT, "immune_checkpoint"), formats=("png",), dpi=300)
print("checkpoint done")
