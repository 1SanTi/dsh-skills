# -*- coding: utf-8 -*-
"""病毒学 / 微生物学：有包膜病毒侵染与复制周期（六步）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("有包膜病毒侵染与复制周期", size=30)

# 宿主细胞
c.add("membrane_boundary", 720, 560, w=1080, h=760, fill="#F4FAFE")
c.text(720, 205, "宿主细胞", size=16, bold=True, fill=C["blue"])

# ① 吸附（病毒与受体结合）
c.add("virus_enveloped", 260, 300, r=40, label=None, color=C["red"])
c.add("receptor_tmembrane", 400, 215, label=None, ligand=True)
c.text(400, 160, "细胞受体", size=13, bold=True)
c.add("step_badge", 195, 300, n=1)
c.text(255, 358, "① 吸附与结合", size=14, bold=True, anchor="start")
c.arrow(305, 295, 372, 235, kind="activation")

# ② 侵入（膜融合 / 内吞）
c.add("vesicle", 520, 420, r=30, fill=C["orange_l"])
c.add("virus_enveloped", 520, 420, r=20, color=C["red"])
c.add("step_badge", 455, 420, n=2)
c.text(490, 480, "② 膜融合 / 内吞", size=14, bold=True, anchor="start")
c.arrow(320, 335, 480, 400, kind="activation")

# ③ 脱壳（释放核酸）
c.add("dna_helix", 700, 430, length=110, width=30, vertical=True)
c.add("protein_blob", 660, 520, r=18, shape="triangle", fill=C["gray_l"])
c.text(700, 555, "衣壳蛋白", size=12, fill=C["gray"])
c.add("step_badge", 620, 430, n=3)
c.text(545, 505, "③ 脱壳释放核酸", size=14, bold=True, anchor="start")
c.arrow(560, 445, 640, 440, kind="activation")

# ④ 生物合成（转录翻译 + 基因组复制）
c.add("mrna", 850, 520, length=190)
c.add("ribosome", 850, 555, r=13)
c.text(850, 470, "病毒 mRNA", size=13, bold=True)
c.add("protein_blob", 1010, 520, r=20, shape="hexagon", fill=C["purple_l"])
c.add("protein_blob", 1075, 520, r=20, shape="square", fill=C["purple_l"])
c.text(1040, 575, "病毒蛋白", size=13, bold=True)
c.add("dna_helix", 850, 330, length=130, width=34)
c.text(850, 272, "基因组复制", size=13, bold=True)
c.add("step_badge", 760, 520, n=4)
c.text(800, 620, "④ 生物合成（核酸复制 + 蛋白翻译）", size=14, bold=True, anchor="start")
c.arrow(730, 450, 800, 505, kind="activation")

# ⑤ 组装
c.add("virus_icosa", 1150, 420, r=30)
c.add("virus_enveloped", 1150, 560, r=32, color=C["red"])
c.text(1150, 620, "核衣壳 + 包膜", size=13, bold=True)
c.add("step_badge", 1085, 420, n=5)
c.text(1120, 380, "⑤ 组装", size=14, bold=True, anchor="start")
c.arrow(1100, 545, 1105, 480, kind="activation")

# ⑥ 出芽释放
c.add("membrane_patch", 1030, 870, w=280, h=30)
c.add("vesicle", 1090, 838, r=24, fill=C["red_l"])
c.add("virus_enveloped", 1090, 838, r=17, color=C["red"])
c.add("step_badge", 960, 838, n=6)
c.text(920, 845, "⑥ 出芽释放", size=14, bold=True, anchor="end")
c.arrow(1150, 640, 1105, 800, kind="activation")

# 传播提示
c.add("virus_enveloped", 1240, 300, r=24, color=C["red"])
c.arrow(1265, 340, 1330, 420, kind="translocation", label="感染新细胞")

c.add("legend_row", 200, 955, items=[
    (C["red"], "病毒颗粒"), (C["orange_l"], "胞内囊泡"),
    (C["purple_l"], "病毒蛋白"), (C["gray"], "虚线箭头 = 扩散/转移")], size=14)

c.save(os.path.join(OUT, "virus_replication_cycle.svg"))
c.export(os.path.join(OUT, "virus_replication_cycle"), formats=("png",), dpi=300)
print("virus done")
