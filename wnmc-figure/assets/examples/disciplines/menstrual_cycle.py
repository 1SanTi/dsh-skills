# -*- coding: utf-8 -*-
"""西医妇产：月经周期三联图（卵巢周期-激素-子宫内膜）"""
import os, sys
sys.path.insert(0, r"C:\Users\Administrator\.workbuddy\skills\medical-illustration\scripts")
from bio_graphics import Canvas, C

OUT = os.path.expanduser("~/.workbuddy/skills/medical-illustration/assets/examples/disciplines")
os.makedirs(OUT, exist_ok=True)

c = Canvas(1500, 1050)
c.title("月经周期：卵巢周期、激素波动与子宫内膜变化", size=29)

X0, X1 = 220, 1380
DAY = 28
def dx(d): return X0 + (d / DAY) * (X1 - X0)

# 日刻度（顶部）
for d in (1, 7, 14, 21, 28):
    c.text(dx(d), 118, str(d), size=13)
c.text(100, 118, "周期天数", size=13, fill=C["gray"], anchor="start")
c.line(X0, 128, X1, 128, color=C["gray"], width=1.2)

# 排卵日竖线
c.line(dx(14), 128, dx(14), 930, color=C["red"], width=1.6, dash="6 5")
c.text(dx(14), 958, "排卵（LH 峰后 ~36h）", size=13, bold=True, fill=C["red"])

# ---------- 第一条带：卵巢周期 ----------
c.text(100, 172, "卵巢周期", size=15, bold=True, anchor="start")
cy = 240
# 卵泡发育
for i, (d, r) in enumerate([(2, 14), (6, 22), (10, 32), (12.5, 40)]):
    x = dx(d)
    c.circle(x, cy, r, fill="#FDFDFD", stroke=C["blue"], width=2.0)
    c.circle(x + r * 0.18, cy - r * 0.1, r * 0.34, fill=C["blue_l"], stroke=C["blue"], width=1.4)
c.text(dx(7), cy - 62, "卵泡期（卵泡发育）", size=13, bold=True, fill=C["blue"])
# 排卵
c.add("oocyte", dx(14.5), cy + 40, r=17, label=None)
c.arrow(dx(14), cy - 8, dx(14.6), cy + 16, kind="activation", color=C["red"])
# 黄体
c.circle(dx(19), cy, 38, fill=C["yellow"], stroke=C["orange"], width=2.0)
c.text(dx(19), cy + 58, "黄体", size=13, bold=True)
c.circle(dx(25.5), cy, 20, fill=C["gray_l"], stroke=C["gray"], width=1.8)
c.text(dx(25.5), cy + 44, "白体（退化）", size=12, fill=C["gray"])
c.text(dx(21), cy - 62, "黄体期", size=13, bold=True, fill=C["orange"])
c.line(X0, cy + 78, X1, cy + 78, color=C["gray"], width=1.2)

# ---------- 第二条带：激素曲线 ----------
c.text(100, 372, "垂体/卵巢激素", size=15, bold=True, anchor="start")
HY0, HY1 = 420, 610
c.line(X0, HY1 + 10, X1, HY1 + 10, color=C["gray"], width=1.2)

def curve(points, color, width=2.6):
    d = "M " + " L ".join(f"{dx(p[0]):.1f} {HY1 + 10 - p[1]*(HY1-HY0):.1f}" for p in points)
    c.path(d, stroke=color, width=width)

curve([(1,0.10),(7,0.18),(10,0.12),(13,0.05),(16,0.10),(20,0.14),(24,0.10),(28,0.12)], C["purple"])          # FSH
curve([(1,0.08),(8,0.14),(11.5,0.72),(14,0.55),(17,0.10),(22,0.12),(26,0.10),(28,0.12)], C["red"])          # LH
curve([(1,0.12),(8,0.30),(11.5,0.92),(14,0.70),(17,0.42),(21,0.46),(24,0.28),(28,0.14)], C["teal"])         # E2
curve([(1,0.05),(10,0.06),(13,0.10),(16,0.30),(20,0.55),(23,0.60),(26,0.35),(28,0.16)], "#C98A1B")          # P

for lbl, col, y in [("FSH", C["purple"], 400), ("LH", C["red"], 400), ("E2 雌二醇", C["teal"], 400), ("P 孕酮", "#C98A1B", 400)]:
    pass
c.text(X0, 408, "相对水平", size=12, fill=C["gray"], anchor="start")
c.add("legend_row", 760, 395, items=[(C["purple"], "FSH"), (C["red"], "LH"),
                                     (C["teal"], "雌二醇 E2"), ("#C98A1B", "孕酮 P")], size=13)
c.text(dx(12), 560, "LH 峰", size=12.5, bold=True, fill=C["red"])
c.text(dx(12), 584, "触发排卵", size=11.5, fill=C["red"])
c.text(dx(21), 480, "黄体分泌 P + E2", size=12.5, fill="#C98A1B")

# ---------- 第三条带：子宫内膜 ----------
c.text(100, 680, "子宫内膜", size=15, bold=True, anchor="start")
BY0, BY1 = 720, 900
c.line(X0, BY1 + 8, X1, BY1 + 8, color=C["gray"], width=1.2)

# 基底层
c.rect(X0, BY1 - 18, X1 - X0, 18, fill="#F3C6B8")
c.text(X1 - 6, BY1 - 8, "基底层", size=12, anchor="end", fill=C["orange"])
# 功能层轮廓：月经期脱落 → 增生期增厚 → 分泌期最厚呈锯齿
seg = []
for d, h in [(1, 4), (4, 8), (5, 2), (8, 30), (11, 55), (14, 62), (17, 70),
             (20, 92), (23, 100), (25, 88), (27, 55), (28, 20)]:
    seg.append((dx(d), BY1 - 18 - h))
dstr = f"M {X0} {BY1-18} "
for (x, y) in seg:
    dstr += f"L {x:.0f} {y:.0f} "
dstr += f"L {X1} {BY1-18} Z"
c.path(dstr, fill="#F7A8A0", stroke=C["red"], width=2.0)

c.text(dx(3), BY1 + 32, "月经期 1-5天", size=13, bold=True, anchor="start")
c.text(dx(9.5), BY1 + 32, "增生期", size=13, bold=True, fill=C["teal"])
c.text(dx(21), BY1 + 32, "分泌期", size=13, bold=True, fill=C["orange"])
c.text(dx(21), 688, "腺体分泌 · 螺旋动脉迂曲 · 适合着床", size=12.5, fill=C["gray"])

c.add("legend_row", 220, 1005, items=[("#F7A8A0", "子宫内膜功能层"),
    ("#F3C6B8", "基底层"), (C["red"], "排卵日")], size=13)

c.save(os.path.join(OUT, "menstrual_cycle.svg"))
c.export(os.path.join(OUT, "menstrual_cycle"), formats=("png",), dpi=300)
print("menstrual done")
