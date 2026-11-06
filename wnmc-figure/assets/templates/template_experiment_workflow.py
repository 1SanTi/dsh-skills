# -*- coding: utf-8 -*-
"""模板: 实验流程图 (动物模型 → 分组处理 → 取材 → 检测 → 分析)"""
import sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C, group_box

TITLE = "实验技术路线"
W, H = 1600, 700
c = Canvas(W, H, background="#FFFFFF")
c.title(TITLE, size=30)

ROW_Y = 330
STEPS = [
    ("mouse_lab",  {"size": 1.4, "label": "动物模型"}, None),
    ("syringe",    {"length": 130, "label": "造模/给药"}, None),
    ("tube_rack",  {"n": 4, "label": "取材"}, None),
    ("microscope", {"label": "病理检测"}, None),
    ("gel_lanes",  {"w": 170, "h": 120, "lanes": 3,
                    "bands": {0: [0.25, 0.6], 1: [0.4], 2: [0.25, 0.7, 0.9]},
                    "label": "Western blot"}, None),
]
n = len(STEPS)
gap = (W - 220) / n
xs = [110 + gap * (i + 0.5) for i in range(n)]
for i, (comp, kw, _) in enumerate(STEPS):
    c.add(comp, xs[i], ROW_Y, **kw)
    c.add("step_badge", xs[i] - 55, ROW_Y - 105, n=i + 1)
    if i < n - 1:
        c.arrow(xs[i] + gap * 0.36, ROW_Y, xs[i + 1] - gap * 0.36, ROW_Y, kind="activation")

# 分组标注
c.add("group_box", xs[0] - 10, ROW_Y, w=gap * 0.95, h=220, label="对照组", color=C["teal"])
c.add("group_box", xs[1] - 10, ROW_Y, w=gap * 0.95, h=220, label="实验组", color=C["red"])
c.export(r"OUTPUT_PATH", formats=("png", "pdf"), dpi=300)
print("done")
