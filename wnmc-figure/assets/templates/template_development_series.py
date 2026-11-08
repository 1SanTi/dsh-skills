# -*- coding: utf-8 -*-
"""模板: 组织学/胚胎学发育时序图 (阶段并排 + 步骤编号 + 时间轴)"""
import sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

TITLE = "早期胚胎发育"
STAGES = [  # (阶段名, 绘制函数名, 组件参数)
    ("受精", "oocyte", {}),
    ("卵裂", "blastocyst", {"r": 40}),
    ("桑椹胚", "cell_generic", {"w": 90, "h": 90}),
    ("胚泡", "blastocyst", {"r": 64}),
]
W, H = 1500, 700
c = Canvas(W, H, background="#FFFDF8")
c.title(TITLE, size=30)

n = len(STAGES)
gap = W / (n + 1)
Y = 400
for i, (name, comp, kw) in enumerate(STAGES):
    x = gap * (i + 1)
    c.add(comp, x, Y, **kw)
    c.add("step_badge", x - 40, Y - 140, n=i + 1)
    c.text(x, Y + 150, name, size=20, bold=True)
    if i < n - 1:
        c.arrow(x + gap / 2 - 40, Y, x + gap / 2 + 40, Y, kind="activation")

c.add("legend_row", 120, H - 50, items=[(C["yellow_l"], "卵细胞/卵裂球"),
                                        (C["blue_l"], "滋养层")], size=15)
c.export(r"OUTPUT_PATH", formats=("png", "pdf"), dpi=300)
print("done")
