# -*- coding: utf-8 -*-
"""生成 寄生虫与微生物组件总览图 (v1.1.0 新增组件质检样张)"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts")))
from bio_graphics import Canvas

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
c = Canvas(1560, 1180)
c.title("新增组件总览: 节肢动物 / 蠕虫 / 原虫 / 真菌与细菌", size=24)
items = [
    ("mite", 170, 260, {"label": "螨虫"}), ("tick", 400, 260, {"label": "硬蜱"}),
    ("flea", 630, 260, {"label": "跳蚤"}), ("mosquito", 850, 265, {"label": "蚊子"}),
    ("mouse_lab", 1120, 265, {"label": "实验小鼠", "size": 1.6}),
    ("roundworm", 170, 560, {"label": "蛔虫"}), ("tapeworm", 470, 560, {"label": "绦虫"}),
    ("schistosome", 810, 560, {"label": "血吸虫(雌雄合抱)"}),
    ("plasmodium_rbc", 1150, 545, {"label": "疟原虫环状体"}),
    ("giardia", 170, 880, {"label": "贾第鞭毛虫"}), ("amoeba", 380, 870, {"label": "阿米巴"}),
    ("yeast", 600, 860, {"label": "酵母菌"}), ("aspergillus", 810, 890, {"label": "曲霉"}),
    ("staphylococcus", 1050, 860, {"label": "葡萄球菌"}),
    ("streptococcus", 1280, 860, {"label": "链球菌"}),
]
for name, x, y, kw in items:
    c.add(name, x, y, **kw)
c.add("spirochete", 1440, 1100, label="螺旋体", w=110)
for f in c.export(os.path.join(OUT, "parasite_microbe_sheet"), formats=("png", "svg"), dpi=200):
    print(f)
