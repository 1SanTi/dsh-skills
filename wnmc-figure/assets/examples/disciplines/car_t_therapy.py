# -*- coding: utf-8 -*-
"""血液肿瘤：CAR-T 细胞治疗 B 细胞白血病/淋巴瘤（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1050)
c.title("CAR-T 细胞免疫治疗：从采集到杀伤", size=30)

# ---------- 左上：CAR 结构 ----------
c.add("group_box", 340, 330, w=480, h=440, label=None, color=C["purple"], fill="#F9F7FC")
c.text(340, 150, "嵌合抗原受体（CAR）结构", size=15, bold=True)
c.rect(150, 360, 380, 24, fill="#DDE7F2", stroke=C["ink"], width=1.8)
c.text(160, 410, "T 细胞膜", size=12, anchor="start", fill=C["gray"])
c.path("M 230 360 L 230 300 L 270 250 L 310 300 L 310 360", stroke=C["teal"], width=5)
c.text(270, 228, "scFv 抗原结合域", size=13, bold=True, fill=C["teal"])
c.text(270, 252, "识别 CD19", size=11.5, fill=C["gray"])
c.line(310, 300, 370, 300, color=C["gray"], width=3.2)
c.text(390, 300, "铰链区", size=11.5, anchor="start", fill=C["gray"])
c.rect(370, 346, 24, 30, fill=C["orange"], stroke=C["ink"], width=1.2)
c.text(402, 368, "跨膜域", size=11.5, anchor="start")
c.rect(360, 398, 105, 28, fill=C["purple_l"], stroke=C["purple"], width=1.4, rx=6)
c.text(412, 416, "CD28 共刺激", size=11.5, bold=True)
c.rect(360, 434, 105, 28, fill=C["red_l"], stroke=C["red"], width=1.4, rx=6)
c.text(412, 452, "CD3ζ 信号", size=11.5, bold=True)
c.text(340, 505, "第二代 CAR（含共刺激域）", size=12, fill=C["gray"])

# ---------- 左下：制备流程 ----------
c.add("group_box", 340, 800, w=480, h=330, label=None, color=C["blue"], fill="#F4F9FE")
c.text(340, 665, "制备流程（约 2~4 周）", size=15, bold=True)
prep = ["白细胞单采（含 T 细胞）", "病毒载体转入 CAR 基因",
        "体外扩增（IL-2 培养）", "质检 → 冰冻回输患者",
        "清淋化疗（FC 方案）后输注"]
for i, t in enumerate(prep):
    c.add("step_badge", 195, 720 + i * 46, n=i + 1, r=13)
    c.text(228, 727 + i * 46, t, size=13.5, anchor="start")

c.arrow(590, 800, 680, 800, kind="activation", width=3.0, label="回输")

# ---------- 右上：杀伤 ----------
c.add("group_box", 1030, 400, w=640, h=560, label=None, color=C["red"], fill="#FDF5F6")
c.text(1030, 160, "体内杀伤 CD19+ 肿瘤细胞", size=15, bold=True)
c.add("cancer_cell", 900, 320, r=46, label=None)
c.text(900, 398, "CD19+ 白血病细胞", size=13, bold=True)
c.add("lymphocyte", 1180, 500, r=46, label=None, receptor=True)
c.text(1180, 580, "CAR-T 细胞", size=13, bold=True, fill=C["purple"])
c.path("M 1212 462 L 1212 438 L 1230 420 L 1248 438 L 1248 462", stroke=C["teal"], width=4)
c.arrow(1145, 465, 950, 355, kind="inhibition", color=C["red"], width=3.0, label="颗粒酶/穿孔素")
c.add("protein_blob", 800, 470, r=15, shape="hexagon", fill=C["yellow_l"], label=None)
c.text(800, 470, "IL-2", size=10.5, bold=True)
c.add("protein_blob", 830, 540, r=15, shape="circle", fill=C["orange_l"], label=None)
c.text(830, 540, "IFN-γ", size=10, bold=True)
c.text(770, 590, "细胞因子释放", size=12, fill=C["gray"], anchor="start")

# ---------- 右下：疗效监测 ----------
c.add("group_box", 1030, 860, w=640, h=290, label=None, color=C["teal"], fill="#F3FAF9")
c.text(1030, 745, "疗效与安全性监测", size=15, bold=True)
for i, t in enumerate([
        "缓解率高：r/r B-ALL 完全缓解约 80~90%",
        "不良反应：CRS（细胞因子释放综合征）",
        "　→ 分级处理：托珠单抗 / 糖皮质激素",
        "神经毒性 ICANS：严密神经评估",
        "远期：B 细胞发育不全 → IVIG 替代"]):
    c.text(770, 790 + i * 42, "· " + t, size=13, anchor="start")

c.add("legend_row", 150, 1015, items=[(C["teal"], "scFv"), (C["purple_l"], "共刺激域"),
                                      (C["red_l"], "肿瘤细胞"), (C["yellow_l"], "细胞因子")], size=13.5)

c.save(os.path.join(OUT, "car_t_therapy.svg"))
c.export(os.path.join(OUT, "car_t_therapy"), formats=("png",), dpi=300)
print("cart done")
