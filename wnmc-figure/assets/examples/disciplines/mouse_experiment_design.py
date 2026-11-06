# -*- coding: utf-8 -*-
"""分子机制研究：小鼠模型实验设计全流程（中心锚点版）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1500, 1000)
c.title("小鼠模型分子机制研究设计（基因 X 敲除示例）", size=28)

# ① 模型构建
c.text(110, 130, "① 模型构建", size=15, bold=True, anchor="start")
c.add("mouse_lab", 190, 260, size=1.5, label=None)
c.add("gene_cassette", 400, 250, w=200, label=None, promoter="loxP", gene="基因X")
c.text(300, 330, "条件性敲除 (flox) × 组织特异性 Cre", size=12, fill=C["gray"])

c.arrow(560, 260, 620, 260, kind="activation", label="繁育鉴定")

# ② 造模
c.add("group_box", 770, 265, w=280, h=170, label=None, color=C["orange"], fill="#FEF8F4")
c.text(770, 205, "② 疾病造模", size=15, bold=True)
c.add("syringe", 710, 285, length=105, angle=-18, label=None)
c.add("mouse_lab", 815, 300, size=0.85, label=None)
c.text(770, 335, "如：高脂饮食 / 手术 / 药物诱导", size=11.5, fill=C["gray"])

c.arrow(925, 265, 985, 265, kind="activation", label="分组")

# ③ 分组
c.add("group_box", 1230, 235, w=300, h=290, label=None, color=C["blue"], fill="#F4F9FE")
c.text(1230, 115, "③ 分组（随机盲法）", size=15, bold=True)
groups = [("WT + 生理盐水", C["gray_l"]), ("WT + 干预药", C["teal_l"]),
          ("KO + 生理盐水", C["orange_l"]), ("KO + 干预药", C["red_l"])]
for i, (g, col) in enumerate(groups):
    yy = 180 + i * 50
    c.rect(1105, yy - 13, 30, 26, fill=col, stroke=C["gray"], width=1.2)
    c.add("mouse_lab", 1165, yy, size=0.5, label=None)
    c.text(1205, yy + 5, g, size=12.5, anchor="start")

c.arrow(1230, 390, 1230, 450, kind="activation", label="取材")

# ④ 表型与分子检测
c.add("group_box", 1090, 640, w=460, h=340, label=None, color=C["teal"], fill="#F3FAF9")
c.text(1090, 500, "④ 表型与分子检测", size=15, bold=True)
c.add("organ_brain", 940, 590, size=0.65)
c.text(940, 655, "靶器官", size=12)
c.add("microtube", 1050, 590, h=60, label=None)
c.text(1050, 655, "血/组织", size=12)
c.add("gel_lanes", 1190, 590, w=130, h=110, lanes=4,
      bands={0: [0.3], 1: [0.3, 0.6], 2: [0.6], 3: [0.3, 0.6, 0.85]}, label=None)
c.text(1190, 680, "Western blot", size=12)
for i, t in enumerate(["qPCR / RNA-seq", "HE / 免疫组化染色", "行为学与功能评估"]):
    c.text(900, 720 + i * 34, "· " + t, size=12.5, anchor="start")

c.arrow(850, 640, 740, 640, kind="activation")

# ⑤ 机制归纳
c.add("group_box", 560, 640, w=350, h=340, label=None, color=C["purple"], fill="#F9F7FC")
c.text(560, 500, "⑤ 分子机制归纳", size=15, bold=True)
c.add("protein_blob", 470, 590, r=22, shape="hexagon", fill=C["purple_l"], label="蛋白A")
c.arrow(498, 590, 570, 590, kind="activation", label="磷酸化")
c.add("protein_blob", 615, 590, r=22, shape="square", fill=C["orange_l"], label="蛋白B")
c.arrow(615, 620, 615, 680, kind="activation")
c.add("nucleus", 615, 725, r=32, label="核", nucleolus=False)
c.text(560, 795, "基因X 缺失 → 通路抑制 → 表型改变", size=12.3, fill=C["gray"])

# 伦理与规范
c.add("group_box", 190, 640, w=330, h=340, label=None, color=C["gray"], fill="#FAFAFA")
c.text(190, 500, "伦理与规范", size=15, bold=True)
for i, t in enumerate(["动物伦理审查 (IACUC)", "3R 原则：替代/减少/优化",
                       "随机化 + 盲法 + 预设终点", "样本量：功效分析确定", "数据：原始数据留档"]):
    c.text(60, 570 + i * 44, "· " + t, size=12.8, anchor="start")

c.add("legend_row", 200, 955, items=[(C["blue_l"], "对照组"), (C["red_l"], "敲除/处理组"),
                                     (C["purple_l"], "机制通路")], size=14)

c.save(os.path.join(OUT, "mouse_experiment_design.svg"))
c.export(os.path.join(OUT, "mouse_experiment_design"), formats=("png",), dpi=300)
print("mouse done")
