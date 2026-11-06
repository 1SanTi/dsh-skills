# -*- coding: utf-8 -*-
"""呼吸 / 胸部肿瘤：气道上皮癌变四阶段（吸烟等危险因素）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 1000)
c.title("肺癌发生：气道上皮从正常到癌的演变", size=29)

# 危险因素（顶部）
c.add("group_box", 700, 130, w=1040, h=80, label=None, color=C["gray"], fill="#F7F7F7")
c.text(700, 152, "危险因素：吸烟（含焦油/苯并芘） · PM2.5 · 职业粉尘（石棉/氡） · 遗传易感", size=15, bold=True)
c.arrow(700, 214, 700, 262, kind="activation")

# 四阶段气道路
BASE = 430   # 基底膜 y
def epithelium(x0, stages_kw):
    """画一段气道壁: 基底膜 + 上皮细胞"""
    W = 260
    c.rect(x0, BASE, W, 14, fill="#C8A088", stroke=C["ink"], width=1.4)  # 基底膜
    c.rect(x0, BASE + 14, W, 60, fill="#F3E4D2")                          # 固有层
    return W

stages = [
    ("① 正常假复层纤毛柱状上皮", "cilia"),
    ("② 鳞状化生", "meta"),
    ("③ 异型增生（原位癌）", "dys"),
    ("④ 浸润性癌", "inv"),
]
X = 110
for i, (name, kind) in enumerate(stages):
    x0 = X + i * 310
    W = epithelium(x0, kind)
    cx = x0 + W / 2
    if kind == "cilia":
        for j in range(5):
            c.add("cell_epithelial", x0 + 30 + j * 50, BASE - 42, w=40, h=68, cilia=True, label=None)
        c.text(cx, 300, "纤毛完整 · 排痰功能正常", size=12, fill=C["teal"])
    elif kind == "meta":
        for j in range(5):
            c.add("cell_epithelial", x0 + 30 + j * 50, BASE - 40, w=42, h=64, kind="squamous", label=None)
        c.text(cx, 300, "鳞状上皮替代 · 纤毛消失", size=12, fill=C["yellow"] if False else "#B98A2F")
    elif kind == "dys":
        for j in range(5):
            # 异型：核大深染、极性紊乱
            c.rect(x0 + 16 + j * 50, BASE - 62, 34, 58, fill="#F9DCDE", stroke=C["red"], width=1.4, rx=8)
            c.circle(x0 + 33 + j * 50, BASE - 38, 11, fill=C["purple"], stroke=C["ink"], width=1.0)
        c.text(cx, 300, "细胞异型 · 核分裂↑ · 未突破基底膜", size=11.5, fill=C["purple"])
    else:
        for j in range(5):
            c.add("cancer_cell", x0 + 40 + j * 46, BASE - 46, r=24, label=None)
        # 突破基底膜
        c.add("cancer_cell", x0 + 60, BASE + 48, r=18, label=None)
        c.add("cancer_cell", x0 + 170, BASE + 66, r=15, label=None)
        c.text(cx, 300, "突破基底膜 → 浸润转移", size=12, bold=True, fill=C["red"])
    c.text(cx, 244, name, size=14, bold=True)
    if i < 3:
        c.arrow(x0 + 270, 330, x0 + 330, 330, kind="activation", width=2.8)
        c.text(x0 + 300, 306, ["吸烟损伤", "持续暴露", "突变累积 KRAS/TP53"][i], size=11.5, fill=C["gray"])

# 分子演变标注
c.add("group_box", 700, 600, w=1180, h=150, label=None, color=C["blue"], fill="#F4F9FE")
c.text(700, 570, "驱动基因与靶向治疗（示例）", size=15, bold=True)
genes = [("EGFR 突变", "EGFR-TKI：奥希/吉非替尼", C["teal"]),
         ("ALK 融合", "ALK 抑制剂：阿来替尼", C["purple"]),
         ("KRAS G12C", "Sotorasib / Adagrasib", C["orange"]),
         ("PD-L1 高表达", "免疫检查点抑制剂", C["red"])]
for i, (g, t, col) in enumerate(genes):
    bx = 150 + i * 290
    c.rect(bx, 640, 26, 26, fill=col)
    c.text(bx + 40, 660, g, size=13.5, bold=True, anchor="start")
    c.text(bx + 40, 692, t, size=12, fill=C["gray"], anchor="start")
c.text(700, 728, "非鳞 NSCLC 常规检测：EGFR / ALK / ROS1 / KRAS / PD-L1 (22C3)", size=12.5, fill=C["gray"], anchor="start")

# 筛查提示
c.add("group_box", 700, 800, w=1180, h=100, label=None, color=C["teal"], fill="#F3FAF9")
c.text(700, 836, "筛查与预防：高危人群（吸烟 ≥ 30 包年，年龄 ≥ 50 岁）年度低剂量螺旋 CT（LDCT）筛查",
       size=14, bold=True)
c.text(700, 872, "戒烟 10 年后肺癌风险下降约 50%；早期（I 期）术后 5 年生存率 > 70%", size=12.5, fill=C["gray"])

c.add("legend_row", 150, 950, items=[("#F9DCDE", "异型细胞"), (C["purple"], "增大细胞核"),
                                     (C["red"], "浸润"), (C["teal"], "正常纤毛上皮")], size=13.5)

c.save(os.path.join(OUT, "lung_cancer_pathogenesis.svg"))
c.export(os.path.join(OUT, "lung_cancer_pathogenesis"), formats=("png",), dpi=300)
print("lung done")
