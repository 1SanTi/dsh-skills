# -*- coding: utf-8 -*-
"""骨科：骨折愈合四期（血肿→骨痂→改建）与骨细胞（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, leader_label

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("骨折愈合过程：二期愈合（膜内 + 软骨内成骨）", size=29)

def bone_pair(x, y, s, gap):
    """两段骨干, x 为断口中心"""
    W, H = 118 * s, 78 * s
    for side in (-1, 1):
        ox = x + side * (gap / 2)
        x0 = ox - W if side < 0 else ox
        c.rect(x0, y - H / 2, W, H, fill="#F7F4EE", stroke=C["ink"], width=2.0)
        c.rect(x0 + (12 if side < 0 else 0), y - H / 2 + 18, W - 12, H - 36, fill="#F3D9C8")

# ---------- 四期 ----------
# ① 血肿
c.text(230, 250, "① 血肿炎症期", size=14.5, bold=True)
c.text(230, 276, "伤后 0~7 天", size=12, fill=C["gray"])
bone_pair(230, 360, 0.78, 60)
c.circle(248, 360, 30, fill="#C85A6A", stroke="#8a3040", width=2.0)
c.circle(238, 352, 6, fill="#E8A0A8")
c.circle(258, 368, 5, fill="#E8A0A8")
c.text(230, 445, "断端出血 · 炎细胞浸润 · 生长因子释放", size=11, fill=C["gray"])

# ② 纤维性骨痂
c.text(580, 250, "② 纤维性骨痂期", size=14.5, bold=True)
c.text(580, 276, "2~3 周", size=12, fill=C["gray"])
bone_pair(580, 360, 0.78, 90)
c.rect(560, 320, 80, 80, fill="#E8D5C0", stroke="#A8873C", width=2.0)
c.add("fibroblast", 595, 358, w=40, h=26, label=None)
c.text(580, 445, "肉芽组织 → 纤维软骨 · 成纤维细胞增殖", size=11, fill=C["gray"])

# ③ 骨性骨痂
c.text(930, 250, "③ 骨性骨痂期", size=14.5, bold=True)
c.text(930, 276, "1~3 月", size=12, fill=C["gray"])
bone_pair(930, 360, 0.78, 110)
c.circle(938, 360, 52, fill="#EFE3C8", stroke="#A8873C", width=2.4)
c.add("protein_blob", 938, 360, r=12, shape="hexagon", fill="#F7F4EE", label=None)
c.text(930, 445, "软骨内成骨 · 临时钙化 · 桥接断端", size=11, fill=C["gray"])

# ④ 改建
c.text(1265, 250, "④ 骨痂改建期", size=14.5, bold=True)
c.text(1265, 276, "数月~数年", size=12, fill=C["gray"])
c.rect(1145, 322, 240, 76, fill="#F7F4EE", stroke=C["ink"], width=2.2)
c.rect(1167, 342, 196, 36, fill="#F3D9C8")
c.circle(1200, 322, 9, fill=C["green_l"], stroke=C["green"], width=1.4)
c.raw(leader_label(1200, 310, 1230, 285, "骨单位重塑", size=11.5))
c.text(1265, 445, "Wolff 定律 · 髓腔再通 · 恢复力学强度", size=11, fill=C["gray"])

# 时间轴
c.arrow(140, 500, 1330, 500, kind="activation", width=3.0)
c.text(140, 528, "时间 →", size=13, fill=C["gray"], anchor="start")

# ---------- 骨重建细胞三联 ----------
c.add("group_box", 700, 780, w=1140, h=250, label=None, color=C["blue"], fill="#F4F9FE")
c.text(700, 690, "骨重建细胞三联（骨改建单位 BRU）", size=15, bold=True)
c.add("protein_blob", 320, 790, r=21, shape="square", fill=C["blue_l"], label=None)
c.text(320, 790, "OB", size=13, bold=True)
c.text(320, 845, "成骨细胞：分泌类骨质", size=12.3, bold=True)
c.text(320, 872, "Runx2 / ALP / 钙化", size=11, fill=C["gray"])
c.arrow(368, 790, 545, 790, kind="bidirectional", label="RANKL/OPG")
c.add("protein_blob", 590, 790, r=21, shape="circle", fill=C["teal_l"], label=None)
c.text(590, 790, "OY", size=13, bold=True)
c.text(590, 845, "骨细胞：力学感受器", size=12.3, bold=True)
c.text(590, 872, "Sost 硬化素 / Wnt 通路", size=11, fill=C["gray"])
c.arrow(638, 790, 790, 790, kind="bidirectional", label="耦联")
c.add("protein_blob", 835, 790, r=24, shape="circle", fill=C["red_l"], label=None)
c.text(835, 790, "OC", size=13, bold=True)
c.text(835, 845, "破骨细胞：吸收骨基质", size=12.3, bold=True)
c.text(835, 872, "TRAP / 组织蛋白酶K", size=11, fill=C["gray"])
c.text(1070, 730, "临床要点", size=13, bold=True)
for i, t in enumerate(["固定与血运保护", "维生素 D + 钙", "负重组建刺激", "延迟愈合→骨不连"]):
    c.text(1070, 765 + i * 32, "· " + t, size=11.5)

c.add("legend_row", 200, 950, items=[("#C85A6A", "血肿"), ("#E8D5C0", "纤维骨痂"),
                                     ("#EFE3C8", "骨性骨痂"), ("#F7F4EE", "改建皮质骨")], size=13.5)

c.save(os.path.join(OUT, "fracture_healing.svg"))
c.export(os.path.join(OUT, "fracture_healing"), formats=("png",), dpi=300)
print("fracture done")
