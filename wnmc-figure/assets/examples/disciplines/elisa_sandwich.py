# -*- coding: utf-8 -*-
"""临床检验诊断：ELISA 双抗体夹心法四步流程"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1400, 950)
c.title("ELISA 双抗体夹心法：临床免疫检验原理", size=29)

def well(x, y, step, antigen=False, det=False, enzyme=False, color="#FDFDFD"):
    """孔板微孔剖面: x,y 中心; step 1-4"""
    W, D = 170, 120
    c.path(f"M {x-W/2} {y-40} L {x-W/2+14} {y+60} Q {x} {y+74} {x+W/2-14} {y+60} L {x+W/2} {y-40} Z",
           fill=color, stroke=C["ink"], width=2.0)
    # 固相包被抗体
    for i in range(4):
        c.path(f"M {x-60+i*36} {y+52} q 9 -26 18 0", stroke=C["blue"], width=3.4)
    if antigen:
        c.circle(x - 26, y + 10, 15, fill=C["red_l"], stroke=C["red"], width=2.0)
        c.circle(x + 22, y + 18, 15, fill=C["red_l"], stroke=C["red"], width=2.0)
    if det:
        for ax, ay in ([x - 26, y - 8], [x + 22, y]):
            c.line(ax - 20, ay - 6, ax, ay - 2, color=C["purple"], width=3.2)
            c.line(ax + 20, ay - 6, ax, ay - 2, color=C["purple"], width=3.2)
            c.line(ax, ay - 2, ax, ay + 16, color=C["purple"], width=3.2)
    if enzyme:
        c.circle(x - 26, y - 34, 11, fill=C["yellow"], stroke=C["orange"], width=1.8)
        c.circle(x + 22, y - 34, 11, fill=C["yellow"], stroke=C["orange"], width=1.8)
        c.text(x, y - 60, "HRP 酶标", size=11.5, bold=True)
    c.add("step_badge", x - 105, y - 55, n=step)

steps = [
    ("① 包被捕获抗体", dict()),
    ("② 加入样本（抗原）", dict(antigen=True)),
    ("③ 加检测抗体", dict(antigen=True, det=True)),
    ("④ 加底物显色", dict(antigen=True, det=True, enzyme=True, color="#F6C453")),
]
names = ["包被", "加样", "抗体结合", "显色"]
for i, (label, kw) in enumerate(steps):
    well(230 + i * 320, 330, i + 1, **kw)
    c.text(230 + i * 320, 450, label, size=14, bold=True)
    c.text(230 + i * 320, 480, ["洗涤 ×3", "37°C 孵育", "洗涤 ×3", "测 OD450"][i], size=12, fill=C["gray"])
    if i < 3:
        c.arrow(330 + i * 320, 330, 390 + i * 320, 330, kind="activation")

# 底部：定量曲线 + 检验流程
c.add("group_box", 410, 700, w=530, h=240, label=None, color=C["orange"], fill="#FEF8F4")
c.text(410, 598, "标准曲线定量", size=14, bold=True)
c.line(200, 790, 620, 790, color=C["ink"], width=1.8)
c.line(200, 790, 200, 650, color=C["ink"], width=1.8)
c.text(410, 815, "抗原浓度（对数）", size=12)
c.text(180, 660, "OD", size=12, anchor="start")
pts = [(220, 780), (270, 755), (320, 715), (370, 675), (420, 652), (470, 644), (540, 642)]
d = "M " + " L ".join(f"{x} {y}" for x, y in pts)
c.path(d, stroke=C["orange"], width=2.6)
c.circle(470, 644, 6, fill=C["red"])
c.text(492, 640, "样本", size=12, fill=C["red"], anchor="start")

c.add("group_box", 1020, 700, w=530, h=240, label=None, color=C["teal"], fill="#F3FAF9")
c.text(1020, 598, "临床检验流程", size=14, bold=True)
flow = ["采样（血/尿/拭子）", "离心与前处理", "上机检测", "质控审核 → 报告"]
for i, t in enumerate(flow):
    c.add("group_box", 1020, 665 + i * 52, w=280, h=38, label=None, color=C["gray"], fill="#FFFFFF")
    c.text(1020, 670 + i * 52, t, size=12.5, bold=True)
    if i < 3:
        c.arrow(1020, 686 + i * 52, 1020, 708 + i * 52, kind="activation", head_size=7)

c.add("legend_row", 200, 910, items=[(C["blue"], "固相抗体"), (C["red_l"], "待测抗原"),
                                     (C["purple"], "检测抗体"), (C["yellow"], "酶标记")], size=14)

c.save(os.path.join(OUT, "elisa_sandwich.svg"))
c.export(os.path.join(OUT, "elisa_sandwich"), formats=("png",), dpi=300)
print("elisa done")
